from typing import List, Dict
from .base import DiskSelectionStrategy
from framework.models.pool_models import PoolConfig

class AutoConfigureStrategy(DiskSelectionStrategy):
    """Strategy for automatic disk selection"""

    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> tuple:
        """Select disks automatically based on configuration"""
        return (
            self._select_main_disks(cluster_info, pool_config),
            self._select_wrc_disks(cluster_info, pool_config),
            self._select_rdc_disks(cluster_info, pool_config),
            self._select_spare_disks(cluster_info, pool_config)
        )

    def _select_main_disks(self, cluster_info: dict, pool_config: PoolConfig) -> List[str]:
        """Select main disks based on configuration"""
        disks = cluster_info['free_disks_by_size_and_type']
        return self._select_disks_by_params(
            disks,
            pool_config.main_disks_count,
            pool_config.main_disks_type,
            pool_config.main_disks_size
        )

    def _select_wrc_disks(self, cluster_info: dict, pool_config: PoolConfig) -> List[str]:
        """Select write cache disks"""
        return self._select_disks_by_params(
            cluster_info['free_for_wc'],
            pool_config.wr_cache_disk_count,
            pool_config.wrc_disk_type,
            pool_config.wrc_disk_size,
            ssd_only=True
        )

    def _select_rdc_disks(self, cluster_info: dict, pool_config: PoolConfig) -> List[str]:
        """Select read cache disks"""
        return self._select_disks_by_params(
            cluster_info['free_disks'],
            pool_config.rd_cache_disk_count,
            pool_config.rdc_disk_type,
            pool_config.rdc_disk_size,
            ssd_only=True
        )

    def _select_spare_disks(self, cluster_info: dict, pool_config: PoolConfig) -> List[str]:
        """Select spare disks matching main disk parameters"""
        return self._select_disks_by_params(
            cluster_info['free_disks'],
            pool_config.spare_cache_disk_count,
            pool_config.spare_disk_type,
            pool_config.spare_disk_size
        )

    def _select_disks_by_params(
        self,
        available_disks: Dict,
        count: int,
        disk_type: str,
        disk_size: int,
        ssd_only: bool = False
    ) -> List[str]:
        """Helper method to select disks by parameters"""
        if count == 0:
            return []

        filtered_disks = [
            disk for disk in available_disks
            if (not disk_type or disk['type'] == disk_type) and
               (not disk_size or disk['size'] == disk_size) and
               (not ssd_only or disk['type'] == 'SSD')
        ]

        if len(filtered_disks) < count:
            raise ValueError(f"Not enough disks matching criteria. Required: {count}")

        return filtered_disks[:count]
