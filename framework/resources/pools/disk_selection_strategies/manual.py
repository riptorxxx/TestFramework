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

