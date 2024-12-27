from datetime import datetime
from threading import Thread, Event
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import os
from ..tools.base_tools import BaseTools
from ..logger import logger


@dataclass
class AuthConfig:
    username: str
    password: str
    remember: bool = True


class TokenRefresher(Thread):
    def __init__(self, auth_tools, refresh_interval=170):  # 5 minutes default - 30sec
        super().__init__(daemon=True)
        self.auth_tools = auth_tools
        self.refresh_interval = refresh_interval
        self.stop_event = Event()

    def run(self):
        while not self.stop_event.is_set():
            # Check if token needs refresh
            if self.auth_tools.needs_token_refresh():
                self.auth_tools.refresh_tokens()

            # Wait for next check
            self.stop_event.wait(self.refresh_interval)

    def stop(self):
        self.stop_event.set()


class AuthTools(BaseTools):
    def __init__(self, context):
        super().__init__(context)
        self._config: Optional[AuthConfig] = None
        self._session_data: Optional[Dict] = None
        self._auth_headers: Optional[Dict] = None
        self._token_refresher: Optional[TokenRefresher] = None
        self.logger = logger

    def validate(self) -> bool:
        """
        Validate authentication configuration and state
        Returns True if configuration is valid
        """
        if not self._config:
            return False

        try:
            # Check if we have valid credentials
            return bool(self._config.username and self._config.password)
        except Exception as e:
            self.logger.error(f"Auth validation failed: {e}")
            return False

    def configure(self,
                 username: str = None,
                 password: str = None,
                 remember: bool = True) -> 'AuthTools':
        """Configure authentication parameters"""
        username = username or os.getenv("NODE_USERNAME")
        password = password or os.getenv("NODE_PASSWORD")

        if not all([username, password]):
            raise ValueError("Missing required authentication parameters")

        self._config = AuthConfig(
            username=username,
            password=password,
            remember=remember
        )
        return self

    @staticmethod
    def _parse_login_response(response) -> Tuple[Dict, Dict]:
        """Extract session data and headers from login response"""
        response_data = response.json()
        cookies = response.cookies

        # Properly format all required cookies
        cookie_header = '; '.join([
            f"BAUMSID={cookies.get('BAUMSID')}",
            f"jwt_access={cookies.get('jwt_access')}",
            f"jwt_refresh={cookies.get('jwt_refresh')}"
        ])

        headers = {
            "Cookie": cookie_header,
            "Content-Type": "application/json"
        }

        session_data = {
            "sid": response_data.get("sid"),
            "login": response_data.get("data", {}).get("login"),
            "role": response_data.get("data", {}).get("role"),
            "jwt_access_expiration": response_data.get("jwtAccessExpirationDate"),
            "jwt_refresh_expiration": response_data.get("jwtRefreshExpirationDate")
        }

        return session_data, headers

    def login(self):
        """Perform login and start token refresh mechanism"""
        response = self._perform_login()

        # Start token refresher
        self._token_refresher = TokenRefresher(self)
        self._token_refresher.start()

        return response

    def _perform_login(self):
        if not self._config:
            raise ValueError("Authentication not configured. Call configure() first.")

        client = self._context.client
        login_data = {
            "login": self._config.username,
            "password": self._config.password,
            "remember": self._config.remember
        }

        response = client.post("/login", json=login_data)

        # Detailed logging of response
        self.logger.info("=== Login Response Details ===")
        self.logger.info(f"Status Code: {response.status_code}")
        self.logger.info("Headers:")
        for header, value in response.headers.items():
            self.logger.info(f"{header}: {value}")
        self.logger.info("Response Body:")
        self.logger.info(response.json())
        self.logger.info("Cookies:")
        self.logger.info(dict(response.cookies))
        self.logger.info("========================")

        if response.status_code != 200:
            raise ConnectionError(f"Login failed: {response.text}")
        self._session_data, self._auth_headers = self._parse_login_response(response)
        return response

    def needs_token_refresh(self) -> bool:
        """Check if token needs refresh based on expiration time"""
        if not self._session_data:
            return False

        current_time = int(datetime.now().timestamp())
        access_expiration = self._session_data.get('jwt_access_expiration', 0)

        # Refresh if less than 5 minutes until expiration
        return (access_expiration - current_time) < 170

    def refresh_tokens(self):
        """Refresh session tokens"""
        if not self._auth_headers:
            return

        client = self._context.client

        # Log refresh request details
        self.logger.info("=== Token Refresh Request Details ===")
        self.logger.info("Endpoint: /refresh_tokens")
        self.logger.info("Method: GET")
        self.logger.info("Request Headers:")
        for header, value in self._auth_headers.items():
            self.logger.info(f"{header}: {value}")
        self.logger.info("Current Session Data:")
        self.logger.info(self._session_data)
        self.logger.info("================================")

        response = client.get("/refresh_tokens", headers=self._auth_headers, cookies=self._cookies)

        # Log refresh response details
        self.logger.info("=== Token Refresh Response Details ===")
        self.logger.info(f"Status Code: {response.status_code}")
        self.logger.info("Response Headers:")
        for header, value in response.headers.items():
            self.logger.info(f"{header}: {value}")
        self.logger.info("Response Body:")
        self.logger.info(response.json())
        self.logger.info("Response Cookies:")
        self.logger.info(dict(response.cookies))
        self.logger.info("=================================")

        if response.status_code == 200:
            self._session_data, self._auth_headers = self._parse_login_response(response)
            self.logger.info("Session tokens refreshed successfully")
        else:
            self.logger.error(f"Failed to refresh tokens: {response.status_code}")

    def logout(self) -> None:
        """Perform logout"""
        if self._token_refresher:
            self._token_refresher.stop()
            self._token_refresher = None

        if not all([self._session_data, self._auth_headers]):
            self.logger.warning("No active session found for logout")
            return

        client = self._context.client
        response = client.post("/logout", json=self._session_data, headers=self._auth_headers)
        if response.status_code not in (200, 204):
            self.logger.warning(f"Logout returned unexpected status code: {response.status_code}")


    # def login(self) -> Dict[str, any]:
    #     """Perform login"""
    #     if not self._config:
    #         raise ValueError("Authentication not configured. Call configure() first.")
    #
    #     client = self._context.client
    #     login_data = {
    #         "login": self._config.username,
    #         "password": self._config.password,
    #         "remember": self._config.remember
    #     }
    #
    #     response = client.post("/login", json=login_data)
    #     self._session_data = response.json()
    #     if response.status_code != 200:
    #         raise ConnectionError(f"Login failed: {response.text}")
    #     return response
