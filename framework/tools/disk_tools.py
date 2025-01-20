from framework.tools.base_tools import BaseTools
from framework.resources.disks.disk_selector import DiskSelector
from framework.helpers.retry import disk_operation_with_retry


class DiskTools(BaseTools):
    """Tools for disk operations"""

    def __init__(self, context):
        super().__init__(context)
        self.disk_selector = DiskSelector(self)

    def validate(self):
        self._context.tools_manager.cluster.validate()

    @disk_operation_with_retry()
    def select_disks_for_pool(self, pool_config):
        """Select disks for pools creation"""
        self.validate()
        cluster_info = self._context.tools_manager.cluster.get_cluster_info()
        return self.disk_selector.select_disks(cluster_info, pool_config)
