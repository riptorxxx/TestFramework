from abc import ABC, abstractmethod
from typing import Dict, Set, List, Tuple


class DiskSelectionStrategy(ABC):
    """Base strategy for disk selection"""

    @abstractmethod
    def select_disks(self, cluster_info: dict, pool_config) -> tuple:
        pass


class AutoConfigureStrategy(DiskSelectionStrategy):
    """Strategy for automatic disk selection"""

    def select_disks(self, cluster_info: dict, pool_config) -> tuple:
        return (
            pool_config.pool_data.get('mainDisks', []),
            pool_config.pool_data.get('wrcDisks', []),
            pool_config.pool_data.get('rdcDisks', []),
            pool_config.pool_data.get('spareDisks', [])
        )


class ManualSelectionStrategy(DiskSelectionStrategy):
    """Strategy for manual disk selection"""

    def select_disks(self, cluster_info: dict, pool_config) -> tuple:
        used_disks = set()

        main_disks = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.mainDisksCount,
            used_disks,
            pool_config.mainDisksType,
            pool_config.mainDisksSize,
            "SSD" if pool_config.performance_type == 0 else None
        )
        used_disks.update(main_disks['disks'])

        wrc_disks = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.wrCacheDiskCount,
            used_disks,
            pool_config.wrcDiskType,
            pool_config.wrcDiskSize
        )
        used_disks.update(wrc_disks['disks'])

        rdc_disks = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.rdCacheDiskCount,
            used_disks,
            pool_config.rdcDiskType,
            pool_config.rdcDiskSize
        )
        used_disks.update(rdc_disks['disks'])

        spare_disks = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.spareCacheDiskCount,
            used_disks,
            pool_config.spareDiskType,
            pool_config.spareDiskSize
        )

        return (
            main_disks['disks'],
            wrc_disks['disks'],
            rdc_disks['disks'],
            spare_disks['disks']
        )

    def _select_disk_group(self, disks_by_size_and_type: Dict, count: int,
                           used_disks: Set, disk_type=None, disk_size=None,
                           priority_type=None) -> Dict:
        if count == 0:
            return {'disks': [], 'size': None, 'type': None}

        filtered_groups = self._filter_disk_groups(
            disks_by_size_and_type,
            disk_type,
            disk_size,
            priority_type
        )

        return self._select_from_filtered_groups(filtered_groups, count, used_disks)
