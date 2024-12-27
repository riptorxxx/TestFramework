import pytest
import allure
from framework.api_client import APIClient
import os
from dotenv import load_dotenv
from framework.context import TestContext

#   Загрузка переменных окружения из .env файла. Нужно для фикстуры login.
load_dotenv()


@pytest.fixture(scope="session")
def base_url(request):
    """
    Фикстура устанавливает base_url в зависимости от
    пришедшего из теста параметра NODE (NODE_1, NODE_2....)

    :param request: Объект запроса pytest.
    :return: Значение URL из .env файла.
    """
    if hasattr(request, 'param'):
        node = request.param

        if node == "NODE_1":
            return os.getenv("NODE_1")
        elif node == "NODE_2":
            return os.getenv("NODE_2")
        else:
            raise ValueError(f"Unknown NODE: {node}")


@pytest.fixture(scope="function")
def client(base_url):
    """
    Фикстура для инициализации APIClient с правильным base_url
    Scope: function
    Установка scope="function" здесь нужно, что бы каждый тест мог использовать разные значения base_url.
    Это позволяет создавать новый экземпляр APIClient для каждого теста,
    что обеспечивает изоляцию и предотвращает возможные проблемы с состоянием.

    :param base_url:
    :return:
    """
    return APIClient(base_url)


#   Фикстура для установки заголовков, query параметров и других атрибутов
@pytest.fixture(scope="function")
def request_params(login):
    """
    Фикстура `request_params` создает словарь с заголовками и параметрами запроса,
    которые могут быть использованы в тестах для выполнения HTTP-запросов.
    Эта фикстура зависит от фикстуры `login`, которая должна возвращать объект
    с куками (cookies) после успешной аутентификации.

    :param login: Фикстура, возвращающая ответ и куки после аутентификации.
                  Ожидается, что `login` возвращает кортеж из двух элементов:
                  1. response: объект ответа (например, HTTPResponse).
                  2. cookies: словарь с куками, полученными из ответа.

    :return: Словарь с заголовками и параметрами запроса:
    """
    # Извлекаем куки из фикстуры login
    response, cookies = login

    return {
        "headers": {
            # "Authorization": "Bearer some_token",
            "Content-Type": "application/json",
            "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])  # Добавляем куки
        },
        "params": {
            # "search": "test"  # Пример query параметра
        }
    }

#
# @pytest.fixture(scope="function")
# def login(client, base_url, request):
#     """
#     Фикстура для авторизации пользователя.
#
#     Эта фикстура выполняет авторизацию на сервере, используя переданные параметры
#     (username и password). Если параметры не переданы из теста, используются значения
#     по умолчанию из .env файла.
#
#     :param client: Экземпляр клиента для выполнения HTTP-запросов.
#     :param base_url: Базовый URL сервера.
#     :param request: Объект запроса, который содержит параметры теста.
#     :return: Кортеж (response, cookies), где:
#              - response: Объект ответа от сервера после попытки авторизации.
#              - cookies: Словарь с куками, полученными из заголовка 'Set-Cookie'.
#
#     :raises AssertionError: Если статус-код ответа не равен 200.
#     """
#     # Получаем параметры username и password из request.param
#     params = request.param if hasattr(request, 'param') else {}
#
#     username = params.get("username") if isinstance(params, dict) else None
#     password = params.get("password") if isinstance(params, dict) else None
#
#     # Проверяем наличие параметров
#     if username is None and password is None:
#         # Используем значения из .env файла
#         username = os.getenv("NODE_USERNAME")
#         password = os.getenv("NODE_PASSWORD")
#
#     # Формируем запрос
#     endpoint = "/login"
#     data = {
#         "login": username,
#         "password": password,
#         "remember": True
#     }
#
#     with allure.step(f"Выполняем авторизацию на {base_url}{endpoint}"):
#         response = client.post(endpoint, json=data)
#         # logger.info(f"Получено тело ответа: {response.json()}")
#
#     assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
#
#     with allure.step(f"Извлекаем куки"):
#         cookies = {}
#         if 'Set-Cookie' in response.headers:
#             cookies.update(client.parse_cookies(response.headers['Set-Cookie']))
#         # logger.info(f"Получили куки: {response.headers.get('Set-Cookie')}")
#
#     return response, cookies
#
#
# # Фикстура для выхода из системы
# @pytest.fixture(scope="function")
# def logout(client, base_url, login):
#     """
#     Функция для выхода пользователя из системы.
#
#     Эта функция выполняет выход пользователя, используя данные, полученные при авторизации.
#     Она формирует запрос на выход и отправляет его на сервер.
#
#     :param client: Экземпляр клиента для выполнения HTTP-запросов.
#     :param base_url: Базовый URL сервера.
#     :param login: Кортеж, содержащий ответ и куки из фикстуры авторизации.
#                   Ожидается, что кортеж содержит:
#                   - response: Объект ответа от сервера после авторизации.
#                   - cookies: Словарь с куками, полученными из заголовка 'Set-Cookie'.
#
#     :return: Объект ответа от сервера после выполнения запроса на выход.
#     :raises AssertionError: Если статус-код ответа не равен 204 (No Content).
#     """
#     response, cookies = login  # Получаем ответ и куки из фикстуры login
#     yield
#     with allure.step(f"Парсим ответ полученный при авторизации"):
#         response_data = response.json()
#         sid = response_data['sid']
#         user = response_data['data']['login']
#         role = response_data['data']['role']
#         # logger.info(f"Результат парсинга (Данные авторизованного пользователя): \n sid={sid} user={user} role={role}")
#
#     #   Формируем запрос
#     with allure.step(f"Формируем запрос"):
#         endpoint = "/logout"
#         headers = {
#             "Cookie": f"jwt_access={cookies.get('jwt_access')}"
#         }
#         data = {
#             "sid": sid,
#             "login": user,
#             "role": role
#         }
#
#     #   Отправляем запрос
#     #     logger.info(f"Отправляем данные для выхода: {data}")
#     with allure.step(f"Отправляем запрос на {base_url} {endpoint}"):
#         response = client.post(endpoint, json=data, headers=headers)
#         assert response.status_code == 204, f"Unexpected status code: {response.status_code}"
#
#         return response
#

@pytest.fixture(scope="function")
def cluster_info(client, base_url):
    """
    Фикстура для получения информации о кластере.

    Эта фикстура выполняет HTTP GET запрос к эндпоинту '/nodes/clusterInfo',
    чтобы получить информацию о текущем состоянии кластера. Данные из ответа
    будут использоваться в тестах для обращения к конкретным объектам через
    параметризацию.

    :param client: API клиент, используемый для выполнения запросов.
    :param base_url: Базовый URL для API.
    :return: dict: Словарь с информацией о кластере или None в случае ошибки.
    :raises AssertionError: Если статус код ответа не равен 200 или если ответ пустой.
    """
    with allure.step("Получаем данные о кластере."):
        endpoint = "/nodes/clusterInfo"

        response = client.get(endpoint)
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

        response_dict = response.json()
        assert response_dict is not None and len(response_dict) > 0, f"Response is empty: {response_dict}."
        # logger.info(f"Информация о кластере успешно получена: {response_dict}")

        return response_dict


@pytest.fixture(scope="function")
def authenticated_context(test_context):
    connection = test_context.tools_manager.connection
    connection.configure()
    connection.login()

    yield test_context

    connection.logout()


@pytest.fixture
def framework_context(client, base_url, cluster_info, keys_to_extract):
    """Create framework context for tests"""
    return TestContext(
        client=client,
        base_url=base_url,
        # request_params=request_params,
        cluster_info=cluster_info,
        keys_to_extract=keys_to_extract
    )



# @pytest.fixture(scope="function")
# def test_context(request, client, base_url, request_params, cluster_info, keys_to_extract, delete_pool, logout):
#     """
#     Фикстура для создания экземпляра `TestContext`.
#
#     Эта фикстура принимает в качестве аргументов другие фикстуры (включая стандартный
#     `request` pytest) и возвращает нужный контекст в зависимости от класса теста.
#
#     :param request: Объект запроса pytest.
#     :param client: API клиент для выполнения запросов.
#     :param base_url: Базовый URL для API.
#     :param request_params: (dict): Параметры запроса, включая заголовки.
#     :param cluster_info: (dict): Информация о кластере, полученная из фикстуры cluster_info.
#     :param keys_to_extract: (list): Ключи для извлечения данных из cluster_info.
#     :param delete_pool: Фикстура для удаления пула.
#     :param logout: Фикстура для выполнения выхода из системы.
#     :return: TestContext: Экземпляр `TestContext`, настроенный в зависимости от класса теста.
#     :raises ValueError: Если класс теста неизвестен или не поддерживается.
#     """
#     test_class = request.node.parent
#
#     if ((test_class is not None and test_class.name == "TestPools") or
#             (test_class is not None and test_class.name == "TestPoolsNegative")):
#         return TestContext(
#             client,
#             base_url,
#             request_params,
#             cluster_info,
#             keys_to_extract,
#             delete_pool,
#             logout,
#             request
#         )
#     else:
#         raise ValueError(f"Unknown test class: {getattr(request.node, 'cls', None)}")
