import pytest

from framework.api.core.logger import logger
from framework.api.models.pool_models import PoolConfig


class TestCreatePools:


    @pytest.mark.nc
    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    def test_get_pools(self, framework_context):
        pool_tools = framework_context.tools_manager.pool
        response = pool_tools.get_pools().json()
        logger.info(response)


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

        response = pool_tools.get_pools().json()
        logger.info(response)
        pool_tools.expand_pool(pool_tools.current_pool['name'])
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


    @pytest.mark.smoke
    @pytest.mark.nc
    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=0),
        # PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=0, spareDisks=0),
        # PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=1, spareDisks=0),
        # PoolConfig(auto_configure=False, raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=1),
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

        response = pool_tools.get_pools().json()
        logger.info(response)
        pool_tools.expand_pool(pool_tools.current_pool['name'])

        pool_tools.cleanup()


    @pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
    @pytest.mark.parametrize("keys_to_extract", [["name"]])
    @pytest.mark.parametrize("pool_config", [
        # PoolConfig(auto_configure=False, raid_type="raid5", mainDisks=3, wrcDisks=0, rdcDisks=0, spareDisks=0),
        # PoolConfig(auto_configure=False, raid_type="raid5", mainDisks=3, wrcDisks=2, rdcDisks=0, spareDisks=0),
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

