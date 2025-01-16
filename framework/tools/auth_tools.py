import os
import time
from threading import Thread, Event
from typing import Dict, Optional, Tuple
from ..configs.auth_config import AuthConfig
from ..tools.base_tools import BaseTools
from framework.core.cookie_manager import CookieManager
from framework.core.logger import logger



class TokenRefresher(Thread):
    def __init__(self, auth_tools, refresh_interval=170):  # 3 minutes default - 10sec
        super().__init__(daemon=True)
        self.auth_tools = auth_tools
        self.refresh_interval = refresh_interval
        self.stop_event = Event()

    def run(self):
        # Выполняем цикл пока не будет вызван stop()
        while not self.stop_event.is_set():

            # Проверяем нужно ли обновить токен
            if self.auth_tools.needs_token_refresh():
                self.auth_tools.refresh_tokens()

            # Ждём следующей проверки
            self.stop_event.wait(self.refresh_interval)

    def stop(self):
        self.stop_event.set()


class AuthTools(BaseTools):
    def __init__(self, context):
        super().__init__(context)
        self._config: Optional[AuthConfig] = None
        self._user_agent: Optional[str] = None
        self._session_data: Optional[Dict] = None
        self._auth_headers: Optional[Dict] = None
        self.cookie_manager = CookieManager()
        self._token_refresher: Optional[TokenRefresher] = None
        self._last_refresh_time: Optional[float] = None
        self._skip_validation: bool = False
        self.logger = logger


    def validate(self) -> bool:
        """
        Validate authentication configuration and state
        Returns True if configuration is valid
        """
        if not self._config:
            return False

        if hasattr(self._config, '_skip_validation'):
            return True

        try:
            # Check if we have valid credentials
            return bool(self._config and self._config.username and self._config.password)
        except Exception as e:
            self.logger.error(f"Auth validation failed: {e}")
            return False

    def configure(self, **kwargs) -> 'AuthTools':
        """Configure authentication parameters"""
        if kwargs:
            self._config = AuthConfig(**kwargs)
            self._skip_validation = True
        else:
            username = os.getenv('NODE_USERNAME')
            password = os.getenv('NODE_PASSWORD')

            if username is None:
                raise ValueError("NODE_USERNAME not found in environment variables")
            if password is None:
                raise ValueError("NODE_PASSWORD not found in environment variables")

            self._config = AuthConfig(
                username=username,
                password=password,
                remember=True
            )
            self._skip_validation = False
        return self


    # def configure(self, **kwargs) -> 'AuthTools':
    #     """
    #     Configure authentication parameters
    #
    #     Allows any parameters to be passed or omitted for testing different request bodies
    #     """
    #     if not kwargs:
    #         # Use default values for empty configure() call
    #         kwargs = {
    #             'username': 'admin',
    #             'password': '123456',
    #             'remember': True
    #         }
    #     self._config = AuthConfig(**kwargs)
    #     return self


    # def configure(self,
    #               username: str = None,
    #               password: str = None,
    #               remember: bool = True,
    #               skip_validation: bool = False) -> 'AuthTools':
    #     """
    #     Configure authentication parameters
    #
    #     Args:
    #         username: Login for authentication
    #         password: Password for authentication
    #         remember: Remember session flag
    #         skip_validation: Skip parameters validation for negative testing
    #     """
    #     # Явно переданные значения имеют приоритет
    #     # None тоже считается явно переданным значением
    #     self._username = username if username is not None else os.getenv("NODE_USERNAME")
    #     self._password = password if password is not None else os.getenv("NODE_PASSWORD")
    #
    #     # Валидация только для позитивных сценариев
    #     if not skip_validation and not all([self._username, self._password]):
    #         raise ValueError("Missing required authentication parameters")
    #
    #     self._config = AuthConfig(
    #         username=self._username,
    #         password=self._password,
    #         remember=remember
    #     )
    #     return self


    # def configure(self,
    #              username: str = None,
    #              password: str = None,
    #              remember: bool = True) -> 'AuthTools':
    #     """Configure authentication parameters"""
    #     username = username or os.getenv("NODE_USERNAME")
    #     password = password or os.getenv("NODE_PASSWORD")
    #
    #     if not all([username, password]):
    #         raise ValueError("Missing required authentication parameters")
    #
    #     self._config = AuthConfig(
    #         username=username,
    #         password=password,
    #         remember=remember
    #     )
    #     return self

    def _parse_auth_response(self, response) -> Tuple[Dict, Dict, Dict]:
        """Управляет парсерами для поддержания сессии"""
        response_data = response.json()

        if "data" in response_data:
            session_data = self._parse_login_data(response_data)
        else:
            session_data = self._parse_refresh_data(response_data)

        cookies = self.cookie_manager.parse_set_cookie_header(
            response.headers.get_list('Set-Cookie')
        )

        headers = {
            "Content-Type": "application/json",
            "Cookie": self.cookie_manager.format_cookie_header(cookies)
        }

        return session_data, headers, cookies

    def _parse_login_data(self, response_data) -> Dict:
        return {
            "sid": response_data.get("sid"),
            "login": response_data.get("data", {}).get("login"),
            "role": response_data.get("data", {}).get("role"),
            "remember": response_data.get("data", {}).get("remember"),
            "jwt_access_expiration": response_data.get("jwtAccessExpirationDate"),
            "jwt_refresh_expiration": response_data.get("jwtRefreshExpirationDate"),
            "expired": response_data.get("expired")
        }

    def _parse_refresh_data(self, response_data) -> Dict:
        session_data = self._session_data.copy()
        session_data.update({
            "jwt_access_expiration": response_data.get("jwtAccessExpirationDate"),
            "jwt_refresh_expiration": response_data.get("jwtRefreshExpirationDate")
        })
        return session_data

    def login(self):
        """Perform login and start token refresh mechanism"""
        if not self._skip_validation and not self.validate():
            raise ValueError("Invalid authentication configuration")
        response = self._perform_login()

        # Update cookie manager with login response
        self.cookie_manager.update_from_response(response)

        # Start token refresher
        self._token_refresher = TokenRefresher(self)
        self._token_refresher.start()

        return response


    def _perform_login(self):
        if not self._config:
            raise ValueError("Authentication not configured")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self._user_agent = headers['User-Agent']

        response = self._context.client.post(
            "/login",
            json=self._config.to_request(),
            headers=headers
        )

        if response.status_code != 200:
            raise ConnectionError(f"Login failed: {response.text}") # Исправить - это не правильная ошибка

        self._session_data, self._auth_headers, self._cookies = self._parse_auth_response(response)
        self._last_refresh_time = time.time()
        return response


    # def _perform_login(self):
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
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    #     }
    #     self._user_agent = headers['User-Agent']
    #
    #     response = client.post("/login", json=login_data, headers=headers)
    #
    #     # Detailed logging of response
    #     # self.logger.info("=== Login Response Details ===")
    #     # self.logger.info(f"Status Code: {response.status_code}")
    #     # self.logger.info("Headers:")
    #     # for header, value in response.headers.items():
    #     #     self.logger.info(f"{header}: {value}")
    #     # self.logger.info("Response Body:")
    #     # self.logger.info(response.json())
    #     # self.logger.info("Cookies:")
    #     # self.logger.info(dict(response.cookies))
    #     # self.logger.info("========================")
    #
    #     if response.status_code != 200:
    #         raise ConnectionError(f"Login failed: {response.text}")
    #     self._session_data, self._auth_headers, self._cookies = self._parse_auth_response(response)
    #     # logger.info(f"Session data after login: {self._session_data}")
    #     self._last_refresh_time = time.time()  # Set initial refresh time
    #     return response


    def needs_token_refresh(self) -> bool:
        """Check if token needs refresh based on expiration time"""
        if not self._session_data:
            return False

        # Если время последнего обновления не установлено (первый вход в систему), установит его сейчас
        if self._last_refresh_time is None:
            self._last_refresh_time = time.time()
            return False

        current_time = time.time()
        time_since_last_refresh = current_time - self._last_refresh_time

        # Обновляем, если с момента последнего обновления/входа прошло более 170 секунд.
        return time_since_last_refresh >= 170


    def refresh_tokens(self):
        """
        Refreshes authentication tokens using the refresh token endpoint.
        Updates session data, headers and cookies with new values.
        """
        if not self._user_agent:
            raise ValueError("User-Agent not set. Login first.")

        params = {
            'user-agent': self._user_agent,
            'tabId': -1
        }

        try:
            response = self._context.client.get(
                "/refresh_tokens",
                headers=self._auth_headers,
                params=params
            )

            if response.status_code == 200:
                # Обновляем данные сессии из ответа
                self._session_data, self._auth_headers, cookies = self._parse_auth_response(response)
                self.cookie_manager.update_from_response(response)
                self._last_refresh_time = time.time()

                # Verify session data is properly updated
                # logger.info(f"Session data after refresh: {self._session_data}")
                return response
            else:
                logger.error(f"Token refresh failed with status code: {response.status_code}")
                raise Exception(f"Token refresh failed: {response.text}")

        except Exception as e:
            logger.error(f"Error during token refresh: {str(e)}")
            raise


    def logout(self) -> None:
        """Perform logout with current cookies"""
        # logger.info(f"Session data before logout: {self._session_data}")
        if self._token_refresher:
            self._token_refresher.stop()
            self._token_refresher = None

        # Получаем текущие cookie от cookie менеджера
        current_cookies = self.cookie_manager.get_current_cookies()
        if not current_cookies:
            self.logger.warning("No active session found for logout")
            return

        # Подготавливаем данные для logout
        logout_data = {"sid": self._session_data.get("sid"),
                       "login": self._session_data.get("login"),
                       "role": self._session_data.get("role")} if self._session_data else {}
        # self.logger.info(f"LOGOUT DATA__________\n{logout_data}")
        client = self._context.client
        response = client.post(
            "/logout",
            json=logout_data,
            headers=self._auth_headers,
            cookies=current_cookies
        )

        if response.status_code not in (200, 204):
            self.logger.warning(f"Logout returned unexpected status code: {response.status_code}")

        # Очищаем все данные сессии
        self._session_data = None
        self._auth_headers = None
        self.cookie_manager = CookieManager()
        self._last_refresh_time = None

        return response
