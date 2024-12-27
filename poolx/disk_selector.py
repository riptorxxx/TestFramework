from typing import Dict, List, Set, Tuple
import time
from tests.api.tests.poolx.pool_constants import *
from tests.api.tests.poolx.pool_models import DiskGroup
from tests.api.api_client import logger

class DiskSelector:
    def __init__(self):
        self.used_disks: Set[str] = set()

    def reset_state(self) -> None:
        self.used_disks.clear()

    def select_disks_single(self, cluster_info: Dict, disk_config: Tuple[int, ...]) -> Tuple[List[str], ...]:
        """Single attempt disk selection for negative cases"""
        return self._try_select_disks(cluster_info, disk_config)

    def select_disks_with_retry(self, cluster_info: Dict, disk_config: Tuple[int, ...]) -> Tuple[List[str], ...]:
        """Disk selection with retries for positive cases"""
        attempts = 0
        last_error = None

        while attempts < MAX_RETRIES:
            try:
                return self._try_select_disks(cluster_info, disk_config)
            except ValueError as e:
                last_error = e
                attempts += 1
                if attempts < MAX_RETRIES:
                    logger.info(f"Attempt {attempts} failed: {str(e)}. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)

        raise ValueError(f"Failed to select disks after {MAX_RETRIES} attempts. Last error: {last_error}")

    def _try_select_disks(self, cluster_info: Dict, disk_config: Tuple[int, ...]) -> Tuple[List[str], ...]:
        main_count, wrc_count, rdc_count, spare_count = disk_config
        used_disks: Set[str] = set()

        # Select main disks
        main_disks_info = self._select_main_disks(
            cluster_info['free_disks_by_size_and_type'],
            main_count,
            used_disks
        )
        used_disks.update(main_disks_info.disks)

        # Select WRC disks
        wrc_disks = self._select_cache_disks(
            cluster_info,
            wrc_count,
            WRITE_CACHE,
            used_disks
        )
        used_disks.update(wrc_disks)

        # Select RDC disks
        rdc_disks = self._select_cache_disks(
            cluster_info,
            rdc_count,
            READ_CACHE,
            used_disks
        )
        used_disks.update(rdc_disks)

        # Select spare disks
        spare_disks = self._select_spare_disks(
            cluster_info['free_disks_by_size_and_type'],
            spare_count,
            main_disks_info.size,
            main_disks_info.type,
            used_disks
        )

        return main_disks_info.disks, wrc_disks, rdc_disks, spare_disks

    def _select_main_disks(self, disks_by_size_and_type: Dict, count: int, used_disks: Set[str]) -> DiskGroup:
        if count == 0:
            return DiskGroup([], None, None)

        # Try HDD first
        hdd_groups = {k: v for k, v in disks_by_size_and_type.items() if k[1] == HDD}
        for (size, disk_type), disks in hdd_groups.items():
            available = list(set(disks) - used_disks)
            if len(available) >= count:
                return DiskGroup(available[:count], size, disk_type)

        # Try SSD if no suitable HDD found
        ssd_groups = {k: v for k, v in disks_by_size_and_type.items() if k[1] == SSD}
        for (size, disk_type), disks in ssd_groups.items():
            available = list(set(disks) - used_disks)
            if len(available) >= count:
                return DiskGroup(available[:count], size, disk_type)

        raise ValueError(f"Not enough identical disks for main group. Required: {count}")
