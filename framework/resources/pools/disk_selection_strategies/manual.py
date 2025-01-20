from typing import List, Set
from .base import DiskSelectionStrategy
from framework.models.pool_models import PoolConfig
from framework.models.disk_models import ClusterDisks, DiskInfo, DiskSelection

class ManualSelectionStrategy(DiskSelectionStrategy):
    def select_disks(self, cluster_info: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
        used_disks: Set[str] = set()

        main_disks = [
            cluster_info.disks[disk_id]
            for disk_id in self._select_disk_group(
                cluster_info,
                pool_config.main_disks_count,
                used_disks,
                pool_config.main_disks_type,
                pool_config.main_disks_size
            )
        ]
        used_disks.update(disk.name for disk in main_disks)

        wrc_disks = [
            cluster_info.disks[disk_id]
            for disk_id in self._select_disk_group(
                cluster_info,
                pool_config.wr_cache_disk_count,
                used_disks,
                pool_config.wrc_disk_type,
                pool_config.wrc_disk_size
            )
        ] if pool_config.wr_cache_disk_count else None
        if wrc_disks:
            used_disks.update(disk.name for disk in wrc_disks)

        rdc_disks = [
            cluster_info.disks[disk_id]
            for disk_id in self._select_disk_group(
                cluster_info,
                pool_config.rd_cache_disk_count,
                used_disks,
                pool_config.rdc_disk_type,
                pool_config.rdc_disk_size
            )
        ] if pool_config.rd_cache_disk_count else None
        if rdc_disks:
            used_disks.update(disk.name for disk in rdc_disks)

        spare_disks = [
            cluster_info.disks[disk_id]
            for disk_id in self._select_disk_group(
                cluster_info,
                pool_config.spare_cache_disk_count,
                used_disks,
                pool_config.spare_disk_type,
                pool_config.spare_disk_size
            )
        ] if pool_config.spare_cache_disk_count else None

        return DiskSelection(
            main_disks=main_disks,
            wrc_disks=wrc_disks,
            rdc_disks=rdc_disks,
            spare_disks=spare_disks
        )

    def _select_disk_group(
        self,
        cluster_info: ClusterDisks,
        count: int,
        used_disks: Set[str],
        disk_type: str = None,
        disk_size: int = None
    ) -> List[str]:
        if not count:
            return []

        available = [
            disk for disk in cluster_info.available_disks
            if disk.name not in used_disks and
            (not disk_type or disk.type == disk_type) and
            (not disk_size or disk.size == disk_size)
        ]

        if len(available) < count:
            raise ValueError(f"Not enough disks matching criteria. Required: {count}")

        return [disk.name for disk in available[:count]]
