import pytest
import testit
from tests.api.tests.pools.pool_errors import POOL_ERRORS
from tests.api.tests.pools.pools_helpers import PoolsHelper, PoolConfig
from tests.api.helpers.error_handler import TestErrorHandler
# from tests.api.api_client import logger


@pytest.fixture(autouse=True)
def handle_nc_marker(request):
    """
    Фикстура выставляет флаг True для тестов помеченных как негативные (pytest.mark.nc).
    Нужно для того что бы убрать валидацию на минимальное кол-во дисков для создания пула.
    и не выполнять повторные запросы к cluster_info.
    :param request: Внутренняя фикстура pytest
    """
    if request.node.get_closest_marker('nc'):
        setattr(pytest, 'skip_validation', True)
        yield
        delattr(pytest, 'skip_validation')
    else:
        yield


@TestErrorHandler.handle_test_errors
@testit.nameSpace("create pools")
@testit.className("TestPoolsNegative")
class TestPoolsNegative:
    """
    Тестовый класс для негативных тестов создания пулов

    Декораторы:
        TestErrorHandler.handle_test_errors: Обработка ошибок выполнения тестов
        testit.className: Отмечает имя класса для отчетности тестов в testIT
    """

    def setup_method(self):
        self.pools_helper = PoolsHelper()


# ________________________ Негативные тесты направленные на проверку бизнес логики _________________________

    @pytest.mark.nc
    @testit.externalID("create_pool_nc_1")
    @testit.displayName("Негативная проверка создания обычного пула RAID1 с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config, expected_error", [
        (PoolConfig(raid_type="raid1", mainDisks=1, wrcDisks=0, rdcDisks=0, spareDisks=0),
         POOL_ERRORS['INVALID_DISK_COUNT_RAID1_MAIN']),
        (PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=1, rdcDisks=0, spareDisks=0),
         POOL_ERRORS['INVALID_WRC_DISK_COUNT'])
    ])
    def test_create_pool_manual_raid1_negative(self, test_context, pool_config, expected_error):
        """Создание RAID1 пула с ручным выбором дисков (негативный сценарий)"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)

            assert response.status_code == 500, f"Expected status code 500, got {response.status_code}"
            actual_response = response.json()
            assert expected_error["msg"] == actual_response[
                "msg"], f"\nExpected: {expected_error['msg']}\nActual: {actual_response['msg']}"
            assert expected_error["code"] == actual_response[
                "code"], f"\nExpected code: {expected_error['code']}\nActual code: {actual_response['code']}"


    @pytest.mark.nc
    @testit.externalID("create_pool_nc_2")
    @testit.displayName("Негативная проверка создания обычного пула RAID5, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1" ,"NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config, expected_error", [
        (PoolConfig(raid_type="raid5", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=0),
         POOL_ERRORS['INVALID_DISK_COUNT_RAID5_MAIN']),
        (PoolConfig(raid_type="raid5", mainDisks=3, wrcDisks=1, rdcDisks=0, spareDisks=0),
         POOL_ERRORS['INVALID_WRC_DISK_COUNT'])
    ])
    def test_create_pool_manual_raid5_negative(self, test_context, pool_config, expected_error):
        """Создание RAID5 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)

            assert response.status_code == 500, f"Expected status code 500, got {response.status_code}"
            actual_response = response.json()
            assert expected_error["msg"] == actual_response[
                "msg"], f"\nExpected: {expected_error['msg']}\nActual: {actual_response['msg']}"
            assert expected_error["code"] == actual_response[
                "code"], f"\nExpected code: {expected_error['code']}\nActual code: {actual_response['code']}"


    @pytest.mark.nc
    @testit.externalID("create_pool_nc_3")
    @testit.displayName("Негативная проверка создания обычного пула RAID6, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1" ,"NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config, expected_error", [
        (PoolConfig(raid_type="raid6", mainDisks=3, wrcDisks=0, rdcDisks=0, spareDisks=0),
         POOL_ERRORS['INVALID_DISK_COUNT_RAID6_MAIN']),
        (PoolConfig(raid_type="raid6", mainDisks=4, wrcDisks=1, rdcDisks=0, spareDisks=0),
         POOL_ERRORS['INVALID_WRC_DISK_COUNT'])
    ])
    def test_create_pool_manual_raid6_negative(self, test_context, pool_config, expected_error):
        """Создание RAID6 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)

            assert response.status_code == 500, f"Expected status code 500, got {response.status_code}"
            actual_response = response.json()
            assert expected_error["msg"] == actual_response[
                "msg"], f"\nExpected: {expected_error['msg']}\nActual: {actual_response['msg']}"
            assert expected_error["code"] == actual_response[
                "code"], f"\nExpected code: {expected_error['code']}\nActual code: {actual_response['code']}"


    @pytest.mark.nc
    @testit.externalID("create_pool_nc_4")
    @testit.displayName("Негативная проверка создания обычного пула RAIDB3, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1" ,"NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config, expected_error", [
        (PoolConfig(raid_type="raid7", mainDisks=4, wrcDisks=0, rdcDisks=0, spareDisks=0),
         POOL_ERRORS['INVALID_DISK_COUNT_RAIDB3_MAIN']),
        (PoolConfig(raid_type="raid7", mainDisks=5, wrcDisks=1, rdcDisks=0, spareDisks=0),
         POOL_ERRORS['INVALID_WRC_DISK_COUNT'])
    ])
    def test_create_pool_manual_raidb3_negative(self, test_context, pool_config, expected_error):
        """Создание RAID6 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)

            assert response.status_code == 500, f"Expected status code 500, got {response.status_code}"
            actual_response = response.json()
            assert expected_error["msg"] == actual_response[
                "msg"], f"\nExpected: {expected_error['msg']}\nActual: {actual_response['msg']}"
            assert expected_error["code"] == actual_response[
                "code"], f"\nExpected code: {expected_error['code']}\nActual code: {actual_response['code']}"



# ________________________ Негативные тесты направленные на валидацию контракта _________________________

