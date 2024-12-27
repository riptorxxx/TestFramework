from tests.api.tests.disks.disk_selection_strategy import (DiskSelectionStrategy,
                                                           AutoConfigureStrategy,
                                                           ManualSelectionStrategy)


class DiskOperationContext:
    """Контекст операций с дисками"""

    def __init__(self, test_context, pool_config):
        self.test_context = test_context
        self.pool_config = pool_config
        self.strategy = self._determine_strategy()

    def _determine_strategy(self) -> DiskSelectionStrategy:
        """Определяет стратегию выбора дисков"""
        return (AutoConfigureStrategy() if self.pool_config.auto_configure
                else ManualSelectionStrategy())

    def execute_selection(self) -> tuple:
        """Выполняет выбор дисков согласно выбранной стратегии"""
        return self.strategy.select_disks(
            self.test_context.cluster_info,
            self.pool_config
        )
