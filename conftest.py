import pytest
import os
from framework.api.core.api_client import APIClient
from dotenv import load_dotenv
from framework.api.core.context import TestContext
from framework.api.tools.connection_tools import ConnectionTools

#   Загрузка переменных окружения из .env файла. Нужно для переключения между нодами.
load_dotenv()

# def pytest_runtest_setup(item):
#     """Hook для установки текущего теста в сериализатор"""
#     from framework.utils.serializer import Serializer
#     Serializer.current_test = item

@pytest.fixture(scope="session")
def connection_tools():
    """
    Фикстура создает и предоставляет инструмент для работы с нодами тестового окружения.

    Scope="session" обеспечивает:
    - Единый экземпляр ConnectionTools на всю сессию тестирования
    - Однократную загрузку конфигурации нод из .env файла
    - Кэширование списка доступных нод
    - Оптимизацию использования ресурсов

    Returns:
        ConnectionTools: Инструмент для управления подключениями к нодам

    Example:
        def test_example(connection_tools):
            connection_tools.configure("NODE_1")
            config = connection_tools.get_current_config()
            assert config.node == "NODE_1"
    """
    return ConnectionTools(None)


@pytest.fixture(scope="session")
def base_url(request, connection_tools):
    """
    Фикстура для управления базовым URL тестового окружения.

    Работает на уровне сессии тестирования и использует ConnectionTools
    для конфигурации URL в зависимости от выбранной ноды.

    Args:
        request: Объект pytest request для доступа к параметрам параметризации
        connection_tools: Инструмент управления подключениями к нодам

    Returns:
        str: URL выбранной ноды из конфигурации

    Example:
        @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
        def test_example(base_url):
            assert base_url.startswith('http')
    """
    if hasattr(request, 'param'):
        connection_tools.configure(request.param)
        return connection_tools.get_current_config().url


@pytest.fixture
def node_switcher(framework_context):
    """
    Фикстура предоставляет функцию для динамического переключения между нодами в рамках одного теста.

    Создает и возвращает замыкание, которое позволяет:
    - Переключаться между нодами в любой момент выполнения теста
    - Автоматически обновлять base_url в клиенте
    - Сохранять контекст подключения

    Args:
        framework_context: Контекст тестового фреймворка

    Returns:
        Callable[[str], None]: Функция switch_to для переключения на указанную ноду

    Example:
        def test_cross_node(node_switcher):
            node_switcher("NODE_1")
            # выполняем действия на NODE_1
            node_switcher("NODE_2")
            # выполняем действия на NODE_2
    """
    connection_tool = framework_context.tools_manager.connection

    def switch_to(node: str):
        connection_tool.configure(node)
        framework_context.client.base_url = os.getenv(node)

    return switch_to


@pytest.fixture(scope="session")
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

# Строчка для распаралеливания тестов. Копирует контекст независимый от другого.
# context = copy.deepcopy(base_framework_context)

@pytest.fixture(scope="session")
def base_framework_context(client, base_url, request):
    """Base context without auth"""
    context = TestContext(client=client, base_url=base_url, request=request)

    yield context

    # Logout only after all tests complete
    if context.tools_manager.auth.is_authenticated():
        context.tools_manager.auth.logout_and_clean()

@pytest.fixture(scope="function")
def framework_context(base_framework_context, request):
    """Context with authentication"""
    base_framework_context.request = request
    base_framework_context.tools_manager.auth.authentication()

    return base_framework_context
