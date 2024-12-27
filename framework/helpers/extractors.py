from framework.api_client import logger
from typing import Dict, List


class TestExtractor:
    """Cluster information extractor"""

    def extract_cluster_info(self, data: dict, keys_to_extract: List[str]) -> Dict:
        extracted = {key: [] for key in keys_to_extract}
        disk_info = {
            'all_disks': set(),
            'free_disks': set(),
            'free_for_wc': set(),
            'free_disks_by_size': {},
            'free_disks_by_size_and_type': {},
            'disks_info': {}
        }

        self._process_cluster_data(data, extracted, disk_info)
        logger.info(f"Available free disks: {sorted(list(disk_info['free_disks']))}")

        return {
            **extracted,
            'all_disks': list(disk_info['all_disks']),
            'free_disks': list(disk_info['free_disks']),
            'free_for_wc': list(disk_info['free_for_wc']),
            'free_disks_by_size': disk_info['free_disks_by_size'],
            'free_disks_by_size_and_type': disk_info['free_disks_by_size_and_type'],
            'disks_info': disk_info['disks_info']
        }

    def _process_cluster_data(self, data, extracted, disk_info):
        """Process cluster data recursively"""
        if isinstance(data, dict):
            self._process_dict(data, extracted, disk_info)
        elif isinstance(data, list):
            for item in data:
                self._process_cluster_data(item, extracted, disk_info)

