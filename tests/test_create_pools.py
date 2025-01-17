import pytest
from framework.configs.pool_config import PoolConfig


def test_create_minimal_pool(test_context):
    pool = test_context.tools_manager.pools.configure(
        name="test_pool",
        node=1,
        main_disks_count=2,
        auto_configure=True
    ).create_pool()

    assert pool["name"] == "test_pool"
    assert pool["node"] == 1

@pytest.mark.parametrize("base_url", ["NODE_1"], indirect=True)
@pytest.mark.parametrize("keys_to_extract", [["name"]])
@pytest.mark.parametrize("pool_config", [
    {
        "auto_configure": False,
        "raid_type": "raid1",
        "main_disks": 2,
        "wrc_disks": 1,
        "rdc_disks": 1,
        "spare_disks": 1
    },
    {
        "auto_configure": False,
        "raid_type": "raid5",
        "main_disks": 3,
        "wrc_disks": 2,
        "rdc_disks": 0,
        "spare_disks": 1
    }
])
def test_create_pool_manual(framework_context, pool_config):
    """Test pool creation with manual disk selection"""
    framework_context.tools_manager.auth.configure()
    pool_tool = framework_context.tools_manager.pool

    # Configure pool
    pool_tool.configure(**pool_config)

    # Create pool
    response = pool_tool.create_pool()
    assert response["status"] == "success"

    # Cleanup
    pool_tool.delete_pool(response["name"])


@pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
@pytest.mark.parametrize("pool_config", [
    {
        "raid_type": "raid1",
        "main_disks_type": "SSD",
        "main_disks_count": 2,
        "main_groups_count": 1
    },
    {
        "raid_type": "raid5",
        "main_disks_type": "HDD",
        "main_disks_count": 3,
        "main_groups_count": 1,
        "wr_cache_disk_count": 2,
        "wrc_disk_type": "SSD"
    }
])
def test_create_pool_auto(configured_auth_ctx, pool_config):
    """Test pool creation with automatic disk selection"""
    pool_tool = configured_auth_ctx.tools_manager.pools

    # Configure pool
    pool_tool.configure(**pool_config)

    # Create pool
    response = pool_tool.create_pool()
    assert response["status"] == "success"

    # Cleanup
    pool_tool.delete_pool(response["name"])


@pytest.mark.pc
@pytest.mark.parametrize("base_url", ["NODE_1", "NODE_2"], indirect=True)
@pytest.mark.parametrize("keys_to_extract", [["name"]])
@pytest.mark.parametrize("pool_config", [
    PoolConfig(raid_type="raid1", main_disks=2, wrc_disks=0, rdc_disks=0, spare_disks=0),
    # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=0, spareDisks=0),
    # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=1, spareDisks=0),
    # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=0, rdcDisks=0, spareDisks=1),
    # PoolConfig(raid_type="raid1", mainDisks=2, wrcDisks=2, rdcDisks=2, spareDisks=2),
])
def test_pool_creation(framework_context, pool_config):
    # Login with parametrized data
    framework_context.tools_manager.auth.login()

    # Create pools using pools tools
    pool_config = {...}
    result = framework_context.tools_manager.pools.create_pool(pool_config)

    # Assertions
    assert result["status"] == "success"

    # Cleanup
    framework_context.tools_manager.auth.logout()



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