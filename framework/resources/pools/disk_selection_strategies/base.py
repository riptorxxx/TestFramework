from abc import ABC, abstractmethod
from typing import Tuple
from framework.models.pool_models import PoolConfig
from framework.models.disk_models import ClusterDisks, DiskSelection


class DiskSelectionStrategy(ABC):
    """Base strategy for disk selection"""

    @abstractmethod
    def select_disks(self, cluster_info: ClusterDisks, pool_config: PoolConfig) -> DiskSelection:
        """
        Select disks according to strategy

        Args:
            cluster_info: Structured cluster information with available disks
            pool_config: Pool configuration

        Returns:
            DiskSelection: Selected disks grouped by their roles
        """
        pass