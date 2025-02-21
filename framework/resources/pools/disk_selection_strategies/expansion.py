from typing import List, Set
from framework.core.logger import logger
from framework.models.disk_models import DiskSelection, ClusterDisks, DiskType
from framework.models.pool_models import PoolConfig, PoolData
from .base import DiskSelectionStrategy


class ExpansionStrategy(DiskSelectionStrategy):
    def _select_disks_impl(self, cluster_disks: ClusterDisks, current_pool: PoolData) -> DiskSelection:
        selection = DiskSelection(set(), set(), set(), set())

        with self._lock:
            self._select_expansion_disks(cluster_disks, current_pool, selection)
            return selection


    def _select_expansion_disks(self, cluster_disks: ClusterDisks,
                                current_pool: PoolData,
                                selection: DiskSelection) -> None:
        logger.info(f"CURRENT_POOL: {current_pool}")
        # Получаем характеристики существующих дисков
        sample_disk_id = current_pool.props.disks[0]
        logger.info(f"SAMPLE_DISK_ID: {sample_disk_id}")
        logger.info(f"DICT: {current_pool.props.disks}")

        required_count = len(current_pool.props.disks)
        logger.info(f"DISK_COUNT_NEEDED: {required_count}")

        sample_disk = cluster_disks.disks_info[sample_disk_id]
        logger.info(f"SAMPLE_DISK_INFO: {sample_disk}")

        # Выбираем диски с идентичными характеристиками
        disk_group = self._select_disk_group(
            cluster_disks=cluster_disks,
            disk_type=DiskType(sample_disk['type']),
            disk_size=sample_disk['size'],
            count=len(current_pool.props.disks)
        )

        selection.main_disks = disk_group['disks']
        self._used_disks.update(disk_group['disks'])

# class ExpansionStrategy(DiskSelectionStrategy):
#     def _select_disks_impl(self, cluster_disks: ClusterDisks, current_pool: dict) -> DiskSelection:
#         selection = DiskSelection()
#
#         with self._lock:
#             sample_disk_id = current_pool['main_disks'][0]
#             required_count = len(current_pool['main_disks'])
#
#             # Using disk_tools through public interface
#             disk_tools = self._disk_selector.get_disk_tools()
#             similar_disks = disk_tools.find_similar_disks(
#                 sample_disk_id=sample_disk_id,
#                 search_group=cluster_disks.free_disks,
#                 criteria=['type', 'size'],
#                 count=required_count
#             )
#
#             selection.main_disks = set(similar_disks)
#             self._used_disks.update(similar_disks)
#
#         return selection




# class ExpansionStrategy(DiskSelectionStrategy):
#     """Strategy for selecting disks for pool expansion"""
#
#     def _select_disks_impl(self, cluster_disks: ClusterDisks, current_pool: dict) -> DiskSelection:
#         selection = DiskSelection(set(), set(), set(), set())
#
#         with self._lock:
#             self._select_expansion_disks(cluster_disks, current_pool, selection)
#             return selection
#
#     def _select_expansion_disks(self, cluster_disks: ClusterDisks,
#                                 current_pool: dict,
#                                 selection: DiskSelection) -> None:
#         # Получаем первый диск из существующего пула как образец
#         existing_disks = current_pool['props']['disks']
#         sample_disk_id = existing_disks[0]
#         sample_disk = cluster_disks.disks_info[sample_disk_id]
#
#         # Выбираем диски с такими же характеристиками
#         disk_group = self._select_disk_group(
#             cluster_disks=cluster_disks,
#             disk_type=DiskType(sample_disk['type']),
#             disk_size=sample_disk['size'],
#             count=len(existing_disks)  # Столько же дисков, сколько в основном пуле
#         )
#
#         selection.main_disks = disk_group['disks']
#         self._used_disks.update(disk_group['disks'])
