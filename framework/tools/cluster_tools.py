from framework.tools.base_tools import BaseTools
from framework.helpers.extractors import TestExtractor


class ClusterTools(BaseTools):
    """Tools for cluster operations"""

    def get_cluster_info(self, keys_to_extract=None):
        response = self._context.client.get("/nodes/clusterInfo")
        assert response.status_code == 200
        data = response.json()

        if keys_to_extract:
            return TestExtractor().extract_cluster_info(data, keys_to_extract)
        return data


''' Если вдруг нужно будет хранить контекст.'''
    # def validate(self):
    #     if not self._context.cluster_info:
    #         self.update_cluster_info()
    #
    # def update_cluster_info(self):
    #     """Update cluster information"""
    #     response = self._context.client.get("/nodes/clusterInfo")
    #     assert response.status_code == 200
    #     self._context.cluster_info = response.json()
    #
    # def get_cluster_info(self):
    #     """Get processed cluster information"""
    #     self.validate()
    #     return TestExtractor().extract_cluster_info(
    #         self._context.cluster_info,     # сырые данные о кластере
    #         self._context.keys_to_extract   # список ключей, которые нужно извлечь из данных
    #     )
