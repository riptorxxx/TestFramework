from abc import ABC, abstractmethod
from typing import Dict, Set, Optional, List
from framework.models.disk_models import DiskSelection, ClusterDisks, DiskType
from framework.models.pool_models import PoolConfig
from framework.core.logger import logger
from threading import Lock


class DiskSelectionStrategy(ABC):
    def __init__(self, disk_selector):
        self._disk_selector = disk_selector
        self._pool_config = None
        self._used_disks = set()
        self._lock = Lock()

    def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
        self._pool_config = pool_config
        cluster_disks = self._create_cluster_disks(cluster_data)
        selection = self._select_disks_impl(cluster_disks, pool_config)
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
        return ClusterDisks(
            disks_info=cluster_data['disks_info'],
            free_disks=cluster_data['free_disks'],
            free_for_wc=cluster_data['free_for_wc'],
            free_disks_by_size_and_type=cluster_data['free_disks_by_size_and_type']
        )

    def _determine_priority_type(self) -> Optional[DiskType]:
        return DiskType.SSD if self._pool_config.perfomance_type == 0 else None

    def _log_selection_results(self, selection: DiskSelection) -> None:
        logger.info(
            f"Selected disks configuration:\n"
            f"Main disks: {selection.main_disks}\n"
            f"WRC disks: {selection.wrc_disks}\n"
            f"RDC disks: {selection.rdc_disks}\n"
            f"Spare disks: {selection.spare_disks}"
        )

# from abc import ABC, abstractmethod
# from typing import Dict, Set, Optional
# from framework.models.disk_models import DiskSelection, ClusterDisks, DiskType
# from framework.models.pool_models import PoolConfig
# from framework.core.logger import logger
# from threading import Lock
#
#
# class DiskSelectionStrategy(ABC):
#     """Базовая стратегия выбора дисков"""
#
#     def __init__(self):
#         self._used_disks = set()
#         self._lock = Lock()
#
#     def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
#         """Основной метод выбора дисков"""
#         cluster_disks = ClusterDisks(
#             disks_info=cluster_data['disks_info'],
#             free_disks=cluster_data['free_disks'],
#             free_for_wc=cluster_data['free_for_wc'],
#             free_disks_by_size_and_type=cluster_data['free_disks_by_size_and_type']
#         )
#
#         with self._lock:
#             selection = self._select_disks_impl(cluster_disks, pool_config)
#             self._log_selection_results(selection)
#             return selection.to_dict()
#
#     @abstractmethod
#     def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
#         """Реализация конкретной стратегии выбора"""
#         pass
#
#     def _select_disk_group(self, cluster_disks: ClusterDisks, count: int,
#                            disk_type: DiskType = None, disk_size: int = None,
#                            source: str = 'all') -> Dict[str, Set[str]]:
#         """Универсальный метод выбора группы дисков"""
#         # Выбор источника дисков
#         disk_pool = cluster_disks.free_for_wc if source == 'wrc' else cluster_disks.free_disks
#
#         # Фильтрация по параметрам
#         available_disks = {
#             (size, type_): [d for d in disks
#                             if d not in self._used_disks and d in disk_pool]
#             for (size, type_), disks in cluster_disks.free_disks_by_size_and_type.items()
#             if (not disk_type or type_ == disk_type) and
#                (not disk_size or size == disk_size)
#         }
#
#         if not available_disks:
#             raise ValueError(f"No disks match criteria: type={disk_type}, size={disk_size}")
#
#         # Выбор оптимальной группы
#         for (size, type_), disks in sorted(available_disks.items()):
#             if len(disks) >= count:
#                 return {
#                     'disks': set(disks[:count]),
#                     'size': size,
#                     'type': type_
#                 }
#
#         raise ValueError(f"Insufficient disks. Required: {count}")


#____________________________________________________________________________________________
# from abc import ABC, abstractmethod
# from typing import Tuple, Dict, Set, Optional
# from framework.models.disk_models import DiskSelection, ClusterDisks, DiskType
# from framework.models.pool_models import PoolConfig
# from framework.core.logger import logger
# from threading import Lock
#
#
# class DiskSelectionStrategy(ABC):
#     """Base strategy for disk selection operations"""
#
#     def __init__(self, disk_selector):
#         self._disk_selector = disk_selector
#         # Множество для отслеживания используемых дисков
#         self._used_disks = set()
#         # Создание блокировки для потокобезопасности
#         self._lock = Lock()
#
#     def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
#         """
#         Main disk selection method
#
#         Args:
#             cluster_data: Raw cluster data
#             pool_config: Pool configuration
#
#         Returns:
#             dict: Selected disks configuration
#         """
#         logger.debug(f"Starting disk selection with data: {cluster_data}")
#
#         # Create ClusterDisks instance
#         cluster_disks = ClusterDisks(
#             disks_info=cluster_data['disks_info'],
#             free_disks=cluster_data['free_disks'],
#             free_for_wc=cluster_data['free_for_wc'],
#             free_disks_by_size_and_type=cluster_data['free_disks_by_size_and_type']
#         )
#
#         # Set priority type based on performance
#         pool_config.priority_type = DiskType.SSD if pool_config.perfomance_type == 0 else DiskType.HDD
#
#         # Execute specific strategy implementation
#         selection = self._select_disks_impl(cluster_disks, pool_config)
#
#         logger.info(
#             f"Selected disks configuration:\n"
#             f"Main disks: {selection.main_disks}\n"
#             f"WRC disks: {selection.wrc_disks}\n"
#             f"RDC disks: {selection.rdc_disks}\n"
#             f"Spare disks: {selection.spare_disks}"
#         )
#
#         return selection.to_dict()
#
#     @abstractmethod
#     def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
#         """
#         Abstract method for specific disk selection implementation
#
#         Example implementation in AutoDiskStrategy:
#         def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
#             selection = DiskSelection()
#
#             # Select main disks
#             main_group = self._select_optimal_group(
#                 cluster_disks,
#                 pool_config.mainDisksCount,
#                 pool_config.mainDisksType,
#                 pool_config.mainDisksSize
#             )
#             selection.main_disks = main_group['disks']
#
#             # Update pool config sizes and return selection
#             return selection
#         """
#         pass
#
#     def _process_main_and_spare_disks(self, cluster_disks: ClusterDisks,
#                                       disk_type: DiskType, count: int,
#                                       disk_size: Optional[int] = None) -> Dict[str, Set[str]]:
#         # Filter out used disks from cluster_disks
#         available_disks = {
#             (size, type_): [disk for disk in disks if disk not in self._used_disks]
#             for (size, type_), disks in cluster_disks.free_disks_by_size_and_type.items()
#         }
#
#         # Create new ClusterDisks instance with filtered disks
#         filtered_cluster_disks = ClusterDisks(
#             disks_info=cluster_disks.disks_info,
#             free_disks=cluster_disks.free_disks,
#             free_for_wc=cluster_disks.free_for_wc,
#             free_disks_by_size_and_type=available_disks
#         )
#
#         disk_group = self._select_optimal_group(
#             filtered_cluster_disks,
#             count,
#             disk_type,
#             disk_size
#         )
#
#         return {
#             'disks': set(disk_group['disks']),
#             'size': disk_group['size'],
#             'type': disk_group['type']
#         }
#
#     def _process_cache_disks(self, cluster_disks: ClusterDisks,
#                              disk_type: DiskType, count: int) -> Dict[str, Set[str]]:
#         available_disks = {
#             (size, type_): [disk for disk in disks
#                             if disk not in self._used_disks and disk in cluster_disks.free_for_wc]
#             for (size, type_), disks in cluster_disks.free_disks_by_size_and_type.items()
#         }
#
#         filtered_cluster_disks = ClusterDisks(
#             disks_info=cluster_disks.disks_info,
#             free_disks=cluster_disks.free_disks,
#             free_for_wc=cluster_disks.free_for_wc,
#             free_disks_by_size_and_type=available_disks
#         )
#
#         disk_group = self._select_optimal_group(
#             filtered_cluster_disks,
#             count,
#             disk_type
#         )
#
#         return {
#             'disks': set(disk_group['disks']),
#             'size': disk_group['size'],
#             'type': disk_group['type']
#         }
#
#     def _select_optimal_group(self, cluster_disks: ClusterDisks, count: int,
#                               disk_type: DiskType = None, disk_size: int = None) -> Dict:
#         """Select optimal disk group based on requirements"""
#         available_groups = {}
#
#         for (size, type_), disks in cluster_disks.free_disks_by_size_and_type.items():
#             if disk_type and type_ != disk_type:
#                 continue
#             if disk_size and size != disk_size:
#                 continue
#             available_groups[(size, type_)] = disks
#
#         if not available_groups:
#             raise ValueError(f"No disks match criteria: type={disk_type}, size={disk_size}")
#
#         sorted_groups = sorted(available_groups.items(), key=lambda x: x[0][0])
#
#         for (size, type_), disks in sorted_groups:
#             if len(disks) >= count:
#                 return {
#                     'disks': disks[:count],
#                     'size': size,
#                     'type': type_
#                 }
#
#         raise ValueError(f"Insufficient disks. Required: {count}")
#
#     def _validate_disk_count(self, count: int, min_required: int, disk_type: str):
#         """Validate minimum disk count requirements"""
#         if 0 < count < min_required:
#             raise ValueError(
#                 f"The number of {disk_type} disks must be at least {min_required}, received {count}"
#             )
#
#     def _log_selection_results(self, selection: DiskSelection) -> None:
#         logger.debug(
#             f"Selected disks for pool:\n"
#             f"Main disks: {selection.main_disks}\n"
#             f"Spare disks: {selection.spare_disks}\n"
#             f"WRC disks: {selection.wrc_disks}\n"
#             f"RDC disks: {selection.rdc_disks}\n"
#             f"Total used disks: {self._used_disks}"
#         )
#
#     def _clear_used_disks(self) -> None:
#         """Очистка множества использованных дисков"""
#         with self._lock:
#             self._used_disks.clear()
#


# from abc import ABC, abstractmethod
# from framework.models.disk_models import DiskSelection, DiskRequirements, ClusterDisks, DiskType
# from framework.models.pool_models import PoolConfig
# from framework.core.logger import logger
#
#
# class DiskSelectionStrategy(ABC):
#     def __init__(self, disk_selector):
#         # self.requirements = DiskRequirements()
#         self._disk_selector = disk_selector
#
#     def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
#         logger.debug(f"Disks info: {cluster_data}")
#         cluster_disks = ClusterDisks(
#             disks_info=cluster_data['disks_info'],
#             free_disks=cluster_data['free_disks'],
#             free_for_wc=cluster_data['free_for_wc'],
#             free_disks_by_size_and_type=cluster_data['free_disks_by_size_and_type']
#         )
#         logger.debug(f"Starting disk selection with free_disks: {cluster_disks.free_disks}")
#         logger.debug(f"Created ClusterDisks with free_for_wc: {cluster_disks.free_for_wc}")
#
#         pool_config.priority_type = DiskType.SSD if pool_config.perfomance_type == 0 else DiskType.HDD
#         selection, sizes = self._select_disks_impl(cluster_disks, pool_config)
#
#         # Важно: обновляем размеры в конфигурации пула
#         self._update_pool_config_sizes(pool_config, sizes)
#
#         logger.info(
#             f"Selected disks:\n"
#             f"main={selection.main_disks} (type={pool_config.mainDisksType}, size={sizes.get('main')})\n"
#             f"wrc={selection.wrc_disks} (type={pool_config.wrcDiskType}, size={sizes.get('wrc')})\n"
#             f"rdc={selection.rdc_disks} (type={pool_config.rdcDiskType}, size={sizes.get('rdc')})\n"
#             f"spare={selection.spare_disks} (type={pool_config.spareDiskType}, size={sizes.get('spare')})"
#         )
#
#         return selection.to_dict()
#         # return {
#         #     'mainDisks': selection.main_disks,
#         #     'wrcDisks': selection.wrc_disks,
#         #     'rdcDisks': selection.rdc_disks,
#         #     'spareDisks': selection.spare_disks
#         # }
#
#     def _update_pool_config_sizes(self, pool_config: PoolConfig, sizes: dict):
#         if not pool_config.mainDisksSize and 'main' in sizes:
#             pool_config.mainDisksSize = sizes['main']
#         if not pool_config.wrcDiskSize and 'wrc' in sizes:
#             pool_config.wrcDiskSize = sizes['wrc']
#         if not pool_config.rdcDiskSize and 'rdc' in sizes:
#             pool_config.rdcDiskSize = sizes['rdc']
#         if not pool_config.spareDiskSize and 'spare' in sizes:
#             pool_config.spareDiskSize = sizes['spare']
#
#     @abstractmethod
#     def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
#         pass
#
#     def _validate_disk_count(self, count: int, min_required: int, disk_type: str):
#         if 0 < count < min_required:
#             raise ValueError(
#                 f"The number of {disk_type} disks must be at least {min_required}, received {count}"
#             )
#
#
# # Импорты определяют зависимости класса
# from abc import ABC, abstractmethod
# from framework.models.disk_models import DiskSelection, DiskRequirements, ClusterDisks, DiskType
# from framework.models.pool_models import PoolConfig
# from framework.core.logger import logger
#
#
# class DiskSelectionStrategy(ABC):
#     def __init__(self, disk_selector):
#         # Инициализация с внедрением зависимости disk_selector
#         self._disk_selector = disk_selector
#
#     def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
#         # Логирование входных данных
#         logger.debug(f"Disks info: {cluster_data}")
#
#         # Создание объекта ClusterDisks из сырых данных кластера
#         cluster_disks = ClusterDisks(
#             disks_info=cluster_data['disks_info'],  # Информация о всех дисках
#             free_disks=cluster_data['free_disks'],  # Список свободных дисков
#             free_for_wc=cluster_data['free_for_wc'],  # Диски доступные для write cache
#             free_disks_by_size_and_type=cluster_data['free_disks_by_size_and_type']  # Сгруппированные диски
#         )
#
#         # Логирование созданного объекта
#         logger.debug(f"Starting disk selection with free_disks: {cluster_disks.free_disks}")
#         logger.debug(f"Created ClusterDisks with free_for_wc: {cluster_disks.free_for_wc}")
#
#         # Определение приоритетного типа дисков на основе производительности
#         pool_config.priority_type = DiskType.SSD if pool_config.perfomance_type == 0 else DiskType.HDD
#
#         # Вызов реализации конкретной стратегии
#         selection, sizes = self._select_disks_impl(cluster_disks, pool_config)
#
#         # Обновление размеров в конфигурации пула
#         self._update_pool_config_sizes(pool_config, sizes)
#
#         # Логирование результатов выбора
#         logger.info(
#             f"Selected disks:\n"
#             f"main={selection.main_disks} (type={pool_config.mainDisksType}, size={sizes.get('main')})\n"
#             f"wrc={selection.wrc_disks} (type={pool_config.wrcDiskType}, size={sizes.get('wrc')})\n"
#             f"rdc={selection.rdc_disks} (type={pool_config.rdcDiskType}, size={sizes.get('rdc')})\n"
#             f"spare={selection.spare_disks} (type={pool_config.spareDiskType}, size={sizes.get('spare')})"
#         )
#
#         # Возврат результата в виде словаря
#         return selection.to_dict()
#
#     def _update_pool_config_sizes(self, pool_config: PoolConfig, sizes: dict):
#         # Обновление размеров дисков в конфигурации пула, если они не были заданы
#         if not pool_config.mainDisksSize and 'main' in sizes:
#             pool_config.mainDisksSize = sizes['main']
#         if not pool_config.wrcDiskSize and 'wrc' in sizes:
#             pool_config.wrcDiskSize = sizes['wrc']
#         if not pool_config.rdcDiskSize and 'rdc' in sizes:
#             pool_config.rdcDiskSize = sizes['rdc']
#         if not pool_config.spareDiskSize and 'spare' in sizes:
#             pool_config.spareDiskSize = sizes['spare']
#
#     @abstractmethod
#     def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
#         # Абстрактный метод для реализации конкретной стратегии выбора дисков
#         pass
#
#     def _validate_disk_count(self, count: int, min_required: int, disk_type: str):
#         # Валидация количества дисков
#         if 0 < count < min_required:
#             raise ValueError(
#                 f"The number of {disk_type} disks must be at least {min_required}, received {count}"
#             )