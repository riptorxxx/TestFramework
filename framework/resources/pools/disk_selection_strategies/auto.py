from typing import List, Dict, Optional
from framework.models.disk_models import DiskSelection, ClusterDisks
from framework.models.pool_models import PoolConfig
from .base import DiskSelectionStrategy


class AutoConfigureStrategy(DiskSelectionStrategy):
    def select_disks(self, free_disks: list, disks_info: dict, pool_config) -> dict:
        if pool_config.perfomance_type == 0:
            main_disks = [disk for disk in free_disks
                          if disks_info[disk]['type'] == 'SSD'][:pool_config.mainDisksCount]
        else:
            main_disks = [disk for disk in free_disks
                          if disks_info[disk]['type'] == pool_config.mainDisksType][:pool_config.mainDisksCount]

        remaining_disks = [d for d in free_disks if d not in main_disks]
        cache_disks = [d for d in remaining_disks if disks_info[d]['type'] == 'SSD']

        return {
            'main_disks': main_disks,
            'cache_disks': cache_disks[:pool_config.wrCacheDiskCount] if hasattr(pool_config,
                                                                                 'wrCacheDiskCount') else []
        }

    def _select_main_disks(
            self,
            available_disks: Dict[str, dict],
            count: int,
            disk_type: str
    ) -> List[dict]:
        filtered_disks = [
            disk for disk in available_disks.values()
            if disk['type'] == disk_type
        ]
        return filtered_disks[:count]

    def _select_cache_disks(
            self,
            available_disks: Dict[str, dict],
            count: int,
            used_disks: set
    ) -> List[dict]:
        if not count:
            return []

        filtered_disks = [
            disk for disk in available_disks.values()
            if disk['name'] not in used_disks and
               disk['type'] == "SSD" and
               disk['used_as_wc'] == 0
        ]
        return filtered_disks[:count]

    def _select_spare_disks(
            self,
            available_disks: Dict[str, dict],
            count: int,
            main_disk: Optional[dict],
            used_disks: set
    ) -> List[dict]:
        if not count or not main_disk:
            return []

        filtered_disks = [
            disk for disk in available_disks.values()
            if disk['name'] not in used_disks and
               disk['type'] == main_disk['type'] and
               disk['size'] == main_disk['size']
        ]
        return filtered_disks[:count]
