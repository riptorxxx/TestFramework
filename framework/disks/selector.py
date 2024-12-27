import testit
from .strategies import DiskSelectionStrategy, AutoConfigureStrategy, ManualSelectionStrategy


class DiskSelector:
    """Disk selection orchestrator"""

    def __init__(self, disk_tools):
        self._disk_tools = disk_tools
        self._strategies = {
            'auto': AutoConfigureStrategy(),
            'manual': ManualSelectionStrategy()
        }

    def select_disks(self, cluster_info: dict, pool_config) -> tuple:
        strategy = self._get_strategy(pool_config)
        result = strategy.select_disks(cluster_info, pool_config)

        with testit.step(f"Selected disks: {result}"):
            return result

    def _get_strategy(self, pool_config) -> DiskSelectionStrategy:
        return self._strategies['auto' if pool_config.auto_configure else 'manual']
