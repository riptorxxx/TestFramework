from typing import Dict
import testit
from framework.models.pool_models import PoolConfig
from framework.models.disk_models import ClusterDisks, DiskSelection
from ..pools.disk_selection_strategies.base import DiskSelectionStrategy
from ..pools.disk_selection_strategies.auto import AutoConfigureStrategy
from ..pools.disk_selection_strategies.manual import ManualSelectionStrategy


class DiskSelector:
    """Disk selection orchestrator"""

    def __init__(self, disk_tools):
        self._disk_tools = disk_tools
        self._strategies: Dict[str, DiskSelectionStrategy] = {
            'auto': AutoConfigureStrategy(),
            'manual': ManualSelectionStrategy()
        }

    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> DiskSelection:
        """
        Select disks based on pool configuration

        Args:
            cluster_info: Raw cluster information dictionary
            pool_config: Pool configuration

        Returns:
            DiskSelection: Selected disks grouped by type
        """
        strategy = self._get_strategy(pool_config)
        cluster_disks = self._prepare_cluster_info(cluster_info)
        result = strategy.select_disks(cluster_disks, pool_config)

        with testit.step(f"Selected disks: {result}"):
            return result

    def _get_strategy(self, pool_config: PoolConfig) -> DiskSelectionStrategy:
        """Get appropriate disk selection strategy based on configuration"""
        strategy_key = 'auto' if pool_config.auto_configure else 'manual'
        return self._strategies[strategy_key]

    def _prepare_cluster_info(self, cluster_info: dict) -> ClusterDisks:
        """Convert raw cluster info into structured ClusterDisks object"""
        return ClusterDisks(disks=cluster_info['free_disks'])
