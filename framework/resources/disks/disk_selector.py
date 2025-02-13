from typing import Dict, List, Set, Type, Optional
from framework.models.pool_models import PoolConfig
from framework.models.disk_models import DiskType, DiskSelection, ClusterDisks
from framework.core.logger import logger
from ..pools.disk_selection_strategies.base import DiskSelectionStrategy
from ..pools.disk_selection_strategies.auto import AutoConfigureStrategy
from ..pools.disk_selection_strategies.manual import ManualConfigureStrategy

class DiskSelector:
    def __init__(self, disk_tools):
        self._disk_tools = disk_tools
        self._strategies: Dict[str, Type[DiskSelectionStrategy]] = {
            'auto': AutoConfigureStrategy,
            'manual': ManualConfigureStrategy
        }
        logger.debug(f"DiskSelector initialized with disk_tools: {disk_tools}")

    def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
        strategy_type = 'auto' if pool_config.auto_configure else 'manual'
        strategy = self._strategies[strategy_type](self)
        return strategy.select_disks(cluster_data, pool_config)

    def register_strategy(self, name: str, strategy_class: Type[DiskSelectionStrategy]):
        if name in self._strategies:
            raise ValueError(f"Strategy {name} already registered")
        self._strategies[name] = strategy_class
        logger.info(f"Registered new disk selection strategy: {name}")





# '''
# Принимает сырые данные о кластере
# Извлекает и структурирует информацию о дисках
# Создает объект ClusterDisks с категоризированными дисками:
#  -free_disks
#  -free_for_wc
#  -free_disks_by_size_and_type
# Предоставляет базовые методы фильтрации дисков
# отвечает на вопрос: "ЧТО у нас есть?" (доступные диски)
# '''
# from typing import Dict, List, Set, Type, Optional
# from framework.models.pool_models import PoolConfig
# from framework.models.disk_models import DiskType, DiskSelection, ClusterDisks
# from framework.core.logger import logger
# from ..pools.disk_selection_strategies.base import DiskSelectionStrategy
# from ..pools.disk_selection_strategies.auto import AutoConfigureStrategy
# from ..pools.disk_selection_strategies.manual import ManualConfigureStrategy
#
#
# class DiskSelector:
#     def __init__(self, disk_tools):
#         self._disk_tools = disk_tools
#         self._strategies: Dict[str, Type[DiskSelectionStrategy]] = {
#             'auto': AutoConfigureStrategy,
#             'manual': ManualConfigureStrategy
#         }
#         logger.debug(f"DiskSelector initialized with disk_tools: {disk_tools}")
#
#     def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
#         """Main entry point for disk selection"""
#         strategy_type = 'auto' if pool_config.auto_configure else 'manual'
#         strategy = self._strategies[strategy_type](self)
#         return strategy.select_disks(cluster_data, pool_config)
#
#     def select_disks_by_type(self, cluster_disks: ClusterDisks, disk_type: str, count: int,
#                             used_disks: set, required_size: Optional[int] = None) -> tuple[List[str], Optional[int]]:
#         """Выбирает точное количество дисков, соответствующих бизнес-требованиям.
#
#         Это метод высокого уровня, который:
#         1. Обеспечивает выбор точного количества дисков.
#         2. Применяет правила приоритета типа диска.
#         3. Подтверждает выбор диска.
#         4. Возвращает оба выбранных диска и их размер.
#         """
#         main_result = self.select_main_disks(
#             cluster_disks,
#             count,
#             used_disks,
#             disk_type=disk_type,
#             disk_size=required_size
#         )
#         return main_result['disks'], main_result['size']
#
#     def select_main_disks(self, cluster_disks, count, used_disks, disk_type=None, disk_size=None, priority_type=None):
#         """Enhanced main disk selection with priority and fallback logic"""
#         if count == 0:
#             return {'disks': set(), 'size': None, 'type': None}
#
#         disks_by_size_and_type = cluster_disks.free_disks_by_size_and_type
#
#         # Priority handling
#         if priority_type == "SSD":
#             filtered_groups = {k: v for k, v in disks_by_size_and_type.items() if k[1] == "SSD"}
#         elif disk_type and disk_size:
#             filtered_groups = {k: v for k, v in disks_by_size_and_type.items()
#                                if k[1] == disk_type and k[0] == disk_size}
#         else:
#             # HDD fallback logic
#             hdd_groups = {k: v for k, v in disks_by_size_and_type.items() if k[1] == "HDD"}
#             if not any(len(set(disks) - used_disks) >= count for disks in hdd_groups.values()):
#                 ssd_groups = {k: v for k, v in disks_by_size_and_type.items() if k[1] == "SSD"}
#                 filtered_groups = {**hdd_groups, **ssd_groups}
#             else:
#                 filtered_groups = hdd_groups
#
#         # Group processing with size preservation
#         sorted_groups = []
#         for (size, disk_type), disks in filtered_groups.items():
#             available = set(disks) - used_disks
#             if available:
#                 sorted_groups.append(((size, disk_type), list(available)))
#
#         sorted_groups.sort(key=lambda x: len(x[1]), reverse=True)
#
#         for (size, disk_type), available in sorted_groups:
#             if len(available) >= count:
#                 selected = set(available[:count])
#                 return {'disks': selected, 'size': size, 'type': disk_type}
#
#         raise ValueError(f"Not enough identical disks for main group. Required: {count}")
#
#     # def select_main_disks(self, cluster_disks, count, used_disks, disk_type=None, disk_size=None, priority_type=None):
#     #     """Enhanced main disk selection with priority and fallback logic"""
#     #     logger.debug(
#     #         f"Selecting main disks: count={count}, type={disk_type}, size={disk_size}, priority={priority_type}")
#     #
#     #     if count == 0:
#     #         return {'disks': set(), 'size': None, 'type': None}
#     #
#     #     disks_by_size_and_type = cluster_disks.free_disks_by_size_and_type
#     #
#     #     if priority_type == "SSD":
#     #         filtered_groups = {k: v for k, v in disks_by_size_and_type.items() if k[1] == "SSD"}
#     #     elif disk_type and disk_size:
#     #         filtered_groups = {k: v for k, v in disks_by_size_and_type.items()
#     #                            if k[1] == disk_type and k[0] == disk_size}
#     #     else:
#     #         hdd_groups = {k: v for k, v in disks_by_size_and_type.items() if k[1] == "HDD"}
#     #         if not any(len(set(disks) - used_disks) >= count for disks in hdd_groups.values()):
#     #             ssd_groups = {k: v for k, v in disks_by_size_and_type.items() if k[1] == "SSD"}
#     #             filtered_groups = {**hdd_groups, **ssd_groups}
#     #         else:
#     #             filtered_groups = hdd_groups
#     #
#     #     sorted_groups = []
#     #     for (size, disk_type), disks in filtered_groups.items():
#     #         available = set(disks) - used_disks
#     #         if available:
#     #             sorted_groups.append(((size, disk_type), list(available)))
#     #
#     #     sorted_groups.sort(key=lambda x: len(x[1]), reverse=True)
#     #
#     #     for (size, disk_type), available in sorted_groups:
#     #         if len(available) >= count:
#     #             selected = set(available[:count])
#     #             return {'disks': selected, 'size': size, 'type': disk_type}
#     #
#     #     raise ValueError(f"Not enough identical disks for main group. Required: {count}")
#
#     # def select_write_cache_disks(self, cluster_disks, count, used_disks, disk_size=None):
#     #     """Enhanced write cache disk selection"""
#     #     logger.debug(f"Selecting write cache disks: count={count}, size={disk_size}")
#     #
#     #     if count == 0:
#     #         return set(), None
#     #
#     #     available_disks = {
#     #         disk for disk in cluster_disks.free_for_wc
#     #         if disk not in used_disks and
#     #            cluster_disks.disks_info[disk]['type'] == "SSD" and
#     #            (disk_size is None or cluster_disks.disks_info[disk]['size'] == disk_size)
#     #     }
#     #
#     #     if len(available_disks) < count:
#     #         raise ValueError(f"Not enough SSD disks for write cache. Required: {count}")
#     #
#     #     selected_disks = set(list(available_disks)[:count])
#     #     return selected_disks, cluster_disks.disks_info[list(selected_disks)[0]]['size']
#
#     def select_write_cache_disks(self, cluster_disks, count, used_disks, disk_size=None):
#         """Enhanced write cache disk selection"""
#         if count == 0:
#             return set(), None
#
#         # Group disks by size first
#         available_wrc_disks = {}
#         for disk in cluster_disks.free_for_wc:
#             if (disk not in used_disks and
#                     cluster_disks.disks_info[disk]['type'] == "SSD" and
#                     (disk_size is None or cluster_disks.disks_info[disk]['size'] == disk_size)):
#                 size = cluster_disks.disks_info[disk]['size']
#                 available_wrc_disks.setdefault(size, []).append(disk)
#
#         # Select from largest group
#         sorted_sizes = sorted(available_wrc_disks.items(), key=lambda x: len(x[1]), reverse=True)
#         for size, disks in sorted_sizes:
#             if len(disks) >= count:
#                 selected = set(disks[:count])
#                 return selected, size
#
#         raise ValueError(f"Not enough SSD disks for write cache. Required: {count}")
#
#     def select_read_cache_disks(self, cluster_disks, count, used_disks, disk_size=None):
#         """Select read cache disks prioritizing smaller sizes"""
#         if count == 0:
#             return set(), None
#
#         # Group SSD disks by size
#         size_groups = {}
#         for (size, type_), disks in cluster_disks.free_disks_by_size_and_type.items():
#             if type_ == "SSD":
#                 available = set(disks) - used_disks
#                 if available:
#                     size_groups[size] = available
#
#         # Sort sizes in ascending order (smaller first)
#         sorted_sizes = sorted(size_groups.items(), key=lambda x: x[0])
#
#         # Try to select from each size group
#         for size, disks in sorted_sizes:
#             if len(disks) >= count:
#                 selected_disks = set(list(disks)[:count])
#                 return selected_disks, size
#
#         raise ValueError(f"Not enough SSD disks for read cache. Required: {count}")
#
#     # def select_read_cache_disks(self, cluster_disks, count, used_disks, disk_size=None):
#     #     """Enhanced read cache disk selection"""
#     #     logger.debug(f"Selecting read cache disks: count={count}, size={disk_size}")
#     #
#     #     if count == 0:
#     #         return set(), None
#     #
#     #     available_disks = {
#     #         disk for disk in cluster_disks.free_disks
#     #         if disk not in used_disks and
#     #            cluster_disks.disks_info[disk]['type'] == "SSD" and
#     #            (disk_size is None or cluster_disks.disks_info[disk]['size'] == disk_size)
#     #     }
#     #
#     #     if len(available_disks) < count:
#     #         raise ValueError(f"Not enough SSD disks for read cache. Required: {count}")
#     #
#     #     selected_disks = set(list(available_disks)[:count])
#     #     return selected_disks, cluster_disks.disks_info[list(selected_disks)[0]]['size']
#
#     def select_spare_disks(self, cluster_disks, count, main_size, main_type, used_disks):
#         """Enhanced spare disk selection"""
#         logger.debug(f"Selecting spare disks: count={count}, size={main_size}, type={main_type}")
#
#         if count == 0:
#             return set()
#
#         key = (main_size, main_type)
#         if key not in cluster_disks.free_disks_by_size_and_type:
#             raise ValueError(f"Spare disks with size {main_size} and type {main_type} not found")
#
#         available = set(cluster_disks.free_disks_by_size_and_type[key]) - used_disks
#         if len(available) < count:
#             raise ValueError(f"Not enough spare disks matching main disks parameters. Required: {count}")
#
#         return set(list(available)[:count])
#
#
#
#     def _match_disk_parameters(self, disk: dict, reference: dict) -> bool:
#         return (disk['type'] == reference['type'] and
#                 disk['size'] == reference['size'])
#
#     def _validate_and_return(self, available_disks: List[str], count: int, disk_type: str
#                              ) -> List[str]:
#         if len(available_disks) < count:
#             raise ValueError(f"Not enough {disk_type}. Required: {count}")
#         return available_disks[:count]
#
#     def register_strategy(self, name: str, strategy_class: Type[DiskSelectionStrategy]):
#         """
#         Позволяет динамическую регистрацию новых стратегий выбора дисков (на будущее)
#         """
#         if name in self._strategies:
#             raise ValueError(f"Strategy {name} already registered")
#         self._strategies[name] = strategy_class
#         logger.info(f"Registered new disk selection strategy: {name}")
#
#
#
#
# #_____________________________________________________________________________________
#
#     # def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
#     #     strategy_type = 'auto' if pool_config.auto_configure else 'manual'
#     #     logger.debug(f"Creating {strategy_type} strategy for pool config: {pool_config}")
#     #
#     #     strategy = self._strategies[strategy_type](self)
#     #     logger.debug(f"Using strategy: {strategy.__class__.__name__}")
#     #
#     #     return strategy.select_disks(cluster_data, pool_config)
#     #
#     # def select_disks_by_type(
#     #         self,
#     #         cluster_disks: ClusterDisks,
#     #         disk_type: str,
#     #         count: int,
#     #         used_disks: set,
#     #         required_size: Optional[int] = None
#     # ) -> tuple[List[str], Optional[int]]:
#     #     logger.debug(f"Selecting {count} disks of type {disk_type} with required size: {required_size}")
#     #
#     #     available_disks = [
#     #         disk for disk in cluster_disks.free_disks
#     #         if disk not in used_disks and
#     #            cluster_disks.disks_info[disk]['type'] == disk_type and
#     #            (required_size is None or cluster_disks.disks_info[disk]['size'] == required_size)
#     #     ]
#     #
#     #     if required_size and not available_disks:
#     #         raise ValueError(f"No available disks of type {disk_type} with required size {required_size}")
#     #
#     #     selected_disks = self._validate_and_return(available_disks, count, f"{disk_type} disks")
#     #     if selected_disks:
#     #         return selected_disks, cluster_disks.disks_info[selected_disks[0]]['size']
#     #     return selected_disks, None
#     #
#     # def select_write_cache_disks(
#     #         self,
#     #         cluster_disks: ClusterDisks,
#     #         count: int,
#     #         used_disks: set
#     # ) -> tuple[List[str], Optional[int]]:
#     #     logger.debug(f"Selecting write cache disks")
#     #     available_disks = [
#     #         disk for disk in cluster_disks.free_for_wc
#     #         if disk not in used_disks and
#     #            cluster_disks.disks_info[disk]['type'] == "SSD"
#     #     ]
#     #     selected_disks = self._validate_and_return(available_disks, count, "write cache disks")
#     #     if selected_disks:
#     #         return selected_disks, cluster_disks.disks_info[selected_disks[0]]['size']
#     #     return selected_disks, None
#     #
#     # def select_read_cache_disks(
#     #         self,
#     #         cluster_disks: ClusterDisks,
#     #         count: int,
#     #         used_disks: set,
#     #         required_size: Optional[int] = None
#     # ) -> tuple[List[str], Optional[int]]:
#     #     logger.debug(f"Selecting read cache disks with required size: {required_size}")
#     #
#     #     available_disks = [
#     #         disk for disk in cluster_disks.free_disks
#     #         if disk not in used_disks and
#     #            cluster_disks.disks_info[disk]['type'] == "SSD" and
#     #            (required_size is None or cluster_disks.disks_info[disk]['size'] == required_size)
#     #     ]
#     #
#     #     if required_size and not available_disks:
#     #         raise ValueError(f"No available RDC disks with required size {required_size}")
#     #
#     #     selected_disks = self._validate_and_return(available_disks, count, "read cache disks")
#     #     if selected_disks:
#     #         return selected_disks, cluster_disks.disks_info[selected_disks[0]]['size']
#     #     return selected_disks, None
#     #
#     # def select_spare_disks(
#     #         self,
#     #         cluster_disks: ClusterDisks,
#     #         count: int,
#     #         used_disks: set,
#     #         required_size: Optional[int] = None,
#     #         disk_type: str = "SSD"
#     # ) -> tuple[List[str], Optional[int]]:
#     #     logger.debug(f"Selecting spare disks with required size: {required_size}")
#     #
#     #     available_disks = [
#     #         disk for disk in cluster_disks.free_disks
#     #         if disk not in used_disks and
#     #            cluster_disks.disks_info[disk]['type'] == disk_type and
#     #            (required_size is None or cluster_disks.disks_info[disk]['size'] == required_size)
#     #     ]
#     #
#     #     if required_size and not available_disks:
#     #         raise ValueError(f"No available spare disks with required size {required_size}")
#     #
#     #     selected_disks = self._validate_and_return(available_disks, count, "spare disks")
#     #     if selected_disks:
#     #         return selected_disks, cluster_disks.disks_info[selected_disks[0]]['size']
#     #     return selected_disks, None
#
#
#
#
# # from typing import Dict, Set
# # from dataclasses import dataclass
# # from framework.models.pool_models import PoolConfig
# # from framework.models.disk_models import DiskType
# # from framework.core.logger import logger
# #
# #
# # @dataclass
# # class DiskGroupRequirements:
# #     """Требования к группе дисков"""
# #     count: int
# #     disk_type: str = None
# #     disk_size: int = None
# #     priority_type: str = None
# #
# #
# # class DiskSelector:
# #     """Селектор дисков с улучшенной логикой выбора"""
# #
# #     MIN_MAIN_DISKS = 2
# #     MIN_CACHE_DISKS = 2
# #
# #     def __init__(self, disk_tools):
# #         self._disk_tools = disk_tools
# #         self._used_disks: Set[str] = set()
# #
# #     def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
# #         """Основной метод выбора дисков"""
# #         # Сброс использованных дисков перед новым выбором
# #         self._used_disks.clear()
# #
# #         # Получаем приоритетный тип диска на основе производительности
# #         priority_type = self._get_priority_disk_type(pool_config)
# #
# #         # Подготавливаем требования к дискам
# #         requirements = self._prepare_disk_requirements(pool_config, priority_type)
# #
# #         # Выбираем основные диски
# #         main_disks = self._select_main_disks(
# #             cluster_data,
# #             requirements.main,
# #             self._used_disks
# #         )
# #
# #         # Выбираем кэш-диски записи
# #         wrc_disks = self._select_cache_disks(
# #             cluster_data,
# #             requirements.wrc,
# #             self._used_disks,
# #             "write cache"
# #         )
# #
# #         # Выбираем кэш-диски чтения
# #         rdc_disks = self._select_cache_disks(
# #             cluster_data,
# #             requirements.rdc,
# #             self._used_disks,
# #             "read cache"
# #         )
# #
# #         # Выбираем запасные диски
# #         spare_disks = self._select_spare_disks(
# #             cluster_data,
# #             requirements.spare,
# #             main_disks[0] if main_disks else None,
# #             self._used_disks
# #         )
# #
# #         return {
# #             'main_disks': main_disks,
# #             'wrc_disks': wrc_disks,
# #             'rdc_disks': rdc_disks,
# #             'spare_disks': spare_disks
# #         }
# #
# #     def _get_priority_disk_type(self, pool_config: PoolConfig) -> str:
# #         """Определяет приоритетный тип дисков на основе типа производительности"""
# #         return DiskType.SSD if pool_config.perfomance_type == 0 else None
# #
# #     def _prepare_disk_requirements(self, pool_config: PoolConfig, priority_type: str) -> Dict[
# #         str, DiskGroupRequirements]:
# #         """Подготавливает требования к разным группам дисков"""
# #         if pool_config.auto_configure:
# #             return self._prepare_auto_requirements(pool_config, priority_type)
# #         return self._prepare_manual_requirements(pool_config, priority_type)
# #
# #     def _prepare_auto_requirements(self, pool_config: PoolConfig, priority_type: str) -> Dict[
# #         str, DiskGroupRequirements]:
# #         """Подготовка требований для автоматического режима"""
# #         return {
# #             'main': DiskGroupRequirements(
# #                 count=pool_config.mainDisksCount * pool_config.mainGroupsCount,
# #                 disk_type=priority_type or pool_config.mainDisksType,
# #                 disk_size=pool_config.mainDisksSize
# #             ),
# #             'wrc': DiskGroupRequirements(
# #                 count=pool_config.wrCacheDiskCount,
# #                 disk_type=DiskType.SSD,
# #                 disk_size=pool_config.wrcDiskSize
# #             ),
# #             'rdc': DiskGroupRequirements(
# #                 count=pool_config.rdCacheDiskCount,
# #                 disk_type=DiskType.SSD,
# #                 disk_size=pool_config.rdcDiskSize
# #             ),
# #             'spare': DiskGroupRequirements(
# #                 count=pool_config.spareCacheDiskCount,
# #                 disk_type=pool_config.spareDiskType,
# #                 disk_size=pool_config.spareDiskSize
# #             )
# #         }
# #
# #     def _prepare_manual_requirements(self, pool_config: PoolConfig, priority_type: str) -> Dict[
# #         str, DiskGroupRequirements]:
# #         """Подготовка требований для ручного режима"""
# #         return {
# #             'main': DiskGroupRequirements(
# #                 count=len(pool_config.mainDisks) if isinstance(pool_config.mainDisks, list) else pool_config.mainDisks,
# #                 disk_type=priority_type
# #             ),
# #             'wrc': DiskGroupRequirements(
# #                 count=len(pool_config.wrcDisks) if isinstance(pool_config.wrcDisks,
# #                                                               list) else pool_config.wrcDisks or 0,
# #                 disk_type=DiskType.SSD
# #             ),
# #             'rdc': DiskGroupRequirements(
# #                 count=len(pool_config.rdcDisks) if isinstance(pool_config.rdcDisks,
# #                                                               list) else pool_config.rdcDisks or 0,
# #                 disk_type=DiskType.SSD
# #             ),
# #             'spare': DiskGroupRequirements(
# #                 count=len(pool_config.spareDisks) if isinstance(pool_config.spareDisks,
# #                                                                 list) else pool_config.spareDisks or 0
# #             )
# #         }
# #
# #     def _select_main_disks(self, cluster_info: dict, requirements: DiskGroupRequirements, used_disks: Set[str]) -> list:
# #         """Выбор основных дисков с учетом требований"""
# #         # Получаем группы дисков по размеру и типу
# #         disk_groups = self._get_disk_groups(cluster_info['free_disks_by_size_and_type'])
# #
# #         # Фильтруем группы по требованиям
# #         filtered_groups = [
# #             (key, disks) for (key, disks) in disk_groups
# #             if (not requirements.disk_type or key[1] == requirements.disk_type) and
# #                (not requirements.disk_size or key[0] == requirements.disk_size) and
# #                len(set(disks) - used_disks) >= requirements.count
# #         ]
# #
# #         if not filtered_groups:
# #             raise ValueError(f"Недостаточно подходящих дисков для основной группы. Требуется: {requirements.count}")
# #
# #         # Выбираем первую подходящую группу
# #         selected_group = filtered_groups[0]
# #         available_disks = list(set(selected_group[1]) - used_disks)
# #         selected_disks = available_disks[:requirements.count]
# #
# #         # Обновляем множество использованных дисков
# #         used_disks.update(selected_disks)
# #
# #         return selected_disks
# #
# #     def _select_cache_disks(
# #             self,
# #             cluster_info: dict,
# #             requirements: DiskGroupRequirements,
# #             used_disks: Set[str],
# #             cache_type: str
# #     ) -> list:
# #         """Выбор кэш-дисков с учетом требований"""
# #         if requirements.count == 0:
# #             return []
# #
# #         # Проверяем минимальное количество дисков для кэша
# #         if 0 < requirements.count < self.MIN_CACHE_DISKS:
# #             raise ValueError(
# #                 f"Количество {cache_type} дисков должно быть не менее {self.MIN_CACHE_DISKS}"
# #             )
# #
# #         # Выбираем доступные диски в зависимости от типа кэша
# #         if cache_type == "write cache":
# #             available_disks = [
# #                 d for d in cluster_info['free_for_wc']
# #                 if d not in used_disks and
# #                    cluster_info['disks_info'][d]['type'] == DiskType.SSD
# #             ]
# #         else:
# #             available_disks = [
# #                 d for d in cluster_info['free_disks']
# #                 if d not in used_disks and
# #                    cluster_info['disks_info'][d]['type'] == DiskType.SSD
# #             ]
# #
# #         # Группируем диски по размеру
# #         disks_by_size = {}
# #         for disk in available_disks:
# #             size = cluster_info['disks_info'][disk]['size']
# #             disks_by_size.setdefault(size, []).append(disk)
# #
# #         # Выбираем группу с наибольшим количеством дисков
# #         sorted_groups = sorted(disks_by_size.items(), key=lambda x: len(x[1]), reverse=True)
# #
# #         for size, disks in sorted_groups:
# #             if len(disks) >= requirements.count:
# #                 selected_disks = disks[:requirements.count]
# #                 used_disks.update(selected_disks)
# #                 return selected_disks
# #
# #         raise ValueError(f"Недостаточно SSD дисков для {cache_type}. Требуется: {requirements.count}")
# #
# #     def _select_spare_disks(
# #             self,
# #             cluster_info: dict,
# #             requirements: DiskGroupRequirements,
# #             main_disk: str,
# #             used_disks: Set[str]
# #     ) -> list:
# #         """Выбор запасных дисков того же типа и размера, что и основные"""
# #         if requirements.count == 0 or not main_disk:
# #             return []
# #
# #         # Получаем параметры основного диска
# #         main_disk_info = cluster_info['disks_info'][main_disk]
# #         main_size = main_disk_info['size']
# #         main_type = main_disk_info['type']
# #
# #         # Ищем диски с теми же параметрами
# #         available_disks = [
# #             disk for disk in cluster_info['free_disks']
# #             if disk not in used_disks and
# #                cluster_info['disks_info'][disk]['size'] == main_size and
# #                cluster_info['disks_info'][disk]['type'] == main_type
# #         ]
# #
# #         if len(available_disks) < requirements.count:
# #             raise ValueError(
# #                 f"Недостаточно запасных дисков с размером {main_size} и типом {main_type}. "
# #                 f"Требуется: {requirements.count}"
# #             )
# #
# #         selected_disks = available_disks[:requirements.count]
# #         used_disks.update(selected_disks)
# #         return selected_disks
# #
# #     def _get_disk_groups(self, disks_by_size_and_type: dict) -> list:
# #         """Группировка доступных дисков по типу и размеру"""
# #         disk_groups = {}
# #
# #         for (size, dtype), disks in disks_by_size_and_type.items():
# #             key = (size, dtype)
# #             disk_groups[key] = list(disks)
# #
# #         # Сортируем группы по количеству дисков
# #         return sorted(
# #             disk_groups.items(),
# #             key=lambda x: len(x[1]),
# #             reverse=True
# #         )
#
# # from typing import Dict
# # from framework.models.pool_models import PoolConfig
# # from framework.models.disk_models import ClusterDisks, DiskSelection
# # from ..pools.disk_selection_strategies.base import DiskSelectionStrategy
# # from ..pools.disk_selection_strategies.auto import AutoConfigureStrategy
# # from ..pools.disk_selection_strategies.manual import ManualConfigureStrategy
# #
# #
# # class DiskSelector:
# #     """Disk selection orchestrator"""
# #
# #     def __init__(self, disk_tools):
# #         self._disk_tools = disk_tools
# #         self._strategies: Dict[str, DiskSelectionStrategy] = {
# #             'auto': AutoConfigureStrategy(),
# #             'manual': ManualConfigureStrategy()
# #         }
# #
# #     def select_disks(self, cluster_data: dict, pool_config) -> dict:
# #         # if not isinstance(cluster_data, dict):
# #         #     raise ValueError(f"Expected dict for cluster_data, got {type(cluster_data)}")
# #
# #         # if 'free_disks_obj' not in cluster_data:
# #         #     raise ValueError(f"Missing 'free_disks_obj' in cluster_data. Available keys: {cluster_data.keys()}")
# #
# #         free_disks = cluster_data.get('free_disks_obj', [])
# #         disks_info = cluster_data.get('disks_info', {})
# #
# #         print(f"DEBUG: free_disks type: {type(free_disks)}")
# #         print(f"DEBUG: free_disks content: {free_disks}")
# #
# #         strategy = self._get_strategy(pool_config)
# #         result = strategy.select_disks(free_disks, disks_info, pool_config)
# #         print(f"DEBUG: RESULT: {result}")
# #
# #         return {
# #             'main_disks': result['main_disks'],
# #             'wrc_disks': result.get('cache_disks', []),
# #             'rdc_disks': [],
# #             'spare_disks': []
# #         }
# #
# #     def _get_strategy(self, pool_config: PoolConfig) -> DiskSelectionStrategy:
# #         """Get appropriate disk selection strategy based on configuration"""
# #         strategy_key = 'auto' if pool_config.auto_configure else 'manual'
# #         return self._strategies[strategy_key]
# #
# #     def _prepare_cluster_info(self, cluster_info: dict) -> ClusterDisks:
# #         """
# #         Convert extracted cluster info to ClusterDisks model
# #         """
# #         return ClusterDisks(disks=cluster_info['disks_info'])
