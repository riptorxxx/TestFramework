from framework.api.core.api_client import logger
from typing import Dict, List


class TestExtractor:
    """Cluster information extractor"""

    def extract_cluster_info(self, data: dict, keys_to_extract: List[str]) -> Dict:
        extracted = {key: [] for key in keys_to_extract}
        disk_info = {
            'all_disks': set(),
            'free_disks': set(),
            'free_disks_obj': set(),
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
            'free_disks_obj': list(disk_info['free_disks_obj']),
            'free_for_wc': list(disk_info['free_for_wc']),
            'free_disks_by_size': disk_info['free_disks_by_size'],
            'free_disks_by_size_and_type': disk_info['free_disks_by_size_and_type'],
            'disks_info': disk_info['disks_info']
        }

    def _process_cluster_data(self, data, extracted, disk_info):
        """Process cluster data recursively"""
        # print(f"DEBUG: Processing cluster data: {data}")  # Add this line
        if isinstance(data, dict):
            self._process_dict(data, extracted, disk_info)
        elif isinstance(data, list):
            for item in data:
                self._process_cluster_data(item, extracted, disk_info)


    def _process_dict(self, data, extracted, disk_info):
        """
            Обработка словаря данных.

            Этот метод проходит по всем ключам и значениям в словаре. Если ключ
            присутствует в списке извлекаемых ключей, значение добавляется в соответствующий список.
            Если ключ равен "disks", вызывается метод обработки информации о дисках.

            Args:
                data (dict): Словарь данных для обработки.
                extracted (dict): Словарь для хранения извлеченной информации.
                disk_info (dict): Словарь для хранения информации о дисках.

            Returns:
                None
        """
        for key, value in data.items():
            if key in extracted:
                extracted[key].append(value)

            if key == "disks" and isinstance(value, dict):
                self._process_disks(value, disk_info)
                continue

            if isinstance(value, (dict, list)):
                self._process_cluster_data(value, extracted, disk_info)

    def _process_disks(self, disks, disk_info):
        """Process and categorize disks from cluster information"""

        # logger.info("\n=== Processing Cluster Disks ===")

        for disk_name, disk_data in disks.items():
            # logger.info(f"\nProcessing disk: {disk_name}")
            # logger.info(f"Full disk data: {disk_data}")

            disk_info['all_disks'].add(disk_name)

            # Save complete disk information
            disk_info['disks_info'][disk_name] = {
                'type': disk_data.get('type'),
                'size': disk_data.get('size'),
                'state': disk_data.get('state'),
                'model': disk_data.get('model'),
                'vendor': disk_data.get('vendor'),
                'serial': disk_data.get('serial'),
                'dev_name': disk_data.get('dev_name'),
                'rotational': disk_data.get('rotational'),
                'bus': disk_data.get('bus'),
                'partition_count': disk_data.get('partition_count'),
                'partitions': disk_data.get('partitions', []),
                'used_as_wc': disk_data.get('used_as_wc'),
                'rdcache': disk_data.get('rdcache'),
                'spare': disk_data.get('spare'),
                'pools': disk_data.get('pools', []),
                'damaged': disk_data.get('damaged'),
                'removed': disk_data.get('removed')
            }

            size = disk_data.get("size")
            disk_type = disk_data.get("type")
            pools = disk_data.get("pools", [])
            used_as_wc = disk_data.get("used_as_wc", 0)

            # Log disk status
            # if pools:
            #     logger.info(f"Disk {disk_name} is used in pools: {pools}")
            # if used_as_wc:
            #     logger.info(f"Disk {disk_name} is used as write cache")

            # Process free disks
            if not pools and used_as_wc == 0:
                # logger.info(f"Disk {disk_name} is free")
                disk_info['free_disks'].add(disk_name)
                disk_info['free_disks_obj'].add(disk_name)  # Add full disk object
                if size:
                    disk_info['free_disks_by_size'].setdefault(size, []).append(disk_name)
                    if disk_type:
                        key = (size, disk_type)
                        disk_info['free_disks_by_size_and_type'].setdefault(key, []).append(disk_name)

            # Process write cache disks
            if used_as_wc == 1:
                # logger.info(f"Disk {disk_name} is available for write cache")
                disk_info['free_for_wc'].add(disk_name)

        # Log final statistics
        # logger.info("\n=== Disk Processing Summary ===")
        # logger.info(f"Total disks found: {len(disk_info['all_disks'])}")
        # logger.info(f"Free disks: {len(disk_info['free_disks'])}")
        # logger.info(f"Write cache available: {len(disk_info['free_for_wc'])}")
