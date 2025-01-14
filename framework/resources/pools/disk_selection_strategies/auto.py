from .base import DiskSelectionStrategy
from framework.configs.pool_config import PoolConfig

class AutoConfigureStrategy(DiskSelectionStrategy):
    """Strategy for automatic disk selection"""

    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> tuple:
        pool_data = pool_config.pool_data
        return (
            pool_data.get('mainDisks', []),
            pool_data.get('wrcDisks', []),
            pool_data.get('rdcDisks', []),
            pool_data.get('spareDisks', [])
        )
