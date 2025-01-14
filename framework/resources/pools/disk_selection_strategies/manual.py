from typing import Dict, Set, Tuple
from dataclasses import dataclass
from framework.configs.pool_config import PoolConfig
from .base import DiskSelectionStrategy


@dataclass
class DiskGroup:
    disks: list
    size: int = None
    type: str = None


class ManualSelectionStrategy(DiskSelectionStrategy):
    """Strategy for manual disk selection during pools creation"""

    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> Tuple[list, list, list, list]:
        used_disks = set()

        main_disks = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.mainDisksCount,
            used_disks,
            pool_config.mainDisksType,
            pool_config.mainDisksSize,
            "SSD" if pool_config.performance_type == 0 else None
        )
        used_disks.update(main_disks.disks)

        wrc_disks = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.wrCacheDiskCount,
            used_disks,
            pool_config.wrcDiskType,
            pool_config.wrcDiskSize
        )
        used_disks.update(wrc_disks.disks)

        rdc_disks = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.rdCacheDiskCount,
            used_disks,
            pool_config.rdcDiskType,
            pool_config.rdcDiskSize
        )
        used_disks.update(rdc_disks.disks)

        spare_disks = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.spareCacheDiskCount,
            used_disks,
            pool_config.spareDiskType,
            pool_config.spareDiskSize
        )

        return (
            main_disks.disks,
            wrc_disks.disks,
            rdc_disks.disks,
            spare_disks.disks
        )

    def _select_disk_group(
            self,
            disks_by_size_and_type: Dict,
            count: int,
            used_disks: Set,
            disk_type: str = None,
            disk_size: int = None,
            priority_type: str = None
    ) -> DiskGroup:
        """
        Select disk group based on specified parameters

        Args:
            disks_by_size_and_type: Available disks grouped by size and type
            count: Number of disks to select
            used_disks: Set of already used disk IDs
            disk_type: Required disk type
            disk_size: Required disk size
            priority_type: Priority disk type for selection

        Returns:
            DiskGroup with selected disks and their parameters
        """
        if count == 0:
            return DiskGroup(disks=[])

        filtered_groups = self._filter_disk_groups(
            disks_by_size_and_type,
            disk_type,
            disk_size,
            priority_type
        )

        return self._select_from_filtered_groups(filtered_groups, count, used_disks)
