import pytest
import testit
from tests.api.tests.pools.pools_helpers import PoolsHelper
from framework.configs.pool_config import PoolConfig
from framework.core.error_handler import TestErrorHandler



@TestErrorHandler.handle_test_errors
@testit.nameSpace("create pools")
@testit.className("TestPools")
class TestPools:
    """
    Тестовый класс для позитивных тестов по созданию пулов.

    Декораторы:
        TestErrorHandler.handle_test_errors: Обработка ошибок выполнения тестов
        testit.nameSpace: определяет namespace в TestIT для тестов.
        testit.className: Отмечает имя класса для отчетности тестов в testIT
    """

    def setup_method(self):
        self.pools_helper = PoolsHelper()

    # '''____________________________________ ZFS POOLS MANUAL DISKS CHOOSEN_________________________________________'''

    @pytest.mark.pc
    @testit.externalID("create_pool_pc_1")
    @testit.displayName("Создание обычного пула RAID1, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=0),
        # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=0, spareDisks=0),
        # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=1, spareDisks=0),
        # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=1),
        # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=2, spareDisks=2),
    ])
    def test_create_zfs_pool_manual_raid1(self, test_context, pool_config):
        """Создание RAID1 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)
            # testit.addMessage(f"data: {test_context.pool_data}")

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {test_context.pool_name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_2")
    @testit.displayName("Cоздание обычного пула RAID5, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(raid_type="raid5", mainDisks=3, wrcDisks=0, rdcDisks=0, spareDisks=0),
        # PoolConfig(raid_type="raid5", mainDisks=3, wrcDisks=2, rdcDisks=0, spareDisks=0),
        # PoolConfig(raid_type="raid5", mainDisks=3, wrcDisks=0, rdcDisks=1, spareDisks=0),
        # PoolConfig(raid_type="raid5", mainDisks=3, wrcDisks=0, rdcDisks=0, spareDisks=1),
        PoolConfig(raid_type="raid5", mainDisks=3, wrcDisks=2, rdcDisks=2, spareDisks=2),
    ])
    def test_create_zfs_pool_manual_raid5(self, test_context, pool_config):
        """Создание RAID5 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_3")
    @testit.displayName("Cоздание обычного пула RAID6, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(raid_type="raid6", mainDisks=4, wrcDisks=0, rdcDisks=0, spareDisks=0),
        # PoolConfig(raid_type="raid6", mainDisks=4, wrcDisks=2, rdcDisks=0, spareDisks=0),
        # PoolConfig(raid_type="raid6", mainDisks=4, wrcDisks=0, rdcDisks=1, spareDisks=0),
        # PoolConfig(raid_type="raid6", mainDisks=4, wrcDisks=0, rdcDisks=0, spareDisks=1),
        PoolConfig(raid_type="raid6", mainDisks=4, wrcDisks=2, rdcDisks=2, spareDisks=2),
    ])
    def test_create_zfs_pool_manual_raid6(self, test_context, pool_config):
        """Создание RAID6 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_4")
    @testit.displayName("Cоздание обычного пула RAIDB3, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(raid_type="raid7", mainDisks=5, wrcDisks=0, rdcDisks=0, spareDisks=0),
        # PoolConfig(raid_type="raid7", mainDisks=5, wrcDisks=2, rdcDisks=0, spareDisks=0),
        # PoolConfig(raid_type="raid7", mainDisks=5, wrcDisks=0, rdcDisks=1, spareDisks=0),
        # PoolConfig(raid_type="raid7", mainDisks=5, wrcDisks=0, rdcDisks=0, spareDisks=1),
        PoolConfig(raid_type="raid7", mainDisks=5, wrcDisks=2, rdcDisks=2, spareDisks=2),
    ])
    def test_create_zfs_pool_manual_raidb3(self, test_context, pool_config):
        """Создание RAID1 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    # '''____________________________________ LVM POOLS MANUAL DISKS CHOOSEN_________________________________________'''

    @pytest.mark.pc
    @testit.externalID("create_pool_pc_5")
    @testit.displayName("Создание быстрого пула RAID1, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(raid_type="raid1", perfomance_type=0, mainDisks=2, spareDisks=0),
        PoolConfig(raid_type="raid1", perfomance_type=0, mainDisks=2, spareDisks=1),
        # PoolConfig(raid_type="raid1", perfomance_type=0, mainDisks=2, spareDisks=2),
    ])
    def test_create_lvm_pool_manual_raid1(self, test_context, pool_config):
        """Создание RAID1 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)
            # testit.addMessage(f"data: {test_context.pool_data}")

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {test_context.pool_name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_6")
    @testit.displayName("Cоздание быстрого пула RAID5, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(raid_type="raid5", perfomance_type=0, mainDisks=3, spareDisks=0),
        PoolConfig(raid_type="raid5", perfomance_type=0, mainDisks=3, spareDisks=1),
        # PoolConfig(raid_type="raid5", perfomance_type=0, mainDisks=3, spareDisks=2),
    ])
    def test_create_lvm_pool_manual_raid5(self, test_context, pool_config):
        """Создание RAID5 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_7")
    @testit.displayName("Cоздание быстрого пула RAID6, с ручным выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(raid_type="raid6", perfomance_type=0, mainDisks=5, spareDisks=0),
        PoolConfig(raid_type="raid6", perfomance_type=0, mainDisks=5, spareDisks=1),
        # PoolConfig(raid_type="raid6", perfomance_type=0, mainDisks=6, spareDisks=2),
    ])
    def test_create_lvm_pool_manual_raid6(self, test_context, pool_config):
        """Создание RAID6 пула с ручным выбором дисков"""
        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {test_context.pool_name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)



    # '''____________________________________ ZFS POOLS AUTO DISKS CHOOSEN_________________________________________'''


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_8")
    @testit.displayName("Создание обычного пула RAID1, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid1", disk_type="SSD", disks_count=2, groups_count=1),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=2, groups_count=1),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=3, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="SSD", disks_count=3, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="SSD", disks_count=4, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=2, rdc_disk_type="SSD", spare_disk_count=2
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=4, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=2, rdc_disk_type="SSD", spare_disk_count=2
        #                                ),
        ])
    def test_create_zfs_pool_auto_raid1(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)



    @pytest.mark.pc
    @testit.externalID("create_pool_pc_9")
    @testit.displayName("Создание обычного пула RAID5, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid5", disk_type="SSD", disks_count=3, groups_count=1),
        # PoolsHelper.create_pool_config(raid_type="raid5", disk_type="HDD", disks_count=3, groups_count=1),
        # PoolsHelper.create_pool_config(raid_type="raid5", disk_type="HDD", disks_count=4, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid5", disk_type="SSD", disks_count=4, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid5", disk_type="SSD", disks_count=5, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=2, rdc_disk_type="SSD", spare_disk_count=2
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid5", disk_type="HDD", disks_count=4, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=2, rdc_disk_type="SSD", spare_disk_count=2
        #                                ),
        ])
    def test_create_zfs_pool_auto_raid5(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_10")
    @testit.displayName("Создание обычного пула RAID6, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid6", disk_type="SSD", disks_count=4, groups_count=1),
        # PoolsHelper.create_pool_config(raid_type="raid6", disk_type="HDD", disks_count=4, groups_count=1),
        # PoolsHelper.create_pool_config(raid_type="raid6", disk_type="HDD", disks_count=5, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid6", disk_type="SSD", disks_count=5, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid6", disk_type="SSD", disks_count=6, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=2, rdc_disk_type="SSD", spare_disk_count=2
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid6", disk_type="HDD", disks_count=4, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=2, rdc_disk_type="SSD", spare_disk_count=2
        #                                ),
        ])
    def test_create_zfs_pool_auto_raid6(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_11")
    @testit.displayName("Создание обычного пула RAIDB3, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid7", disk_type="SSD", disks_count=5, groups_count=1),
        # PoolsHelper.create_pool_config(raid_type="raid7", disk_type="HDD", disks_count=5, groups_count=1),
        # PoolsHelper.create_pool_config(raid_type="raid7", disk_type="HDD", disks_count=6, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid7", disk_type="SSD", disks_count=6, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid7", disk_type="SSD", disks_count=7, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=2, rdc_disk_type="SSD", spare_disk_count=2
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid7", disk_type="HDD", disks_count=5, groups_count=1,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=2, rdc_disk_type="SSD", spare_disk_count=1
        #                                ),
        ])
    def test_create_zfs_pool_auto_raidb3(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_12")
    @testit.displayName("Создание обычного пула RAID1, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid1", disk_type="SSD", disks_count=2, groups_count=2),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="SSD", disks_count=2, groups_count=3),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=2, groups_count=2),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=2, groups_count=3),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=3, groups_count=2,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        ])
    def test_create_zfs_pool_auto_raid10(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)



    @pytest.mark.pc
    @testit.externalID("create_pool_pc_13")
    @testit.displayName("Создание обычного пула RAID10, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid1", disk_type="SSD", disks_count=2, groups_count=2),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="SSD", disks_count=2, groups_count=3),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=2, groups_count=2),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=2, groups_count=3),
        # PoolsHelper.create_pool_config(raid_type="raid1", disk_type="HDD", disks_count=3, groups_count=2,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        ])
    def test_create_zfs_pool_auto_raid10(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_14")
    @testit.displayName("Создание обычного пула RAID50, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid5", disk_type="SSD", disks_count=3, groups_count=2),
        # PoolsHelper.create_pool_config(raid_type="raid5", disk_type="SSD", disks_count=3, groups_count=3),
        # PoolsHelper.create_pool_config(raid_type="raid5", disk_type="HDD", disks_count=3, groups_count=2),
        # PoolsHelper.create_pool_config(raid_type="raid5", disk_type="HDD", disks_count=3, groups_count=2,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD"
        #                                ),
        ])
    def test_create_zfs_pool_auto_raid50(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_15")
    @testit.displayName("Создание обычного пула RAID60, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid6", disk_type="SSD", disks_count=4, groups_count=2),
        # PoolsHelper.create_pool_config(raid_type="raid6", disk_type="SSD", disks_count=4, groups_count=2,
        #             wrc_disk_count=2, wrc_disk_type="SSD", rdc_disk_count=1, rdc_disk_type="SSD",
        #             spare_disk_count=1, spare_disk_type="SSD"
        #                                ),
        ])
    def test_create_zfs_pool_auto_raid60(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_16")
    @testit.displayName("Создание обычного пула RAIDB30, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid7", disk_type="SSD", disks_count=5, groups_count=2),

        ])
    def test_create_zfs_pool_auto_raidb30(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)

    # '''____________________________________ LVM POOLS AUTO DISKS CHOOSEN_________________________________________'''


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_17")
    @testit.displayName("Создание быстрого пула RAID1, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid1", perfomance_type=0, disk_type="SSD",
                                       disks_count=2, groups_count=1
                                       ),
        # PoolsHelper.create_pool_config(raid_type="raid1", perfomance_type=0, disk_type="SSD",
        #                                disks_count=2, groups_count=1, spare_disk_count=1
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid1", perfomance_type=0, disk_type="SSD",
        #                                disks_count=2, groups_count=1, spare_disk_count=2
        #                                ),
        ])
    def test_create_lvm_pool_auto_raid1(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_18")
    @testit.displayName("Создание быстрого пула RAID5, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid5", perfomance_type=0, disk_type="SSD",
                                       disks_count=3, groups_count=1
                                       ),
        # PoolsHelper.create_pool_config(raid_type="raid5", perfomance_type=0, disk_type="SSD",
        #                                disks_count=4, groups_count=1, spare_disk_count=1
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid5", perfomance_type=0, disk_type="SSD",
        #                                disks_count=5, groups_count=1, spare_disk_count=2
        #                                ),
        ])
    def test_create_lvm_pool_auto_raid5(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)


    @pytest.mark.pc
    @testit.externalID("create_pool_pc_19")
    @testit.displayName("Создание быстрого пула RAID6, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid6", perfomance_type=0, disk_type="SSD",
                                       disks_count=5, groups_count=1
                                       ),
        # PoolsHelper.create_pool_config(raid_type="raid6", perfomance_type=0, disk_type="SSD",
        #                                disks_count=6, groups_count=1, spare_disk_count=1
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid6", perfomance_type=0, disk_type="SSD",
        #                                disks_count=7, groups_count=1, spare_disk_count=2
        #                                ),
        ])
    def test_create_lvm_pool_auto_raid6(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)



    @pytest.mark.pc
    @testit.externalID("create_pool_pc_20")
    @testit.displayName("Создание быстрого пула RAID10, с автоматическим выбором дисков")
    @pytest.mark.parametrize("base_url", ["NODE_1","NODE_2"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name", "size", "type"]])
    @pytest.mark.parametrize("pool_config", [
        PoolsHelper.create_pool_config(raid_type="raid1", perfomance_type=0, disk_type="SSD",
                                       disks_count=2, groups_count=2
                                       ),
        # PoolsHelper.create_pool_config(raid_type="raid1", perfomance_type=0, disk_type="SSD",
        #                                disks_count=2, groups_count=2, spare_disk_count=1
        #                                ),
        # PoolsHelper.create_pool_config(raid_type="raid1", perfomance_type=0, disk_type="SSD",
        #                                disks_count=2, groups_count=2, spare_disk_count=2
        #                                ),
        ])
    def test_create_lvm_pool_auto_raid10(self, test_context, pool_config):
        """Создание пулов с разными RAID конфигурациями"""

        with testit.step(f"Подготовка конфигурации пула"):
            pool_data = test_context.prepare_pool_config(pool_config)

        with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
            self.pools_helper.select_disks(test_context, pool_config)

        with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
            self.pools_helper.prepare_request(test_context)

        with testit.step(f"Создание пула: {pool_config.name}"):
            response = self.pools_helper.create_pool(test_context)
            assert response.status_code == 201, f"Failed to create pool: {response.text}"

        with testit.step(f"Удаление пула: {pool_config.name}"):
            test_context.delete_pool(test_context)