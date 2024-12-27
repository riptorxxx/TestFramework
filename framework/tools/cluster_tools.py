from framework.tools.base_tools import BaseTools
from framework.helpers.extractors import TestExtractor


class ClusterTools(BaseTools):
    """Tools for cluster operations"""

    def validate(self):
        if not self._context.cluster_info:
            self.update_cluster_info()

    def update_cluster_info(self):
        """Update cluster information"""
        response = self._context.client.get("/nodes/clusterInfo")
        assert response.status_code == 200
        self._context.cluster_info = response.json()

    def get_cluster_info(self):
        """Get processed cluster information"""
        self.validate()
        return TestExtractor().extract_cluster_info(
            self._context.cluster_info,
            self._context.keys_to_extract
        )
