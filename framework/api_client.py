import httpx
import allure
from framework.logger import logger
import time
import json
from urllib.parse import urlencode


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


def handle_http(method, url, json=None, headers=None, params=None, cookies=None, timeout=40.0):
    """
    Общая функция для выполнения HTTP-запросов и обработки ошибок.

    :param method: (str): HTTP метод (GET, POST, PUT, DELETE).
    :param url: (str): URL для запроса.
    :param json: (dict, optional): JSON данные для POST/PUT запросов.
    :param headers: (dict, optional): Заголовки для запроса.
    :param params: (dict, optional): Параметры для GET запросов.
    :param cookies: (dict, optional): Куки для передачи с запросом.
    :param timeout: (float): Тайм-аут для HTTP клиента.
    :return: httpx.Response: Ответ от сервера.
    :raises httpx.HTTPStatusError: Если статус ответа указывает на ошибку.
            Exception: Для других неожиданных ошибок.
    """
    start_time = time.time()  # Время начала запроса

    # Вывод в логи всех запросов в виде CURL
    curl_command = request_to_curl(method, url, headers, params, json, cookies)
    logger.info(f"Equivalent CURL command:\n{curl_command}")

    try:
        with httpx.Client(timeout=timeout, cookies=cookies) as client:
            if method == 'GET':
                response = client.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = client.post(url, json=json, headers=headers)
            elif method == 'PUT':
                response = client.put(url, json=json, headers=headers)
            elif method == 'DELETE':
                response = client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            elapsed_time = time.time() - start_time  # Время завершения запроса
            logger.info(f"{method} {url} completed with status {response.status_code} in {elapsed_time:.2f} seconds")
            return response

    except httpx.HTTPStatusError as exc:
        logger.error(f"{method} request failed: {exc.response.status_code} - {exc.response.text}", exc_info=exc)
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in {method}: {str(exc)}")
        raise


class APIClient:

    def __init__(self, base_url):
        """
        Инициализация API клиента.

        :param base_url: (str): Базовый URL для API.
        """

        self.base_url = base_url
        self.cookies = {}  # Хранение куки


    def parse_cookies(self, set_cookie_header):
        """
        Парсит заголовок Set-Cookie и возвращает словарь с куками.

        :param set_cookie_header: (str): Заголовок Set-Cookie из ответа.
        :return: dict: Словарь с куками.
        """

        cookies = {}
        for cookie in set_cookie_header.split(','):
            key_value = cookie.split(';')[0].strip().split('=')
            if len(key_value) == 2:
                cookies[key_value[0]] = key_value[1]
        return cookies


    @allure.step("Sending GET request to {endpoint}")
    def get(self, endpoint, headers=None, params=None):
        """
        Выполняет GET запрос к указанному эндпоинту.

        :param endpoint: (str): Эндпоинт для запроса.
        :param headers: (dict, optional): Заголовки для запроса.
        :param params: (dict, optional): Параметры запроса.
        :return: httpx.Response: Ответ от сервера.
        """

        url = f"{self.base_url}{endpoint}"
        response = handle_http("GET", url, headers=headers, params=params, cookies=self.cookies)
        self.log_response(response)
        # logger.info(f"GET RESPONSE:  {response.json()}")
        return response


    @allure.step("Sending POST request to {endpoint}")
    def post(self, endpoint, json=None, headers=None):
        """
        Выполняет POST запрос к указанному эндпоинту.

        :param endpoint: (str): Эндпоинт для запроса.
        :param json: (dict or list): Данные JSON для отправки в теле запроса.
        :param headers: (dict or None): Заголовки для запроса.
        :return: httpx.Response: Ответ от сервера.
        """

        url = f"{self.base_url}{endpoint}"
        response = handle_http("POST", url, json=json, headers=headers, cookies=self.cookies)
        self.log_response(response)

        # Обновляем куки при необходимости
        if 'Set-Cookie' in response.headers:
            self.cookies.update(self.parse_cookies(response.headers['Set-Cookie']))
        return response


    @allure.step("Sending PUT request to {endpoint}")
    def put(self, endpoint, json=None, headers=None):
        """
        Выполняет PUT запрос к указанному эндпоинту.

        :param endpoint: (str): Эндпоинт для запроса.
        :param json: (dict or list): Данные JSON для отправки в теле запроса.
        :param headers: (dict or None): Заголовки для запроса.
        :return: httpx.Response: Ответ от сервера.
        """

        url = f"{self.base_url}{endpoint}"
        response = handle_http("PUT", url, json=json, headers=headers, cookies=self.cookies)
        self.log_response(response)
        return response


    @allure.step("Sending DELETE request to {endpoint}")
    def delete(self, endpoint, headers=None):
        """
        Выполняет DELETE запрос к указанному эндпоинту.

        :param endpoint: (str): Эндпоинт для запроса.
        :param headers: (dict or None): Заголовки для запроса.
        :return: httpx.Response: Ответ от сервера.
        """

        url = f"{self.base_url}{endpoint}"
        response = handle_http("DELETE", url, headers=headers, cookies=self.cookies)
        self.log_response(response)
        return response


    @staticmethod
    @allure.step("Logging response")
    def log_response(response):
        """
        Логирует информацию о ответе от сервера.

        :param response: (httpx.Response): Ответ от сервера.
        :return: None
        """

        if response.status_code not in (200, 201, 204):
            logger.error(f"Error response. Status code: {response.status_code} - Body: {response.text}")
        allure.attach(response.text, name="response_body", attachment_type=allure.attachment_type.JSON)


    @staticmethod
    @allure.step("Logging request")
    def log_request(method, url, headers=None, params=None, json=None):
        """
        Логирует информацию о выполненном запросе.

        :param method: (str): Метод HTTP-запроса.
        :param url: (str): URL запроса.
        :param headers: (dict or None): Заголовки запроса.
        :param params: (dict or None): Параметры запроса.
        :param json: (dict or None): Тело запроса в формате JSON.
        :return: None
        """

        logger.info(f"{method} Request to {url}")
        if headers:
            logger.info(f"Headers: {headers}")
            allure.attach(str(headers), name="request_headers", attachment_type=allure.attachment_type.TEXT)

        if params:
            logger.info(f"Params: {params}")
            allure.attach(str(params), name="request_params", attachment_type=allure.attachment_type.TEXT)

        if json:
            logger.info(f"Body: {json}")
            allure.attach(str(json), name="request_body", attachment_type=allure.attachment_type.JSON)
