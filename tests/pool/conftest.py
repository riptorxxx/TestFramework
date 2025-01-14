import pytest
import testit
from framework.core import logger
from tests.api.tests.pools.pools_helpers import PoolsHelper


@pytest.fixture(autouse=True)
@pytest.mark.usefixtures("pools")
def log_test_scenario(request):
    """Логирование конфигурации текущего тестового сценария"""
    if hasattr(request.node, 'callspec'):
        pool_config = request.node.callspec.params.get('pool_config')
        if pool_config:
            try:
                if callable(pool_config):
                    # Get initial config parameters
                    initial_config = {
                        k: v for k, v in pool_config.__defaults__[0].items()
                        if v is not None
                    }
                    config_str = ', '.join(f"{k}={v}" for k, v in initial_config.items())
                else:
                    # For manual mode - existing logic
                    config_dict = {k: v for k, v in vars(pool_config).items() if v is not None}
                    config_str = ', '.join(f"{k}={v}" for k, v in config_dict.items())

                logger.info(f"Выполняем сценарий: [{config_str}]")
            except Exception as e:
                logger.warning(f"Failed to log test scenario: {str(e)}")
    yield


# def get_test_display_name(self):
#     base_config = f"RAID{self.raid_type.upper()}"
#     disk_config = f"M{self.mainDisks}W{self.wrcDisks}R{self.rdcDisks}S{self.spareDisks}"
#     mode = "Auto" if self.auto_configure else "Manual"
#     return f"{base_config}_{disk_config}_{mode}"


@pytest.fixture(autouse=True)
def pools_helper():
    """ Создаёт и сбрасывает состояние PoolsHelper перед каждым тестом благодаря аргументу autouse=True.
        Это давольно опасный аргумент, с ним нужно быть аккуратным и всегда держать в голове
    """
    helper = PoolsHelper()
    helper.reset_state()
    return helper


@pytest.fixture(scope="function")
def delete_pool(client, request_params):
    """
    Фикстура для удаления пула.

    Эта фикстура предоставляет функциональность для удаления пула
    с использованием API клиента. Она выполняет HTTP DELETE запрос
    на указанный конечный пункт и обрабатывает ответ.

    Args:
        client: API client, используемый для выполнения запросов.
        request_params (dict): Параметры запроса, включая заголовки.

    Returns:
        function: Возвращает функцию _delete_pool, которая принимает
                  объект test_context и выполняет удаление пула.

    Raises:
        None: В случае успешного удаления возвращается статус код 204.
              В противном случае возвращается статус код ошибки и сообщение об ошибке.
    """
    def _delete_pool(test_context):
        delete_endpoint = test_context.post_endpoint  # Already contains the correct path
        response = client.delete(delete_endpoint, headers=request_params['headers'])
        error_message = response.json().get("error", "Unknown error") if response.status_code != 204 else None

        with testit.step(f"Response code: {response.status_code}, Error: {error_message}"):
            if response.status_code != 204:
                logger.error(f"Ошибка при удалении пула {test_context.pool_name}: {error_message}")
                return response.status_code, error_message

            logger.info(f"Пул {test_context.pool_name} успешно удален.")
            return response.status_code, None

    yield _delete_pool

