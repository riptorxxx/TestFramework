from typing import List, Dict, Union, Optional
from framework.models.disk_models import DiskSelection, ClusterDisks
from framework.models.pool_models import PoolConfig
from .base import DiskSelectionStrategy


class ManualConfigureStrategy(DiskSelectionStrategy):
    def select_disks(self, free_disks: list, disks_info: dict, pool_config) -> dict:
        main_count = pool_config.mainDisks if isinstance(pool_config.mainDisks, int) else len(pool_config.mainDisks)
        main_disks = free_disks[:main_count]

        remaining_disks = [d for d in free_disks if d not in main_disks]
        cache_disks = [d for d in remaining_disks if disks_info[d]['type'] == 'SSD']

        return {
            'main_disks': main_disks,
            'cache_disks': cache_disks[:pool_config.wrcDisks] if pool_config.wrcDisks else []
        }
    # def select_disks(self, cluster_info: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
    #     available_disks = cluster_info.available_disks
    #     disk_type = "SSD" if pool_config.perfomance_type == 0 else None
    #
    #     main_disks = self._select_main_disks(
    #         available_disks,
    #         pool_config.mainDisks,
    #         disk_type
    #     )
    #     used_disks = set(d['name'] for d in main_disks)
    #
    #     wrc_disks = self._select_cache_disks(
    #         available_disks,
    #         pool_config.wrcDisks,
    #         used_disks
    #     )
    #     used_disks.update(d['name'] for d in wrc_disks)
    #
    #     rdc_disks = self._select_cache_disks(
    #         available_disks,
    #         pool_config.rdcDisks,
    #         used_disks
    #     )
    #     used_disks.update(d['name'] for d in rdc_disks)
    #
    #     spare_disks = self._select_spare_disks(
    #         available_disks,
    #         pool_config.spareDisks,
    #         main_disks[0] if main_disks else None,
    #         used_disks
    #     )
    #
    #     return DiskSelection(
    #         main_disks=main_disks,
    #         wrc_disks=wrc_disks,
    #         rdc_disks=rdc_disks,
    #         spare_disks=spare_disks
    #     )

    def _select_main_disks(
            self,
            available_disks: Dict[str, dict],
            disk_count: Union[int, List[str]],
            disk_type: str
    ) -> List[dict]:
        count = len(disk_count) if isinstance(disk_count, list) else disk_count
        filtered_disks = [
            disk for disk in available_disks.values()
            if disk_type is None or disk['type'] == disk_type
        ]
        return filtered_disks[:count]

    def _select_cache_disks(
            self,
            available_disks: Dict[str, dict],
            disk_count: Union[int, List[str]],
            used_disks: set
    ) -> List[dict]:
        if not disk_count:
            return []

        count = len(disk_count) if isinstance(disk_count, list) else disk_count
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
            disk_count: Union[int, List[str]],
            main_disk: Optional[dict],
            used_disks: set
    ) -> List[dict]:
        if not disk_count or not main_disk:
            return []

        count = len(disk_count) if isinstance(disk_count, list) else disk_count
        filtered_disks = [
            disk for disk in available_disks.values()
            if disk['name'] not in used_disks and
               disk['type'] == main_disk['type'] and
               disk['size'] == main_disk['size']
        ]
        return filtered_disks[:count]
