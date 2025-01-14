from typing import Dict
import testit
from framework.configs.pool_config import PoolConfig
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

    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> tuple:
        """
        Select disks based on pool configuration

        Args:
            cluster_info: Cluster information
            pool_config: Pool configuration

        Returns:
            tuple: Selected disks grouped by type
        """
        strategy = self._get_strategy(pool_config)
        result = strategy.select_disks(cluster_info, pool_config)

        with testit.step(f"Selected disks: {result}"):
            return result

    def _get_strategy(self, pool_config: PoolConfig) -> DiskSelectionStrategy:
        strategy_key = 'auto' if pool_config.auto_configure else 'manual'
        return self._strategies[strategy_key]
