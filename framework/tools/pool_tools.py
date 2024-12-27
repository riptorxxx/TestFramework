from framework.tools.base_tools import BaseTools
from framework.pool.config import PoolConfig
from framework.helpers.retry import disk_operation_with_retry


class PoolTools(BaseTools):
    """Tools for pool operations"""

    def __init__(self, context):
        super().__init__(context)
        self.current_pool = None

    def validate(self):
        self._context.tools_manager.cluster.validate()

    @disk_operation_with_retry()
    def create_pool(self, pool_config: PoolConfig):
        """Create pool with configuration"""
        self.validate()
        selected_disks = self._context.tools_manager.disk.select_disks_for_pool(pool_config)
        pool_config.update_disks(selected_disks)

        response = self._context.client.post(
            "/pools",
            json=pool_config.to_request_data()
        )
        assert response.status_code == 200
        self.current_pool = response.json()
        return self.current_pool

    def cleanup(self):
        """Cleanup created pools"""
        if self.current_pool:
            self._context.client.delete(f"/pools/{self.current_pool['name']}")
