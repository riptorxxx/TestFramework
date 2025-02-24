from abc import ABC, abstractmethod
from typing import Dict, Set, Optional, List, Union
from framework.models.disk_models import DiskSelection, ClusterDisks, DiskType
from framework.models.pool_models import PoolConfig, PoolData
from framework.core.logger import logger
from threading import Lock


class DiskSelectionStrategy(ABC):
    def __init__(self, disk_selector):
        self._disk_selector = disk_selector
        self._pool_config = None
        self._used_disks = set()
        self._lock = Lock()

    def select_disks(self, cluster_data: dict, config: Union[PoolConfig, PoolData]) -> dict:
        """Base method for disk selection"""
        cluster_disks = self._create_cluster_disks(cluster_data)
        # Сохраняем конфигурацию только если это PoolConfig (чтобы auto и manual использовали PoolConfig)
        if isinstance(config, PoolConfig):
            self._pool_config = config
        selection = self._select_disks_impl(cluster_disks, config)
        self._log_selection_results(selection)
        return selection.to_dict()

    @abstractmethod
    def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
        pass

    def _select_disk_group(self, cluster_disks: ClusterDisks, count: int,
                           disk_type: Optional[DiskType] = None,
                           disk_size: Optional[int] = None,
                           for_cache: bool = False,
                           ) -> Dict[str, Set[str]]:

        # Force SSD type if performance_type is 0
        priority_type = self._determine_priority_type()
        if priority_type == DiskType.SSD:
            disk_type = DiskType.SSD

        if for_cache:
            available_disks = self._filter_wrc_disks(cluster_disks, disk_type, disk_size)
        else:
            available_disks = self._filter_available_disks(cluster_disks, disk_type, disk_size, for_cache)

        if not available_disks:
            raise ValueError(f"No disks match criteria: type={disk_type}, size={disk_size}")

        selected_group = self._select_optimal_group(available_disks, count)

        return selected_group

    def _filter_wrc_disks(self, cluster_disks: ClusterDisks,
                          disk_type: Optional[DiskType],
                          disk_size: Optional[int]) -> Dict:
        filtered = {}
        for disk_id in cluster_disks.free_for_wc:
            if disk_id in self._used_disks:
                continue

            disk_info = cluster_disks.disks_info[disk_id]
            if disk_info['type'] != DiskType.SSD:
                continue

            if disk_size and disk_info['size'] != disk_size:
                continue

            size = disk_info['size']
            filtered.setdefault((size, DiskType.SSD), []).append(disk_id)

        return filtered

    def _filter_available_disks(self, cluster_disks: ClusterDisks,
                                disk_type: Optional[DiskType],
                                disk_size: Optional[int],
                                for_cache: bool) -> Dict:
        filtered = {}
        for (size, type_), disks in cluster_disks.free_disks_by_size_and_type.items():
            if self._matches_criteria(size, type_, disk_size, disk_type, disks, for_cache):
                filtered[(size, type_)] = [d for d in disks if d not in self._used_disks]
        return filtered

    def _matches_criteria(self, size: int, type_: str,
                          required_size: Optional[int],
                          required_type: Optional[DiskType],
                          disks: List[str],
                          for_cache: bool) -> bool:
        if required_size and size != required_size:
            return False
        if required_type and type_ != required_type:
            return False
        if for_cache and type_ != DiskType.SSD:
            return False
        return True

    def _select_optimal_group(self, available_groups: Dict, count: int) -> Dict:
        for (size, type_), disks in sorted(available_groups.items()):
            if len(disks) >= count:
                return {
                    'disks': set(disks[:count]),
                    'size': size,
                    'type': type_
                }
        raise ValueError(f"Insufficient disks. Required: {count}")

    def _create_cluster_disks(self, cluster_data: dict) -> ClusterDisks:
        logger.info(f"Received cluster_data: {cluster_data}")
        return ClusterDisks(
            disks_info=cluster_data['disks_info'],
            free_disks=cluster_data['free_disks'],
            free_for_wc=cluster_data['free_for_wc'],
            free_disks_by_size_and_type=cluster_data['free_disks_by_size_and_type']
        )

    def _determine_priority_type(self) -> Optional[DiskType]:
        # Проверяем отсутствие pool_config, что бы expand не проверял на perfomance==0
        if not self._pool_config:
            return None
        return DiskType.SSD if self._pool_config.perfomance_type == 0 else None

    def _log_selection_results(self, selection: DiskSelection) -> None:
        logger.info(
            f"Selected disks configuration:\n"
            f"Main disks: {selection.main_disks}\n"
            f"WRC disks: {selection.wrc_disks}\n"
            f"RDC disks: {selection.rdc_disks}\n"
            f"Spare disks: {selection.spare_disks}"
        )

