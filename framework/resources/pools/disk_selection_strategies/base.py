from abc import ABC, abstractmethod
from typing import Tuple
from framework.configs.pool_config import PoolConfig


class DiskSelectionStrategy(ABC):
    """Base strategy for disk selection"""

    @abstractmethod
    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> Tuple[list, list, list, list]:
        """
        Select disks according to strategy

        Args:
            cluster_info: Cluster information with available disks
            pool_config: Pool configuration

        Returns:
            Tuple of lists: (main_disks, wrc_disks, rdc_disks, spare_disks)
        """
        pass
