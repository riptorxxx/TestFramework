from typing import List, Set, Dict
from framework.models.disk_models import DiskSelection, ClusterDisks, DiskType
from framework.models.pool_models import PoolConfig
from framework.core.logger import logger
from .base import DiskSelectionStrategy


class ManualConfigureStrategy(DiskSelectionStrategy):
    """Стратегия ручного выбора дисков"""

    def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
        # Создаем объект для хранения выбранных дисков
        selection = DiskSelection(set(), set(), set(), set())

        # Блокируем доступ к общим ресурсам на время выполнения
        with self._lock:
            # Последовательно выбираем диски каждого типа, если они указаны в конфигурации
            if pool_config.mainDisks:
                self._select_main_disks(cluster_disks, pool_config, selection)

            if pool_config.spareDisks:
                self._select_spare_disks(cluster_disks, pool_config, selection)

            if pool_config.wrcDisks:
                self._select_wrc_disks(cluster_disks, pool_config, selection)

            if pool_config.rdcDisks:
                self._select_rdc_disks(cluster_disks, pool_config, selection)

            # Логируем результаты выбора
            # self._log_selection_results(selection)
            return selection

    def _select_main_disks(self, cluster_disks: ClusterDisks, pool_config: PoolConfig,
                           selection: DiskSelection) -> None:
        # Проверяем режим выбора дисков: список конкретных дисков или количество
        if isinstance(pool_config.mainDisks, list):
            # Проверяем и добавляем указанные диски
            selection.main_disks = set(self._validate_manual_disks(cluster_disks, pool_config.mainDisks))
            # Получаем информацию о первом диске для определения размера и типа
            disk_info = cluster_disks.disks_info[next(iter(selection.main_disks))]
            pool_config.mainDisksSize = disk_info['size']
            pool_config.mainDisksType = DiskType(disk_info['type'])
        else:
            # Автоматически выбираем указанное количество HDD дисков
            disk_group = self._select_disk_group(
                cluster_disks=cluster_disks,
                disk_type=DiskType.HDD,
                count=pool_config.mainDisks,
                disk_size=None
            )
            selection.main_disks = disk_group['disks']
            pool_config.mainDisksSize = disk_group['size']
            pool_config.mainDisksType = disk_group['type']

        # Добавляем выбранные диски в множество использованных
        self._used_disks.update(selection.main_disks)

    def _select_spare_disks(self, cluster_disks: ClusterDisks, pool_config: PoolConfig,
                            selection: DiskSelection) -> None:
        if isinstance(pool_config.spareDisks, list):
            # Проверяем и добавляем указанные запасные диски
            selection.spare_disks = set(self._validate_manual_disks(cluster_disks, pool_config.spareDisks))
        else:
            # Получаем характеристики из первого основного диска
            first_main_disk = next(iter(selection.main_disks))
            main_disk_info = cluster_disks.disks_info[first_main_disk]

            # Выбираем запасные диски того же типа и размера
            disk_group = self._select_disk_group(
                cluster_disks=cluster_disks,
                disk_type=DiskType(main_disk_info['type']),
                count=pool_config.spareDisks,
                disk_size=main_disk_info['size']
            )
            selection.spare_disks = disk_group['disks']

        self._used_disks.update(selection.spare_disks)

    def _select_wrc_disks(self, cluster_disks: ClusterDisks, pool_config: PoolConfig,
                          selection: DiskSelection) -> None:
        if isinstance(pool_config.wrcDisks, list):
            # Проверяем и добавляем указанные WRC диски
            selection.wrc_disks = set(self._validate_manual_disks(cluster_disks, pool_config.wrcDisks))
            # Сохраняем размер дисков в конфигурации
            pool_config.wrcDiskSize = cluster_disks.disks_info[next(iter(selection.wrc_disks))]['size']
        else:
            # Автоматически выбираем указанное количество SSD дисков для WRC
            disk_group = self._select_disk_group(
                cluster_disks=cluster_disks,
                disk_type=DiskType.SSD,
                count=pool_config.wrcDisks,
                for_cache=True
            )
            selection.wrc_disks = disk_group['disks']
            pool_config.wrcDiskSize = disk_group['size']

        self._used_disks.update(selection.wrc_disks)

    def _select_rdc_disks(self, cluster_disks: ClusterDisks, pool_config: PoolConfig,
                          selection: DiskSelection) -> None:
        if isinstance(pool_config.rdcDisks, list):
            # Проверяем и добавляем указанные RDC диски
            selection.rdc_disks = set(self._validate_manual_disks(cluster_disks, pool_config.rdcDisks))
            # Сохраняем размер дисков в конфигурации
            pool_config.rdcDiskSize = cluster_disks.disks_info[next(iter(selection.rdc_disks))]['size']
        else:
            # Автоматически выбираем указанное количество SSD дисков для RDC
            disk_group = self._select_disk_group(
                cluster_disks=cluster_disks,
                disk_type=DiskType.SSD,
                count=pool_config.rdcDisks
            )
            selection.rdc_disks = disk_group['disks']
            pool_config.rdcDiskSize = disk_group['size']

        self._used_disks.update(selection.rdc_disks)

    def _validate_manual_disks(self, cluster_disks: ClusterDisks, disk_ids: List[str]) -> List[str]:
        """Валидация вручную выбранных дисков"""
        for disk_id in disk_ids:
            # Проверяем существование диска в кластере
            if disk_id not in cluster_disks.disks_info:
                raise ValueError(f"Disk {disk_id} not found")
            # Проверяем не используется ли диск уже
            if disk_id in self._used_disks:
                raise ValueError(f"Disk {disk_id} already in use")
        return disk_ids


# from typing import List
# from .base import DiskSelectionStrategy
# from framework.models.disk_models import DiskSelection, ClusterDisks
# from framework.models.pool_models import PoolConfig
#
#
# class ManualConfigureStrategy(DiskSelectionStrategy):
#     def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> tuple[DiskSelection, dict]:
#         selection = DiskSelection([], [], [], [])
#         used_disks = set()
#         sizes = {}
#
#         if pool_config.mainDisks:
#             if isinstance(pool_config.mainDisks, list):
#                 selection.main_disks = self._validate_manual_disks(cluster_disks, pool_config.mainDisks, used_disks)
#                 sizes['main'] = cluster_disks.disks_info[selection.main_disks[0]]['size']
#             else:
#                 selection.main_disks, main_size = self._disk_selector.select_disks_by_type(
#                     cluster_disks,
#                     "HDD",
#                     pool_config.mainDisks,
#                     used_disks
#                 )
#                 if main_size:
#                     sizes['main'] = main_size
#             used_disks.update(selection.main_disks)
#
#         # write cache disks
#         if pool_config.wrcDisks:
#             if isinstance(pool_config.wrcDisks, list):
#                 selection.wrc_disks = self._validate_manual_disks(cluster_disks, pool_config.wrcDisks, used_disks)
#                 sizes['wrc'] = cluster_disks.disks_info[selection.wrc_disks[0]]['size']
#             else:
#                 selection.wrc_disks, wrc_size = self._disk_selector.select_write_cache_disks(
#                     cluster_disks,
#                     pool_config.wrcDisks,
#                     used_disks
#                 )
#                 if wrc_size:
#                     sizes['wrc'] = wrc_size
#             used_disks.update(selection.wrc_disks)
#
#         # Spare disks
#         if pool_config.spareDisks:
#             if isinstance(pool_config.spareDisks, list):
#                 selection.spare_disks = self._validate_manual_disks(cluster_disks, pool_config.spareDisks, used_disks)
#                 sizes['spare'] = cluster_disks.disks_info[selection.spare_disks[0]]['size']
#             else:
#                 main_size = sizes.get('main')
#                 main_type = cluster_disks.disks_info[list(selection.main_disks)[0]]['type']
#                 selection.spare_disks = self._disk_selector.select_spare_disks(
#                     cluster_disks,
#                     pool_config.spareDisks,
#                     main_size,
#                     main_type,
#                     used_disks
#                 )
#                 if selection.spare_disks:
#                     sizes['spare'] = main_size
#             used_disks.update(selection.spare_disks)
#
#         # Read cache disks
#         if pool_config.rdcDisks:
#             if isinstance(pool_config.rdcDisks, list):
#                 selection.rdc_disks = self._validate_manual_disks(cluster_disks, pool_config.rdcDisks, used_disks)
#                 sizes['rdc'] = cluster_disks.disks_info[selection.rdc_disks[0]]['size']
#             else:
#                 selection.rdc_disks, rdc_size = self._disk_selector.select_read_cache_disks(
#                     cluster_disks,
#                     pool_config.rdcDisks,
#                     used_disks
#                 )
#                 if rdc_size:
#                     sizes['rdc'] = rdc_size
#             used_disks.update(selection.rdc_disks)
#
#         return selection, sizes
#
#
#     def _validate_manual_disks(
#             self,
#             cluster_disks: ClusterDisks,
#             disk_ids: List[str],
#             used_disks: set
#     ) -> List[str]:
#         for disk_id in disk_ids:
#             if disk_id not in cluster_disks.disks_info:
#                 raise ValueError(f"Disk {disk_id} not found")
#             if disk_id in used_disks:
#                 raise ValueError(f"Disk {disk_id} already in use")
#         return disk_ids


# from typing import List, Dict, Union, Optional
# from framework.models.disk_models import DiskSelection, ClusterDisks
# from framework.models.pool_models import PoolConfig
# from .base import DiskSelectionStrategy
#
#
# class ManualConfigureStrategy(DiskSelectionStrategy):
#     def select_disks(self, free_disks: list, disks_info: dict, pool_config) -> dict:
#         main_count = pool_config.mainDisks if isinstance(pool_config.mainDisks, int) else len(pool_config.mainDisks)
#         main_disks = free_disks[:main_count]
#
#         remaining_disks = [d for d in free_disks if d not in main_disks]
#         cache_disks = [d for d in remaining_disks if disks_info[d]['type'] == 'SSD']
#
#         return {
#             'main_disks': main_disks,
#             'cache_disks': cache_disks[:pool_config.wrcDisks] if pool_config.wrcDisks else []
#         }
#     # def select_disks(self, cluster_info: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
#     #     available_disks = cluster_info.available_disks
#     #     disk_type = "SSD" if pool_config.perfomance_type == 0 else None
#     #
#     #     main_disks = self._select_main_disks(
#     #         available_disks,
#     #         pool_config.mainDisks,
#     #         disk_type
#     #     )
#     #     used_disks = set(d['name'] for d in main_disks)
#     #
#     #     wrc_disks = self._select_cache_disks(
#     #         available_disks,
#     #         pool_config.wrcDisks,
#     #         used_disks
#     #     )
#     #     used_disks.update(d['name'] for d in wrc_disks)
#     #
#     #     rdc_disks = self._select_cache_disks(
#     #         available_disks,
#     #         pool_config.rdcDisks,
#     #         used_disks
#     #     )
#     #     used_disks.update(d['name'] for d in rdc_disks)
#     #
#     #     spare_disks = self._select_spare_disks(
#     #         available_disks,
#     #         pool_config.spareDisks,
#     #         main_disks[0] if main_disks else None,
#     #         used_disks
#     #     )
#     #
#     #     return DiskSelection(
#     #         main_disks=main_disks,
#     #         wrc_disks=wrc_disks,
#     #         rdc_disks=rdc_disks,
#     #         spare_disks=spare_disks
#     #     )
#
#     def _select_main_disks(
#             self,
#             available_disks: Dict[str, dict],
#             disk_count: Union[int, List[str]],
#             disk_type: str
#     ) -> List[dict]:
#         count = len(disk_count) if isinstance(disk_count, list) else disk_count
#         filtered_disks = [
#             disk for disk in available_disks.values()
#             if disk_type is None or disk['type'] == disk_type
#         ]
#         return filtered_disks[:count]
#
#     def _select_cache_disks(
#             self,
#             available_disks: Dict[str, dict],
#             disk_count: Union[int, List[str]],
#             used_disks: set
#     ) -> List[dict]:
#         if not disk_count:
#             return []
#
#         count = len(disk_count) if isinstance(disk_count, list) else disk_count
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
#             disk_count: Union[int, List[str]],
#             main_disk: Optional[dict],
#             used_disks: set
#     ) -> List[dict]:
#         if not disk_count or not main_disk:
#             return []
#
#         count = len(disk_count) if isinstance(disk_count, list) else disk_count
#         filtered_disks = [
#             disk for disk in available_disks.values()
#             if disk['name'] not in used_disks and
#                disk['type'] == main_disk['type'] and
#                disk['size'] == main_disk['size']
#         ]
#         return filtered_disks[:count]
