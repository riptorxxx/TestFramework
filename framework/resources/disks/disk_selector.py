from typing import Dict, Type
from framework.models.pool_models import PoolConfig
from framework.core.logger import logger
from ..pools.disk_selection_strategies.base import DiskSelectionStrategy
from ..pools.disk_selection_strategies.auto import AutoConfigureStrategy
from ..pools.disk_selection_strategies.manual import ManualConfigureStrategy


class DiskSelector:
    def __init__(self, disk_tools):
        self._disk_tools = disk_tools
        self._strategies: Dict[str, Type[DiskSelectionStrategy]] = {
            'auto': AutoConfigureStrategy,
            'manual': ManualConfigureStrategy
        }
        logger.debug(f"DiskSelector initialized with disk_tools: {disk_tools}")

    def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
        strategy_type = 'auto' if pool_config.auto_configure else 'manual'
        strategy = self._strategies[strategy_type](self)
        return strategy.select_disks(cluster_data, pool_config)

    def register_strategy(self, name: str, strategy_class: Type[DiskSelectionStrategy]):
        if name in self._strategies:
            raise ValueError(f"Strategy {name} already registered")
        self._strategies[name] = strategy_class
        logger.info(f"Registered new disk selection strategy: {name}")

