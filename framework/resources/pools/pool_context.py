from typing import Tuple
from framework.core.context import TestContext  # Переименовали из FrameworkContext
from framework.models.pool_models import PoolConfig
from framework.resources.disks.disk_selector import DiskSelector

class BasePoolContext:
    """Base context for pool operations"""
    def __init__(self, test_context: TestContext):
        self._context = test_context
        self._disk_selector = DiskSelector(test_context.tools_manager.disk)

class PoolOperationContext(BasePoolContext):
    """Context for pool creation operations"""
    def __init__(self, test_context: TestContext, pool_config: PoolConfig):
        super().__init__(test_context)
        self._pool_config = pool_config

    def select_disks(self) -> Tuple[list, list, list, list]:
        """Execute disk selection based on pool configuration"""
        return self._disk_selector.select_disks(
            self._context.cluster_info,
            self._pool_config
        )
