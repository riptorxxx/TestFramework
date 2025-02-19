import pytest

from framework.core.logger import logger
from framework.models.pool_models import PoolConfig


class TestCreatePools:


    @pytest.mark.nc
    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    def test_get_pool(self, framework_context):
        pool_tools = framework_context.tools_manager.pool
        response = pool_tools.get_pools().json()
        logger.info(response)
        # Проверяем успешное создание пула
        # assert response['status'] == "created"





    @pytest.mark.nc
    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        PoolConfig(
            raid_type="raid1",
            perfomance_type=1,
            mainDisksCount=2,
            mainGroupsCount=1,
            # mainDisksType=DiskType.SSD,
            # mainDisksSize=322122547200,
            wrCacheDiskCount=2,
            # wrcDiskType=DiskType.SSD,
            # wrcDiskSize=536870912000,
            spareCacheDiskCount=2,
            # spareDiskType=DiskType.SSD,
            # spareDiskSize=
            rdCacheDiskCount=2,
            # rdcDiskType=DiskType.SSD,
            # rdcDiskSize=322122547200,
            auto_configure=True
        ),
    ])
    def test_create_pool(self, framework_context, pool_config, keys_to_extract):
        # auth_tools = framework_context.tools_manager.auth
        # auth_tools.configure()
        # auth_tools.login()
        pool_tools = framework_context.tools_manager.pool
        pool_tools.configure(pool_config)
        response = pool_tools.create()

        # Проверяем успешное создание пула
        assert response['status'] == "created"

        # Проверяем что пул сохранился в current_pool
        assert pool_tools.current_pool is not None
        assert pool_tools.current_pool['name'] in pool_tools._pool_names

        pool_tools.cleanup()


    @pytest.mark.nc
    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        PoolConfig(
            raid_type="raid1",
            perfomance_type=0,
            mainDisksCount=2,
            mainGroupsCount=1,
            # mainDisksType=DiskType.SSD,
            # mainDisksSize=322122547200,
            spareCacheDiskCount=2,
            # spareDiskType=DiskType.SSD,
            # spareDiskSize=
            auto_configure=True
        ),
    ])
    def test_create_lvm_auto_pool(self, framework_context, pool_config, keys_to_extract):
        pool_tools = framework_context.tools_manager.pool
        pool_tools.configure(pool_config)
        response = pool_tools.create()

        # Проверяем успешное создание пула
        assert response['status'] == "created"

        # Проверяем что пул сохранился в current_pool
        assert pool_tools.current_pool is not None
        assert pool_tools.current_pool['name'] in pool_tools._pool_names
        pool_tools.cleanup()


    @pytest.mark.nc
    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=0, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=1, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=1),
        PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=2, spareDisks=2),
    ])
    def test_create_zfs_pool_manual_raid1(self, framework_context, pool_config, keys_to_extract):
        pool_tools = framework_context.tools_manager.pool
        pool_tools.configure(pool_config)
        response = pool_tools.create()

        # Проверяем успешное создание пула
        assert response['status'] == "created"

        # Проверяем что пул сохранился в current_pool
        assert pool_tools.current_pool is not None
        assert pool_tools.current_pool['name'] in pool_tools._pool_names

        pool_tools.cleanup()

    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        PoolConfig(auto_configure=False, raid_type="raid5", mainDisks=3, wrcDisks=0, rdcDisks=0, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid5", mainDisks=3, wrcDisks=2, rdcDisks=0, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid5", mainDisks=3, wrcDisks=0, rdcDisks=1, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid5", mainDisks=3, wrcDisks=0, rdcDisks=0, spareDisks=1),
        PoolConfig(auto_configure=False, raid_type="raid5", mainDisks=3, wrcDisks=2, rdcDisks=2, spareDisks=2),
    ])
    def test_create_zfs_pool_manual_raid5(self, framework_context, pool_config, keys_to_extract):
        pool_tools = framework_context.tools_manager.pool
        pool_tools.configure(pool_config)
        response = pool_tools.create()

        # Проверяем успешное создание пула
        assert response['status'] == "created"

        # Проверяем что пул сохранился в current_pool
        assert pool_tools.current_pool is not None
        assert pool_tools.current_pool['name'] in pool_tools._pool_names

        pool_tools.cleanup()


    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        PoolConfig(auto_configure=False, raid_type="raid6", mainDisks=4, wrcDisks=0, rdcDisks=0, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid6", mainDisks=4, wrcDisks=2, rdcDisks=0, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid6", mainDisks=4, wrcDisks=0, rdcDisks=1, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid6", mainDisks=4, wrcDisks=0, rdcDisks=0, spareDisks=1),
        PoolConfig(auto_configure=False, raid_type="raid6", mainDisks=4, wrcDisks=2, rdcDisks=2, spareDisks=2),
    ])
    def test_create_zfs_pool_manual_raid6(self, framework_context, pool_config, keys_to_extract):
        pool_tools = framework_context.tools_manager.pool
        pool_tools.configure(pool_config)
        response = pool_tools.create()

        # Проверяем успешное создание пула
        assert response['status'] == "created"

        # Проверяем что пул сохранился в current_pool
        assert pool_tools.current_pool is not None
        assert pool_tools.current_pool['name'] in pool_tools._pool_names

        pool_tools.cleanup()


    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        PoolConfig(auto_configure=False, raid_type="raid7", mainDisks=5, wrcDisks=0, rdcDisks=0, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid7", mainDisks=5, wrcDisks=2, rdcDisks=0, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid7", mainDisks=5, wrcDisks=0, rdcDisks=1, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid7", mainDisks=5, wrcDisks=0, rdcDisks=0, spareDisks=1),
        PoolConfig(auto_configure=False, raid_type="raid7", mainDisks=5, wrcDisks=2, rdcDisks=2, spareDisks=2),
    ])
    def test_create_zfs_pool_manual_raidb3(self, framework_context, pool_config, keys_to_extract):
        pool_tools = framework_context.tools_manager.pool
        pool_tools.configure(pool_config)
        response = pool_tools.create()

        # Проверяем успешное создание пула
        assert response['status'] == "created"

        # Проверяем что пул сохранился в current_pool
        assert pool_tools.current_pool is not None
        assert pool_tools.current_pool['name'] in pool_tools._pool_names

        pool_tools.cleanup()


    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(raid_type="raid1", perfomance_type=0, mainDisks=2, spareDisks=0),
        PoolConfig(auto_configure=False, raid_type="raid1", perfomance_type=0, mainDisks=2, spareDisks=1),
        # PoolConfig(raid_type="raid1", perfomance_type=0, mainDisks=2, spareDisks=2),
    ])
    def test_create_lvm_pool_manual_raid1(self, framework_context, pool_config, keys_to_extract):
        pool_tools = framework_context.tools_manager.pool
        pool_tools.configure(pool_config)
        response = pool_tools.create()

        # Проверяем успешное создание пула
        assert response['status'] == "created"

        # Проверяем что пул сохранился в current_pool
        assert pool_tools.current_pool is not None
        assert pool_tools.current_pool['name'] in pool_tools._pool_names

        pool_tools.cleanup()



# @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
# def test_create_pool_auto(framework_context):
#     # Fully automatic pool creation
#     response = framework_context.tools_manager.pool.create()
#     assert response.status_code == 200
#
#
# @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
# @pytest.mark.parametrize("keys_to_extract", [["name"]])
# @pytest.mark.parametrize("pool_config", [
#     PoolConfig(raid_type="raid6", main_disks_count=4, wr_cache_disk_count=2)
# ])
# def test_create_pool(framework_context, pool_config, keys_to_extract):
#     # Get cluster data with specified keys
#     cluster_data = framework_context.tools_manager.cluster.get_cluster_info(keys_to_extract)
#
#     # Select disks using our disk selector
#     selected_disks = framework_context.tools_manager.disk_selector.select_disks(cluster_data, pool_config)
#
#     # Create pool with selected disks
#     pool = framework_context.tools_manager.pool.create(
#         name=pool_config.name,
#         raid_type=pool_config.raid_type,
#         main_disks=selected_disks.main_disks,
#         wrc_disks=selected_disks.wrc_disks
#     )






# @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
# @pytest.mark.parametrize("keys_to_extract", [["name"]])
# @pytest.mark.parametrize("pool_config", [
#     PoolConfig(
#         name="test_raid1",
#         raid_type="raid1",
#         main_disks_count=2,
#         main_disks_type="HDD",
#         wr_cache_disk_count=1,
#         wrc_disk_type="SSD"
#     ),
#     PoolConfig(
#         name="test_raid6",
#         raid_type="raid6",
#         main_disks_count=4,
#         main_disks_type="HDD",
#         wr_cache_disk_count=2,
#         wrc_disk_type="SSD",
#         rd_cache_disk_count=2,
#         rdc_disk_type="SSD",
#         spare_cache_disk_count=2,
#         spare_disk_type="HDD"
#     )
# ])
# def test_create_pool_with_disk_selection(framework_context, pool_config):
#     # Get cluster data
#     cluster_data = framework_context.cluster.get_cluster_info()
#
#     # Select disks using our selector
#     selected_disks = framework_context.cluster.disk_selector.select_disks(cluster_data, pool_config)
#
#     # Create pool
#     pool = framework_context.cluster.create_pool(
#         name=pool_config.name,
#         raid_type=pool_config.raid_type,
#         main_disks=selected_disks.main_disks,
#         wrc_disks=selected_disks.wrc_disks,
#         rdc_disks=selected_disks.rdc_disks,
#         spare_disks=selected_disks.spare_disks
#     )
#
#     # Verify pool creation
#     assert pool.status == "healthy"
#     assert len(pool.main_disks) == pool_config.main_disks_count
#     if pool_config.wr_cache_disk_count:
#         assert len(pool.wrc_disks) == pool_config.wr_cache_disk_count
#
#
#
#
#
# def test_create_minimal_pool(test_context):
#     pool = test_context.tools_manager.pools.configure(
#         name="test_pool",
#         node=1,
#         main_disks_count=2,
#         auto_configure=True
#     ).create_pool()
#
#     assert pool["name"] == "test_pool"
#     assert pool["node"] == 1
#
# @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
# @pytest.mark.parametrize("keys_to_extract", [["name"]])
# @pytest.mark.parametrize("pool_config", [
#     {
#         "auto_configure": False,
#         "raid_type": "raid1",
#         "main_disks": 2,
#         "wrc_disks": 1,
#         "rdc_disks": 1,
#         "spare_disks": 1
#     },
#     {
#         "auto_configure": False,
#         "raid_type": "raid5",
#         "main_disks": 3,
#         "wrc_disks": 2,
#         "rdc_disks": 0,
#         "spare_disks": 1
#     }
# ])
# def test_create_pool_manual(framework_context, pool_config):
#     """Test pool creation with manual disk selection"""
#     framework_context.tools_manager.auth.configure()
#     pool_tool = framework_context.tools_manager.pool
#
#     # Configure pool
#     pool_tool.configure(**pool_config)
#
#     # Create pool
#     response = pool_tool.create_pool()
#     assert response["status"] == "success"
#
#     # Cleanup
#     pool_tool.delete_pool(response["name"])
#
#
# @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
# @pytest.mark.parametrize("pool_config", [
#     {
#         "raid_type": "raid1",
#         "main_disks_type": "SSD",
#         "main_disks_count": 2,
#         "main_groups_count": 1
#     },
#     {
#         "raid_type": "raid5",
#         "main_disks_type": "HDD",
#         "main_disks_count": 3,
#         "main_groups_count": 1,
#         "wr_cache_disk_count": 2,
#         "wrc_disk_type": "SSD"
#     }
# ])
# def test_create_pool_auto(configured_auth_ctx, pool_config):
#     """Test pool creation with automatic disk selection"""
#     pool_tool = configured_auth_ctx.tools_manager.pools
#
#     # Configure pool
#     pool_tool.configure(**pool_config)
#
#     # Create pool
#     response = pool_tool.create_pool()
#     assert response["status"] == "success"
#
#     # Cleanup
#     pool_tool.delete_pool(response["name"])
#
#
# @pytest.mark.pc
# @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
# @pytest.mark.parametrize("keys_to_extract", [["name"]])
# @pytest.mark.parametrize("pool_config", [
#     PoolConfig(raid_type="raid1", main_disks=2, wrc_disks=0, rdc_disks=0, spare_disks=0),
#     # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=0, spareDisks=0),
#     # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=1, spareDisks=0),
#     # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=1),
#     # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=2, spareDisks=2),
# ])
# def test_pool_creation(framework_context, pool_config):
#     # Login with parametrized data
#     framework_context.tools_manager.auth.login()
#
#     # Create pools using pools tools
#     pool_config = {...}
#     result = framework_context.tools_manager.pools.create_pool(pool_config)
#
#     # Assertions
#     assert result["status"] == "success"
#
#     # Cleanup
#     framework_context.tools_manager.auth.logout()



    #
    #
    # @pytest.mark.pc
    # @testit.externalID("create_pool_pc_1")
    # @testit.displayName("Создание обычного пула RAID1, с ручным выбором дисков")
    # @pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
    # @pytest.mark.parametrize("keys_to_extract", [["name"]])
    # @pytest.mark.parametrize("pool_config", [
    #     PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=0),
    #     # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=0, spareDisks=0),
    #     # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=1, spareDisks=0),
    #     # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=1),
    #     # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=2, spareDisks=2),
    # ])
    # def test_create_zfs_pool_manual_raid1(self, test_context, pool_config):
    #     """Создание RAID1 пула с ручным выбором дисков"""
    #     with testit.step(f"Подготовка конфигурации пула"):
    #         test_context.prepare_pool_config(pool_config)
    #
    #     with testit.step(f"Выбор дисков для пула: {test_context.pool_name}"):
    #         self.pools_helper.select_disks(test_context, pool_config)
    #
    #     with testit.step(f"Формирование запроса для пула: {test_context.pool_name}"):
    #         self.pools_helper.prepare_request(test_context)
    #         # testit.addMessage(f"data: {test_context.pool_data}")
    #
    #     with testit.step(f"Создание пула: {test_context.pool_name}"):
    #         response = self.pools_helper.create_pool(test_context)
    #         assert response.status_code == 201, f"Failed to create pool: {response.text}"
    #
    #     with testit.step(f"Удаление пула: {test_context.pool_name}"):
    #         test_context.delete_pool(test_context)
    #
    #