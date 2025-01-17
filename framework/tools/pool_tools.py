from typing import Dict, List, Optional
from .base_tools import BaseTools
from ..configs.pool_config import PoolConfig
from ..helpers.retry import disk_operation_with_retry
from ..resources.disks.disk_selector import DiskSelector


class PoolTools(BaseTools):
    def __init__(self, context):
        super().__init__(context)
        self._config: Optional[PoolConfig] = None
        self.current_pool = None
        # self._disk_selector = DiskSelector(context.tools_manager.disks)
        self._disk_tool = disk_tool or context.tools_manager.get_tool('disks')

    def configure(self, **kwargs) -> 'PoolTools':
        """Configure pool parameters"""
        self._config = PoolConfig(**kwargs)
        return self

    def validate(self):
        """Validate cluster state before pool operations"""
        self._context.tools_manager.cluster.validate()

    @disk_operation_with_retry()
    def create_pool(self) -> dict:
        """Create pool with current configuration"""
        if not self._config:
            raise ValueError("Pool configuration not set")

        self.validate()

        # Select and update disks configuration
        selected_disks = self.select_disks_for_pool()
        self._update_pool_disks(selected_disks)

        response = self._context.client.post(
            "/pools",
            json=self._config.to_request()
        )

        if response.status_code != 201:
            raise ValueError(f"Failed to create pool: {response.text}")

        self.current_pool = response.json()
        return self.current_pool

    def select_disks_for_pool(self) -> tuple:
        """Select disks based on pool configuration"""
        disk_tool = self._context.tools_manager.disks

        if self._config.auto_configure:
            return disk_tool.select_disks_auto(
                main_type=self._config.main_disks_type,
                main_count=self._config.main_disks_count,
                wrc_type=self._config.wrc_disk_type,
                wrc_count=self._config.wr_cache_disk_count,
                rdc_type=self._config.rdc_disk_type,
                rdc_count=self._config.rd_cache_disk_count,
                spare_type=self._config.spare_disk_type,
                spare_count=self._config.spare_cache_disk_count
            )
        else:
            return disk_tool.select_disks_manual(
                main_count=self._config.main_disks,
                wrc_count=self._config.wrc_disks,
                rdc_count=self._config.rdc_disks,
                spare_count=self._config.spare_disks
            )

    def _update_pool_disks(self, selected_disks: tuple):
        """Update pool configuration with selected disks"""
        main_disks, wrc_disks, rdc_disks, spare_disks = selected_disks
        self._config.main_disks = main_disks
        self._config.wrc_disks = wrc_disks
        self._config.rdc_disks = rdc_disks
        self._config.spare_disks = spare_disks

    def delete_pool(self, pool_name: str) -> None:
        """Delete pool by name"""
        response = self._context.client.delete(f"/pools/{pool_name}")

        if response.status_code not in (200, 204):
            raise ValueError(f"Failed to delete pool: {response.text}")

        self.current_pool = None

    def cleanup(self):
        """Cleanup created pools"""
        if self.current_pool:
            self.delete_pool(self.current_pool['name'])

#
# class PoolTools(BaseTools):
#     """Tools for pools operations"""
#
#     def __init__(self, context):
#         super().__init__(context)
#         self.current_pool = None
#
#     def validate(self):
#         self._context.tools_manager.cluster.validate()
#
#     @disk_operation_with_retry()
#     def create_pool(self, pool_config: PoolConfig):
#         """Create pools with configuration"""
#         self.validate()
#         selected_disks = self._context.tools_manager.disk.select_disks_for_pool(pool_config)
#         pool_config.update_disks(selected_disks)
#
#         response = self._context.client.post(
#             "/pools",
#             json=pool_config.to_request_data()
#         )
#         assert response.status_code == 200
#         self.current_pool = response.json()
#         return self.current_pool
#
#     def cleanup(self):
#         """Cleanup created pools"""
#         if self.current_pool:
#             self._context.client.delete(f"/pools/{self.current_pool['name']}")
