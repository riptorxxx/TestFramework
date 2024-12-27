from abc import ABC, abstractmethod
from typing import Dict, Tuple, Set, List
from dataclasses import dataclass
import testit

from tests.api.tests.pools.pools_helpers import PoolConfig


class DiskSelectionStrategy(ABC):
    """Базовый класс для стратегий выбора дисков"""

    @abstractmethod
    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> tuple:
        pass


class AutoConfigureStrategy(DiskSelectionStrategy):
    """Стратегия автоматического выбора дисков"""

    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> tuple:
        return (
            pool_config.pool_data.get('mainDisks', []),
            pool_config.pool_data.get('wrcDisks', []),
            pool_config.pool_data.get('rdcDisks', []),
            pool_config.pool_data.get('spareDisks', [])
        )


class ManualSelectionStrategy(DiskSelectionStrategy):
    """Стратегия ручного выбора дисков"""

    def select_disks(self, cluster_info: dict, pool_config: PoolConfig) -> tuple:
        used_disks = set()

        # Выбор основных дисков
        main_disks_result = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.mainDisks,
            used_disks,
            pool_config.mainDisksType,
            pool_config.mainDisksSize,
            "SSD" if pool_config.perfomance_type == 0 else None
        )
        used_disks.update(main_disks_result['disks'])

        # Выбор WRC дисков
        wrc_disks_result = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.wrCacheDiskCount,
            used_disks,
            pool_config.wrcDiskType,
            pool_config.wrcDiskSize
        )
        used_disks.update(wrc_disks_result['disks'])

        # Выбор RDC дисков
        rdc_disks_result = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.rdCacheDiskCount,
            used_disks,
            pool_config.rdcDiskType,
            pool_config.rdcDiskSize
        )
        used_disks.update(rdc_disks_result['disks'])

        # Выбор spare дисков
        spare_disks_result = self._select_disk_group(
            cluster_info['free_disks_by_size_and_type'],
            pool_config.spareCacheDiskCount,
            used_disks,
            pool_config.spareDiskType,
            pool_config.spareDiskSize
        )

        return (
            main_disks_result['disks'],
            wrc_disks_result['disks'],
            rdc_disks_result['disks'],
            spare_disks_result['disks']
        )

    def _select_disk_group(self, disks_by_size_and_type: Dict, count: int,
                           used_disks: Set, disk_type=None, disk_size=None,
                           priority_type=None) -> Dict:
        """Выбирает группу дисков с учетом заданных параметров"""
        if count == 0:
            return {'disks': [], 'size': None, 'type': None}

        # Приоритет SSD дисков
        if priority_type == "SSD":
            filtered_groups = {k: v for k, v in disks_by_size_and_type.items()
                               if k[1] == "SSD"}
        # Ручной режим с указанным типом и размером
        elif disk_type and disk_size:
            filtered_groups = {k: v for k, v in disks_by_size_and_type.items()
                               if k[1] == disk_type and k[0] == disk_size}
        # Ручной режим без специфических требований
        else:
            hdd_groups = {k: v for k, v in disks_by_size_and_type.items()
                          if k[1] == "HDD"}

            if not any(len(set(disks) - used_disks) >= count
                       for disks in hdd_groups.values()):
                ssd_groups = {k: v for k, v in disks_by_size_and_type.items()
                              if k[1] == "SSD"}
                filtered_groups = {**hdd_groups, **ssd_groups}
            else:
                filtered_groups = hdd_groups

        # Выбор дисков из отфильтрованных групп
        for (size, disk_type), disks in filtered_groups.items():
            available = list(set(disks) - used_disks)
            if len(available) >= count:
                selected = available[:count]
                return {'disks': selected, 'size': size, 'type': disk_type}

        raise ValueError(f"Недостаточно идентичных дисков для группы. Требуется: {count}")
