import httpx
from framework.api.core.logger import logger
import time
import json
from urllib.parse import urlencode
from framework.api.core.cookie_manager import CookieManager


""" Этот модуль предоставляет функциональность для выполнения HTTP-запросов (GET, POST, PUT, DELETE)
    к API серверу и обработки ответов. Он включает в себя механизмы для логирования информации о запросах
    и ответах, а также преобразования запросов в формат cURL для удобства отладки.

Основные функции:
    - `handle_http`: Выполняет HTTP-запросы и обрабатывает ошибки.
    - `request_to_curl`: Преобразует параметры запроса в строку cURL. (используется для отладки и отчётности)
    - Класс `APIClient`: Реализует методы для выполнения CRUD операций.
"""


def request_to_curl(method, url, headers=None, params=None, json_data=None, cookies=None):
    """
    Преобразует параметры HTTP-запроса в строку cURL.

    :param method: (str): HTTP метод (GET, POST, PUT, DELETE).
    :param url: (str): URL для запроса.
    :param headers: (dict, optional): Заголовки для запроса.
    :param params: (dict, optional): Параметры для GET запросов.
    :param json_data: (dict, optional): JSON данные для POST/PUT запросов.
    :param cookies: (dict, optional): Куки для передачи с запросом.
    :return: str: Строка cURL для данного запроса.
    """
    curl_command = ['curl']

    if method != 'GET':
        curl_command.extend(['-X', method])

    if headers:
        for key, value in headers.items():
            curl_command.extend(['-H', f"'{key}: {value}'"])

    if cookies:
        cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])
        curl_command.extend(['-H', f"'Cookie: {cookie_string}'"])

    if json_data:
        curl_command.extend(['-d', f"'{json.dumps(json_data)}'"])
        if not headers or 'Content-Type' not in headers:
            curl_command.extend(['-H', "'Content-Type: application/json'"])

    final_url = url
    if params:
        param_string = urlencode(params)
        final_url = f"{url}?{param_string}"

    curl_command.append(f"'{final_url}'")

    return ' '.join(curl_command)


class APIClient:

    def __init__(self, base_url):
        """
        Инициализация API клиента.

        :param base_url: (str): Базовый URL для API.
        """

        self.base_url = base_url
        self.http_client = httpx.Client(timeout=40.0)
        self.cookie_manager = CookieManager()

    def __del__(self):
        self.http_client.close()

    def handle_http(self, method, url, json=None, headers=None, params=None, cookies=None):
        start_time = time.time()

        # Merge default cookies from cookie_manager with custom cookies
        request_cookies = {
            **self.cookie_manager.get_current_cookies(),
            **(cookies or {})
        }

        curl_command = request_to_curl(method, url, headers, params, json, request_cookies)
        logger.info(f"Equivalent CURL command:\n{curl_command}")

        try:
            # if cookies:
            #     self.http_client.cookies.update(cookies)

            if method == 'GET':
                response = self.http_client.get(url, headers=headers, params=params, cookies=request_cookies)
            elif method == 'POST':
                response = self.http_client.post(url, json=json, headers=headers, cookies=request_cookies)
            elif method == 'PUT':
                response = self.http_client.put(url, json=json, headers=headers, cookies=request_cookies)
            elif method == 'DELETE':
                response = self.http_client.delete(url, headers=headers, cookies=request_cookies)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Update cookies from response
            self.cookie_manager.update_from_response(response)

            elapsed_time = time.time() - start_time
            logger.info(f"{method} {url} completed with status {response.status_code} in {elapsed_time:.2f} seconds")
            return response

        except httpx.HTTPStatusError as exc:
            logger.error(f"{method} request failed: {exc.response.status_code} - {exc.response.text}", exc_info=exc)
            raise

    def get(self, endpoint, headers=None, params=None, cookies=None):
        """
        Выполняет GET запрос к указанному эндпоинту.

        :param endpoint: (str): Эндпоинт для запроса.
        :param headers: (dict, optional): Заголовки для запроса.
        :param cookies: (dict or None): Кастомные куки для запроса.
        :param cookies:
        :return: httpx.Response: Ответ от сервера.
        """

        url = f"{self.base_url}{endpoint}"
        # cookies = self.cookie_manager.get_current_cookies()
        response = self.handle_http("GET", url, headers=headers, params=params, cookies=cookies)
        self.log_response(response)
        # logger.info(f"GET RESPONSE:  {response.json()}")
        return response


    def post(self, endpoint, json=None, headers=None, cookies=None):
        """
        Выполняет POST запрос к указанному эндпоинту.

        :param endpoint: (str): Эндпоинт для запроса.
        :param json: (dict or list): Данные JSON для отправки в теле запроса.
        :param headers: (dict or None): Заголовки для запроса.
        :param cookies: (dict or None): Кастомные куки для запроса.
        :return: httpx.Response: Ответ от сервера.
        """
        url = f"{self.base_url}{endpoint}"

        # self.log_request("POST", url, headers, None, json, request_cookies)
        response = self.handle_http("POST", url, json=json, headers=headers, cookies=cookies)

        # Update cookie_manager with new cookies from response
        self.cookie_manager.update_from_response(response)
        self.log_response(response)

        return response


    def put(self, endpoint, json=None, headers=None, cookies=None):
        """
        Выполняет PUT запрос к указанному эндпоинту.

        :param endpoint: (str): Эндпоинт для запроса.
        :param json: (dict or list): Данные JSON для отправки в теле запроса.
        :param headers: (dict or None): Заголовки для запроса.
        :param cookies: (dict or None): Кастомные куки для запроса.
        :return: httpx.Response: Ответ от сервера.
        """

        url = f"{self.base_url}{endpoint}"
        response = self.handle_http("PUT", url, json=json, headers=headers, cookies=cookies)
        self.log_response(response)
        return response


    def delete(self, endpoint, headers=None, cookies=None):
        """
        Выполняет DELETE запрос к указанному эндпоинту.

        :param endpoint: (str): Эндпоинт для запроса.
        :param headers: (dict or None): Заголовки для запроса.
        :param cookies: (dict or None): Кастомные куки для запроса.
        :return: httpx.Response: Ответ от сервера.
        """

        url = f"{self.base_url}{endpoint}"
        response = self.handle_http("DELETE", url, headers=headers, cookies=cookies)
        self.log_response(response)
        return response


    @staticmethod
    def log_response(response):
        """
        Логирует информацию о ответе от сервера.

        :param response: (httpx.Response): Ответ от сервера.
        :return: None
        """

        if response.status_code not in (200, 201, 204):
            logger.error(f"Error response. Status code: {response.status_code} - Body: {response.text}")


    @staticmethod
    def log_request(method, url, headers=None, params=None, json=None, cookies=None):
        """
        Логирует информацию о выполненном запросе.

        :param method: (str): Метод HTTP-запроса.
        :param url: (str): URL запроса.
        :param headers: (dict or None): Заголовки запроса.
        :param params: (dict or None): Параметры запроса.
        :param json: (dict or None): Тело запроса в формате JSON.
        :return: None
        """

        logger.info("=== Request Details ===")
        logger.info(f"{method} Request to {url}")
        if headers:
            logger.info("Headers:")
            for header, value in headers.items():
                logger.info(f"  {header}: {value}")

        if cookies:
            logger.info("Cookies:")
            for cookie, value in cookies.items():
                logger.info(f"  {cookie}: {value}")

        if params:
            logger.info(f"Params: {params}")

        if json:
            logger.info(f"Body: {json}")

        logger.info("=====================")