import os
import time
from httpx import Response
from threading import Thread, Event
from typing import Dict, Optional, Tuple
from ..models.auth_models import AuthConfig
from ..tools.base_tools import BaseTools
from framework.core.cookie_manager import CookieManager
from framework.core.logger import logger
from framework.resources.auth.auth_exceptions import AuthenticationError



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
        self._manual_auth = False  # Flag for manual authentication

    def authentication(self):
        """High-level authentication handler"""
        if self._manual_auth:
            return self.get_current_session()

        if not self.is_authenticated():
            self._configure_credentials()
            return self.login().json()
        return self.get_current_session()

    def force_authentication(self):
        """Принудительный login независимо от текущего состояния(очистка)"""
        self.logout_and_clean()  # Clear existing session
        return self.login()

    def _configure_credentials(self):
        """Обрабатывает credentials переданные в ручном режиме в тесте"""
        if hasattr(self._context.request, 'param') and 'credentials' in self._context.request.param:
            self.configure(**self._context.request.param['credentials'])
        else:
            self.configure()

    def login(self):
        """Public login interface"""
        self._manual_auth = True
        self._validate_login_prerequisites()
        response = self._perform_login()
        self._setup_session(response)
        return response

    def _validate_login_prerequisites(self):
        if not self._skip_validation and not self.validate():
            raise ValueError("Invalid authentication configuration")
        if not self._config:
            raise ValueError("Authentication not configured")

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

    def _perform_login(self):
        """Core login implementation"""
        headers = self._prepare_headers()
        response = self._send_login_request(headers)
        self._validate_response(response)
        return response

    def _prepare_headers(self):
        """Prepare request"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self._user_agent = headers['User-Agent']
        return headers

    def _send_login_request(self, headers):
        """Выполняет POST запрос"""
        return self._context.client.post(
            "/login",
            json=self._config.to_request(),
            headers=headers
        )

    # def _validate_response(self, response):
    #     """Валидация ответа сервера на login запрос"""
    #     if response.status_code != 200:
    #         raise AuthenticationError(f"Login failed: {response.text}")

    @staticmethod
    def _validate_response(response):
        """Validate login response and raise appropriate errors"""
        if response.status_code == 200:
            return

        error_mapping = {
            401: "Invalid credentials",
            403: "Account locked",
            404: "User not found",
            429: "Too many login attempts",
            500: "Internal server error during authentication"
        }

        error_message = error_mapping.get(
            response.status_code,
            f"Login failed with status {response.status_code}"
        )

        raise AuthenticationError(
            message=error_message,
            status_code=response.status_code,
            response_data=response.json() if response.text else {}
        )

    def _setup_session(self, response):
        """Setup session after successful login"""
        self.cookie_manager.update_from_response(response)
        self._session_data, self._auth_headers, self._cookies = self._parse_auth_response(response)
        logger.info(f"Session data after login: {self._session_data}")
        self._last_refresh_time = time.time()
        self._start_token_refresher()

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

    @staticmethod
    def _parse_login_data(response_data) -> Dict:
        return {
            "sid": response_data["sid"],
            "data": {
                "login": response_data["data"]["login"],
                "role": response_data["data"]["role"],
                "remember": response_data["data"]["remember"]
            },
            "jwtAccessExpirationDate": response_data["jwtAccessExpirationDate"],
            "jwtRefreshExpirationDate": response_data["jwtRefreshExpirationDate"]
        }

    def _parse_refresh_data(self, response_data) -> Dict:
        session_data = self._session_data.copy()
        session_data.update({
            "jwtAccessExpirationDate": response_data["jwtAccessExpirationDate"],
            "jwtRefreshExpirationDate": response_data["jwtRefreshExpirationDate"]
        })
        return session_data

    def _start_token_refresher(self):
        """Запускаем token_refresher в отдельном потоке"""
        self._token_refresher = TokenRefresher(self)
        self._token_refresher.start()

    def needs_token_refresh(self) -> bool:
        """Check if token needs refresh based on expiration time
            Проверяем наличие session_data
            Устанавливаем время первого входа если его нет
            Вычисляем время прошедшее с последнего обновления
            Возвращаем True если прошло больше 170 секунд (3 минуты минус 10 секунд)
            Проверка выполняется в цикле с интервалом, указанным в refresh_interval
        """
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

    def get_current_session(self) -> Dict:
        """Get current session information"""
        return self._session_data

    def is_authenticated(self) -> bool:
        """Check if client is authenticated and has active token refresher"""
        return bool(self._token_refresher)

    # def logout(self) -> None:
    #     """Perform logout with current cookies"""
    #     # logger.info(f"Session data before logout: {self._session_data}")
    #     if self._token_refresher:
    #         self._token_refresher.stop()
    #         self._token_refresher = None
    #
    #     # Получаем текущие cookie от cookie менеджера
    #     current_cookies = self.cookie_manager.get_current_cookies()
    #     if not current_cookies:
    #         self.logger.warning("No active session found for logout")
    #         return
    #
    #     # Подготавливаем данные для logout
    #     logout_data = {
    #         "sid": self._session_data["sid"],
    #         "login": self._session_data["data"]["login"],
    #         "role": self._session_data["data"]["role"]
    #     } if self._session_data else {}
    #
    #     # self.logger.info(f"LOGOUT DATA__________\n{logout_data}")
    #     client = self._context.client
    #     response = client.post(
    #         "/logout",
    #         json=logout_data,
    #         headers=self._auth_headers,
    #         cookies=current_cookies
    #     )
    #
    #     if response.status_code not in (200, 204):
    #         self.logger.warning(f"Logout returned unexpected status code: {response.status_code}")
    #
    #     return response

    def logout(self) -> Dict:
        """Perform logout and return status"""
        if not self._prepare_logout():
            status = {
                "success": False,
                "message": "Logout preparation failed - no active session",
                "action_completed": "none"
            }
            self.logger.info(f"Logout status: {status}")
            return status

        response = self._send_logout_request()
        self._handle_logout_response(response)

        status = {
            "success": response.status_code in (200, 204),
            "message": "Logout successful" if response.status_code in (200, 204) else "Logout failed",
            "status_code": response.status_code,
            "action_completed": "full_logout"
        }
        self.logger.info(f"Logout status: {status}")
        return status

    def _prepare_logout(self) -> bool:
        self._stop_token_refresher()
        return self._validate_logout_prerequisites()

    def _stop_token_refresher(self):
        if self._token_refresher:
            self._token_refresher.stop()
            self._token_refresher = None

    def _validate_logout_prerequisites(self) -> bool:
        current_cookies = self.cookie_manager.get_current_cookies()
        if not current_cookies:
            self.logger.warning("No active session found for logout")
            return False
        return True

    def _send_logout_request(self):
        logout_data = self._prepare_logout_data()
        return self._context.client.post(
            "/logout",
            json=logout_data,
            headers=self._auth_headers,
            cookies=self.cookie_manager.get_current_cookies()
        )

    def _prepare_logout_data(self) -> Dict:
        if not self._session_data:
            return {}
        return {
            "sid": self._session_data["sid"],
            "login": self._session_data["data"]["login"],
            "role": self._session_data["data"]["role"]
        }

    def _handle_logout_response(self, response):
        if response.status_code not in (200, 204):
            self.logger.warning(f"Logout returned unexpected status code: {response.status_code}")

    def logout_and_clean(self) -> Optional[Response]:
        """Perform logout with clean"""
        if not self._prepare_logout():
            return None

        response = self._send_logout_request()
        self._handle_logout_response(response)
        return response

    def clean_session_data(self):
        # Очищаем все данные сессии
        self._session_data = None
        self._auth_headers = None
        self._last_refresh_time = None
        self.cookie_manager = CookieManager()



    # def authentication(self):
    #     """Handles authentication with custom or default credentials"""
    #     if not self.is_authenticated():
    #         if hasattr(self._context.request, 'param') and 'credentials' in self._context.request.param:
    #             # Используем переданные credentials для конфигурации
    #             self.configure(**self._context.request.param['credentials'])
    #         else:
    #             # Используем дефолтные значения
    #             self.configure()
    #         response = self.login().json()
    #     else:
    #         response = self.get_current_session()
    #     return response

    # def login(self):
    #     """Perform login and start token refresh mechanism"""
    #     if not self._skip_validation and not self.validate():
    #         raise ValueError("Invalid authentication configuration")
    #     response = self._perform_login()
    #
    #     # Update cookie manager with login response
    #     self.cookie_manager.update_from_response(response)
    #
    #     # Start token refresher
    #     self._token_refresher = TokenRefresher(self)
    #     self._token_refresher.start()
    #
    #     return response


    # def _perform_login(self):
    #     if not self._config:
    #         raise ValueError("Authentication not configured")
    #
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    #     }
    #     self._user_agent = headers['User-Agent']
    #
    #     response = self._context.client.post(
    #         "/login",
    #         json=self._config.to_request(),
    #         headers=headers
    #     )
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
    #         raise ConnectionError(f"Login failed: {response.text}") # Исправить - это не правильная ошибка
    #
    #     self._session_data, self._auth_headers, self._cookies = self._parse_auth_response(response)
    #     logger.info(f"Session data after login: {self._session_data}")
    #     self._last_refresh_time = time.time()   # Set initial refresh time
    #     return response
