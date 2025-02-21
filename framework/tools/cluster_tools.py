from abc import ABC
from framework.tools.base_tools import BaseTools
from framework.utils.extractors import TestExtractor
from ..resources.endpoints import ApiEndpoints
from ..core.logger import logger


class ClusterTools(BaseTools):
    """Tools for cluster operations"""

    def validate(self):
        """Implementation of abstract method"""
        pass

    def get_cluster_info(self, keys_to_extract=None):
        """Get cluster information with required disk data"""
        response = self._context.client.get(ApiEndpoints.Cluster.CLUSTER_INFO)
        assert response.status_code == 200
        data = response.json()

        default_keys = ['disks_info', 'free_disks', 'free_for_wc', 'free_disks_by_size_and_type']
        extractor = TestExtractor()

        resp_data = extractor.extract_cluster_info(data, keys_to_extract or default_keys)
        logger.info(f"DATA: {resp_data}")

        return resp_data
        # return extractor.extract_cluster_info(data, keys_to_extract or default_keys)



    # def get_cluster_info(self, keys_to_extract=None):
    #     response = self._context.client.get(ApiEndpoints.Cluster.CLUSTER_INFO)
    #     assert response.status_code == 200
    #     data = response.json()
    #     # print(f"DEBUG: cluster info: {data}")
    #     # return TestExtractor().extract_cluster_info(data, keys_to_extract)
    #
    #     if keys_to_extract:
    #         return TestExtractor().extract_cluster_info(data, keys_to_extract)
    #     return data


    # def update_cluster_info(self):
    #     """Update cluster information"""
    #     response = self._context.client.get("/nodes/clusterInfo")
    #     assert response.status_code == 200
    #     self._context.cluster_info = response.json()

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
