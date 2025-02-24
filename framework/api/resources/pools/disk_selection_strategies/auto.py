'''
Определяет логику выбора конкретных дисков для пула
Выбирает оптимальные группы дисков по заданным критериям
Распределяет диски по ролям (main, spare, wrc, rdc)
Обновляет конфигурацию пула размерами выбранных дисков
Отслеживает уже использованные диски
Обеспечивает потокобезопасность при выборе дисков
отвечает на вопрос: "КАК выбрать" (логика выбора)
'''
from framework.api.models.disk_models import DiskSelection, ClusterDisks, DiskType
from framework.api.models.pool_models import PoolConfig
from .base import DiskSelectionStrategy


class AutoConfigureStrategy(DiskSelectionStrategy):
    """Стратегия автоматического выбора дисков"""


    def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
        # Создание объекта выбранных дисков
        selection = DiskSelection(set(), set(), set(), set())

        # Блокировка для обеспечения потокобезопасности
        with self._lock:
            # Выбор основных дисков
            self._select_main_disks(cluster_disks, pool_config, selection)

            # Выбор запасных дисков
            self._select_spare_disks(cluster_disks, pool_config, selection)

            # Выбор write cache дисков
            if pool_config.wrCacheDiskCount:
                self._select_wrc_disks(cluster_disks, pool_config, selection)

            # Выбор read cache дисков
            if pool_config.rdCacheDiskCount:
                self._select_rdc_disks(cluster_disks, pool_config, selection)

            # Логирование результатов
            # self._log_selection_results(selection)

            return selection

    # Выбор основных дисков
    def _select_main_disks(self, cluster_disks: ClusterDisks, pool_config: PoolConfig,
                           selection: DiskSelection) -> None:
        disk_group = self._select_disk_group(
            cluster_disks=cluster_disks,
            disk_type=DiskType(pool_config.mainDisksType) if pool_config.mainDisksType else None,
            disk_size=pool_config.mainDisksSize,
            count=pool_config.mainDisksCount
        )

        selection.main_disks = disk_group['disks']
        pool_config.mainDisksSize = disk_group['size']
        pool_config.mainDisksType = disk_group['type']
        self._used_disks.update(disk_group['disks'])

    # Выбор spare дисков. Диски должны быть идентичны main дискам.
    def _select_spare_disks(self, cluster_disks: ClusterDisks, pool_config: PoolConfig,
                            selection: DiskSelection) -> None:
        if not pool_config.spareCacheDiskCount:
            return

        disk_group = self._select_disk_group(
            cluster_disks=cluster_disks,
            disk_type=pool_config.spareDiskType if hasattr(pool_config, 'spareDiskType') else pool_config.mainDisksType,
            disk_size=pool_config.mainDisksSize,
            count=pool_config.spareCacheDiskCount
        )

        selection.spare_disks = disk_group['disks']
        pool_config.spareDiskType = disk_group['type']
        pool_config.spareDiskSize = disk_group['size']
        self._used_disks.update(disk_group['disks'])

    def _select_wrc_disks(self, cluster_disks: ClusterDisks, pool_config: PoolConfig,
                          selection: DiskSelection) -> None:
        # Выбор write cache дисков
        wrc_group = self._select_disk_group(
            cluster_disks=cluster_disks,
            count=pool_config.wrCacheDiskCount,
            disk_type=pool_config.wrcDiskType if hasattr(pool_config, 'wrcDiskType') else DiskType.SSD,
            for_cache=True
        )

        selection.wrc_disks = wrc_group['disks']
        pool_config.wrcDiskType = wrc_group['type']
        pool_config.wrcDiskSize = wrc_group['size']
        self._used_disks.update(wrc_group['disks'])


    def _select_rdc_disks(self, cluster_disks: ClusterDisks, pool_config: PoolConfig,
                          selection: DiskSelection) -> None:
        # Выбор read cache дисков
        rdc_group = self._select_disk_group(
            cluster_disks=cluster_disks,
            count=pool_config.rdCacheDiskCount,
            disk_type=pool_config.rdcDiskType if hasattr(pool_config, 'rdcDiskType') else DiskType.SSD,
        )
        selection.rdc_disks = rdc_group['disks']
        pool_config.rdcDiskType = rdc_group['type']
        pool_config.rdcDiskSize = rdc_group['size']
        self._used_disks.update(rdc_group['disks'])

