from typing import Dict, Type
from framework.models.pool_models import PoolConfig, PoolData
from framework.core.logger import logger
from ..pools.disk_selection_strategies.base import DiskSelectionStrategy
from ..pools.disk_selection_strategies.auto import AutoConfigureStrategy
from ..pools.disk_selection_strategies.manual import ManualConfigureStrategy
from ..pools.disk_selection_strategies.expansion import ExpansionStrategy


class DiskSelector:
    def __init__(self, disk_tools):
        self._disk_tools = disk_tools
        # Храним классы стратегий, а не их экземпляры
        self._auto_strategy = AutoConfigureStrategy
        self._manual_strategy = ManualConfigureStrategy
        self._expansion_strategy = ExpansionStrategy

    def select_disks_auto(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
        """Автоматический выбор дисков для нового пула"""
        strategy = self._auto_strategy(self)
        return strategy.select_disks(cluster_data, pool_config)

    def select_disks_manual(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
        """Ручной выбор дисков для нового пула"""
        strategy = self._manual_strategy(self)
        return strategy.select_disks(cluster_data, pool_config)

    def select_disks_for_expansion(self, cluster_data: dict, pool_data: PoolData) -> dict:
        """Выбор дисков для расширения существующего пула"""
        strategy = self._expansion_strategy(self)
        return strategy.select_disks(cluster_data, pool_data)

    def select_disks(self, cluster_data: dict, pool_config: PoolConfig) -> dict:
        if pool_config.auto_configure:
            return self.select_disks_auto(cluster_data, pool_config)
        return self.select_disks_manual(cluster_data, pool_config)
