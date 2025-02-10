from abc import ABC, abstractmethod
from framework.models.disk_models import DiskSelection, DiskRequirements, ClusterDisks, DiskType
from framework.models.pool_models import PoolConfig
from framework.core.logger import logger


class DiskSelectionStrategy(ABC):
    def __init__(self, disk_selector):
        # self.requirements = DiskRequirements()
        self._disk_selector = disk_selector

    def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
        logger.debug(f"Disks info: {cluster_data}")
        cluster_disks = ClusterDisks(
            disks_info=cluster_data['disks_info'],
            free_disks=cluster_data['free_disks'],
            free_for_wc=cluster_data['free_for_wc'],
            free_disks_by_size_and_type=cluster_data['free_disks_by_size_and_type']
        )
        logger.debug(f"Starting disk selection with free_disks: {cluster_disks.free_disks}")
        logger.debug(f"Created ClusterDisks with free_for_wc: {cluster_disks.free_for_wc}")

        pool_config.priority_type = DiskType.SSD if pool_config.perfomance_type == 0 else DiskType.HDD
        selection, sizes = self._select_disks_impl(cluster_disks, pool_config)

        # Важно: обновляем размеры в конфигурации пула
        self._update_pool_config_sizes(pool_config, sizes)

        logger.info(
            f"Selected disks:\n"
            f"main={selection.main_disks} (type={pool_config.mainDisksType}, size={sizes.get('main')})\n"
            f"wrc={selection.wrc_disks} (type={pool_config.wrcDiskType}, size={sizes.get('wrc')})\n"
            f"rdc={selection.rdc_disks} (type={pool_config.rdcDiskType}, size={sizes.get('rdc')})\n"
            f"spare={selection.spare_disks} (type={pool_config.spareDiskType}, size={sizes.get('spare')})"
        )

        return selection.to_dict()
        # return {
        #     'mainDisks': selection.main_disks,
        #     'wrcDisks': selection.wrc_disks,
        #     'rdcDisks': selection.rdc_disks,
        #     'spareDisks': selection.spare_disks
        # }

    def _update_pool_config_sizes(self, pool_config: PoolConfig, sizes: dict):
        if not pool_config.mainDisksSize and 'main' in sizes:
            pool_config.mainDisksSize = sizes['main']
        if not pool_config.wrcDiskSize and 'wrc' in sizes:
            pool_config.wrcDiskSize = sizes['wrc']
        if not pool_config.rdcDiskSize and 'rdc' in sizes:
            pool_config.rdcDiskSize = sizes['rdc']
        if not pool_config.spareDiskSize and 'spare' in sizes:
            pool_config.spareDiskSize = sizes['spare']

    @abstractmethod
    def _select_disks_impl(self, cluster_disks: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
        pass

    def _validate_disk_count(self, count: int, min_required: int, disk_type: str):
        if 0 < count < min_required:
            raise ValueError(
                f"The number of {disk_type} disks must be at least {min_required}, received {count}"
            )

