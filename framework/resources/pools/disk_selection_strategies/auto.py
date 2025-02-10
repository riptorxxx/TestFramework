from typing import List, Dict, Optional
from .base import DiskSelectionStrategy
from framework.models.disk_models import ClusterDisks, DiskSelection
from framework.models.pool_models import PoolConfig
from framework.core.logger import logger


class AutoConfigureStrategy(DiskSelectionStrategy):
    def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> tuple[DiskSelection, dict]:
        logger.debug(f"Starting auto disk selection for config: {pool_config}")
        selection = DiskSelection(set(), set(), set(), set())
        used_disks = set()
        sizes = {}

        # Выбираем main диски
        total_main_disks = pool_config.mainDisksCount * pool_config.mainGroupsCount
        main_result = self._disk_selector.select_main_disks(
            cluster_disks,
            total_main_disks,
            used_disks,
            disk_type=pool_config.mainDisksType,
            disk_size=pool_config.mainDisksSize,
            priority_type="SSD" if pool_config.perfomance_type == 0 else None
        )

        if main_result['disks']:
            selection.main_disks = set(main_result['disks'])
            pool_config.mainDisksSize = main_result['size']
            sizes['main'] = main_result['size']
            used_disks.update(main_result['disks'])
            logger.debug(f"Selected main disks: {main_result['disks']}")

        # Выбираем WRC диски
        if pool_config.wrCacheDiskCount:
            wrc_disks, wrc_size = self._disk_selector.select_write_cache_disks(
                cluster_disks,
                pool_config.wrCacheDiskCount,
                used_disks,
                disk_size=pool_config.wrcDiskSize
            )
            if wrc_disks:
                selection.wrc_disks = set(wrc_disks)
                pool_config.wrcDiskSize = wrc_size
                sizes['wrc'] = wrc_size
                used_disks.update(wrc_disks)
                logger.debug(f"Selected WRC disks: {wrc_disks}")

        # Выбираем RDC диски
        if pool_config.rdCacheDiskCount:
            rdc_disks, rdc_size = self._disk_selector.select_read_cache_disks(
                cluster_disks,
                pool_config.rdCacheDiskCount,
                used_disks,
                disk_size=pool_config.rdcDiskSize
            )
            if rdc_disks:
                selection.rdc_disks = set(rdc_disks)
                pool_config.rdcDiskSize = rdc_size
                sizes['rdc'] = rdc_size
                used_disks.update(rdc_disks)
                logger.debug(f"Selected RDC disks: {rdc_disks}")

        # Выбираем spare диски
        if pool_config.spareCacheDiskCount and selection.main_disks:
            required_size = pool_config.spareDiskSize or sizes.get('main')
            spare_disks = self._disk_selector.select_spare_disks(
                cluster_disks,
                pool_config.spareCacheDiskCount,
                required_size,
                pool_config.spareDiskType or main_result['type'],
                used_disks
            )
            if spare_disks:
                selection.spare_disks = set(spare_disks)
                pool_config.spareDiskSize = required_size
                sizes['spare'] = required_size
                logger.debug(f"Selected spare disks: {spare_disks}")

        logger.debug(f"Final disk selection: {selection}")
        logger.debug(f"Final disk sizes: {sizes}")
        return selection, sizes













    # def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> tuple[DiskSelection, dict]:
    #     logger.debug(f"Starting auto disk selection for config: {pool_config}")
    #     selection = DiskSelection([], [], [], [])
    #     used_disks = set()
    #     sizes = {}
    #
    #     # Вычисляем общее количество main дисков с учетом групп
    #     total_main_disks = pool_config.mainDisksCount * pool_config.mainGroupsCount
    #
    #     # Выбираем main диски и определяем их размер
    #     selection.main_disks, main_size = self._disk_selector.select_disks_by_type(
    #         cluster_disks,
    #         pool_config.mainDisksType,
    #         total_main_disks,
    #         used_disks
    #     )
    #     if main_size:
    #         pool_config.mainDisksSize = main_size
    #         sizes['main'] = main_size
    #         used_disks.update(selection.main_disks)
    #
    #     # Выбираем WRC диски и определяем их размер
    #     if pool_config.wrCacheDiskCount:
    #         selection.wrc_disks, wrc_size = self._disk_selector.select_write_cache_disks(
    #             cluster_disks,
    #             pool_config.wrCacheDiskCount,
    #             used_disks
    #         )
    #         if wrc_size:
    #             pool_config.wrcDiskSize = wrc_size
    #             sizes['wrc'] = wrc_size
    #             used_disks.update(set(selection.wrc_disks))
    #
    #     # Select RDC disks
    #     if pool_config.rdCacheDiskCount:
    #         selection.rdc_disks, rdc_size = self._disk_selector.select_read_cache_disks(
    #             cluster_disks,
    #             pool_config.rdCacheDiskCount,
    #             used_disks,
    #             required_size=pool_config.rdcDiskSize
    #         )
    #         if rdc_size:
    #             pool_config.rdcDiskSize = rdc_size
    #             sizes['rdc'] = rdc_size
    #             used_disks.update(selection.rdc_disks)
    #
    #     # Для spare дисков используем размер main дисков если не указан явно
    #     if pool_config.spareCacheDiskCount and selection.main_disks:
    #         required_size = pool_config.spareDiskSize or sizes.get('main')
    #         selection.spare_disks, spare_size = self._disk_selector.select_spare_disks(
    #             cluster_disks,
    #             pool_config.spareCacheDiskCount,
    #             used_disks,
    #             required_size=required_size,
    #             disk_type=pool_config.spareDiskType
    #         )
    #         if spare_size:
    #             pool_config.spareDiskSize = spare_size
    #             sizes['spare'] = spare_size
    #
    #     return selection, sizes

    def _get_disk_size_for_type(self, cluster_disks: ClusterDisks, disk_type: str, required_count: int) -> Optional[
        int]:
        """Определяет оптимальный размер для заданного типа и количества дисков"""
        type_disks = cluster_disks.get_disks_by_type(disk_type)
        if not type_disks:
            return None

        # Группируем диски по размеру и подсчитываем количество
        size_counts = {}
        for disk in type_disks:
            size = cluster_disks.disks_info[disk]['size']
            size_counts[size] = size_counts.get(size, 0) + 1

        # Выбираем наименьший размер, для которого есть достаточное количество дисков
        for size in sorted(size_counts.keys()):
            if size_counts[size] >= required_count:
                return size

        return None



# from typing import List, Dict, Optional
# from framework.models.disk_models import DiskSelection, ClusterDisks
# from framework.models.pool_models import PoolConfig
# from .base import DiskSelectionStrategy
#
#
# class AutoConfigureStrategy(DiskSelectionStrategy):
#     def select_disks(self, free_disks: list, disks_info: dict, pool_config) -> dict:
#         if pool_config.perfomance_type == 0:
#             main_disks = [disk for disk in free_disks
#                           if disks_info[disk]['type'] == 'SSD'][:pool_config.mainDisksCount]
#         else:
#             main_disks = [disk for disk in free_disks
#                           if disks_info[disk]['type'] == pool_config.mainDisksType][:pool_config.mainDisksCount]
#
#         remaining_disks = [d for d in free_disks if d not in main_disks]
#         cache_disks = [d for d in remaining_disks if disks_info[d]['type'] == 'SSD']
#
#         return {
#             'main_disks': main_disks,
#             'cache_disks': cache_disks[:pool_config.wrCacheDiskCount] if hasattr(pool_config,
#                                                                                  'wrCacheDiskCount') else []
#         }
#
#     def _select_main_disks(
#             self,
#             available_disks: Dict[str, dict],
#             count: int,
#             disk_type: str
#     ) -> List[dict]:
#         filtered_disks = [
#             disk for disk in available_disks.values()
#             if disk['type'] == disk_type
#         ]
#         return filtered_disks[:count]
#
#     def _select_cache_disks(
#             self,
#             available_disks: Dict[str, dict],
#             count: int,
#             used_disks: set
#     ) -> List[dict]:
#         if not count:
#             return []
#
#         filtered_disks = [
#             disk for disk in available_disks.values()
#             if disk['name'] not in used_disks and
#                disk['type'] == "SSD" and
#                disk['used_as_wc'] == 0
#         ]
#         return filtered_disks[:count]
#
#     def _select_spare_disks(
#             self,
#             available_disks: Dict[str, dict],
#             count: int,
#             main_disk: Optional[dict],
#             used_disks: set
#     ) -> List[dict]:
#         if not count or not main_disk:
#             return []
#
#         filtered_disks = [
#             disk for disk in available_disks.values()
#             if disk['name'] not in used_disks and
#                disk['type'] == main_disk['type'] and
#                disk['size'] == main_disk['size']
#         ]
#         return filtered_disks[:count]
