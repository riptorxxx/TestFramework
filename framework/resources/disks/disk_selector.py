from typing import Dict
import testit
from framework.models.pool_models import PoolConfig
from framework.models.disk_models import ClusterDisks, DiskSelection
from ..pools.disk_selection_strategies.base import DiskSelectionStrategy
from ..pools.disk_selection_strategies.auto import AutoConfigureStrategy
from ..pools.disk_selection_strategies.manual import ManualConfigureStrategy


class DiskSelector:
    """Disk selection orchestrator"""

    def __init__(self, disk_tools):
        self._disk_tools = disk_tools
        self._strategies: Dict[str, DiskSelectionStrategy] = {
            'auto': AutoConfigureStrategy(),
            'manual': ManualConfigureStrategy()
        }

    def select_disks(self, cluster_data: dict, pool_config) -> dict:
        # if not isinstance(cluster_data, dict):
        #     raise ValueError(f"Expected dict for cluster_data, got {type(cluster_data)}")

        # if 'free_disks_obj' not in cluster_data:
        #     raise ValueError(f"Missing 'free_disks_obj' in cluster_data. Available keys: {cluster_data.keys()}")

        free_disks = cluster_data.get('free_disks_obj', [])
        disks_info = cluster_data.get('disks_info', {})

        print(f"DEBUG: free_disks type: {type(free_disks)}")
        print(f"DEBUG: free_disks content: {free_disks}")

        strategy = self._get_strategy(pool_config)
        result = strategy.select_disks(free_disks, disks_info, pool_config)
        print(f"DEBUG: RESULT: {result}")

        return {
            'main_disks': result['main_disks'],
            'wrc_disks': result.get('cache_disks', []),
            'rdc_disks': [],
            'spare_disks': []
        }

    # def select_disks(self, cluster_data: dict, pool_config) -> dict:
    #     free_disks = list(cluster_data['free_disks_obj'])
    #     disks_info = cluster_data['disks_info']
    #
    #     strategy = self._get_strategy(pool_config)
    #     result = strategy.select_disks(free_disks, disks_info, pool_config)
    #
    #     with testit.step(f"Selected disks: {result}"):
    #         return result

    # def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> DiskSelection:
    #     """
    #     Select disks based on pool configuration
    #
    #     Args:
    #         cluster_info: Raw cluster information dictionary
    #         pool_config: Pool configuration
    #
    #     Returns:
    #         DiskSelection: Selected disks grouped by type
    #     """
    #     strategy = self._get_strategy(pool_config)
    #     cluster_disks = self._prepare_cluster_info(cluster_info)
    #     result = strategy.select_disks(cluster_disks, pool_config)
    #
    #     with testit.step(f"Selected disks: {result}"):
    #         return result

    def _get_strategy(self, pool_config: PoolConfig) -> DiskSelectionStrategy:
        """Get appropriate disk selection strategy based on configuration"""
        strategy_key = 'auto' if pool_config.auto_configure else 'manual'
        return self._strategies[strategy_key]

    def _prepare_cluster_info(self, cluster_info: dict) -> ClusterDisks:
        """
        Convert extracted cluster info to ClusterDisks model
        """
        return ClusterDisks(disks=cluster_info['disks_info'])

    # def _prepare_cluster_info(self, cluster_info: dict) -> ClusterDisks:
    #     """Convert raw cluster info into structured ClusterDisks object"""
    #     return ClusterDisks(disks=cluster_info['free_disks'])
