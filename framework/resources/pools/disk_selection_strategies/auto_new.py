from typing import Set, Dict, List
from .base import DiskSelectionStrategy
from framework.models.pool_models import PoolConfig
from framework.models.disk_models import ClusterDisksInfo, DiskSelection

class ManualSelectionStrategy(DiskSelectionStrategy):
    def select_disks(self, cluster_info: ClusterDisksInfo, pool_config: PoolConfig) -> DiskSelection:
        used_disks: Set[str] = set()

        main_disks = self._select_disk_group(
            cluster_info.free_disks_by_size_and_type,
            pool_config.main_disks_count,
            used_disks,
            pool_config.main_disks_type,
            pool_config.main_disks_size,
            "SSD" if pool_config.performance_type == 0 else None
        )
        used_disks.update(main_disks)

        wrc_disks = self._select_disk_group(
            cluster_info.free_disks_by_size_and_type,
            pool_config.wr_cache_disk_count,
            used_disks,
            pool_config.wrc_disk_type,
            pool_config.wrc_disk_size
        )
        used_disks.update(wrc_disks)

        rdc_disks = self._select_disk_group(
            cluster_info.free_disks_by_size_and_type,
            pool_config.rd_cache_disk_count,
            used_disks,
            pool_config.rdc_disk_type,
            pool_config.rdc_disk_size
        )
        used_disks.update(rdc_disks)

        spare_disks = self._select_disk_group(
            cluster_info.free_disks_by_size_and_type,
            pool_config.spare_cache_disk_count,
            used_disks,
            pool_config.spare_disk_type,
            pool_config.spare_disk_size
        )

        return DiskSelection(
            main_disks=main_disks,
            wrc_disks=wrc_disks,
            rdc_disks=rdc_disks,
            spare_disks=spare_disks
        )

    def _select_disk_group(
        self,
        disks_by_size_and_type: Dict[int, Dict[str, List[str]]],
        count: int,
        used_disks: Set[str],
        disk_type: str = None,
        disk_size: int = None,
        priority_type: str = None
    ) -> List[str]:
        if not count:
            return []

        filtered_groups = self._filter_disk_groups(
            disks_by_size_and_type,
            disk_type,
            disk_size,
            priority_type
        )

        selected_disks = []
        for size, types in filtered_groups.items():
            for type_, disks in types.items():
                available = [d for d in disks if d not in used_disks]
                if len(available) >= count:
                    selected_disks = available[:count]
                    return selected_disks

        if not selected_disks:
            raise ValueError(f"Not enough disks matching criteria. Required: {count}")

        return selected_disks

    def _filter_disk_groups(
        self,
        disks_by_size_and_type: Dict[int, Dict[str, List[str]]],
        disk_type: str,
        disk_size: int,
        priority_type: str
    ) -> Dict[int, Dict[str, List[str]]]:
        filtered = {}

        for size, types in disks_by_size_and_type.items():
            if disk_size and size != disk_size:
                continue

            filtered_types = {}
            for type_, disks in types.items():
                if disk_type and type_ != disk_type:
                    continue
                if priority_type and type_ != priority_type:
                    continue
                filtered_types[type_] = disks

            if filtered_types:
                filtered[size] = filtered_types

        return filtered
