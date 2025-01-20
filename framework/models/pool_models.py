from dataclasses import dataclass, asdict
from typing import Optional, Union, List
from .base_models import BaseConfig

@dataclass
class PoolConfig(BaseConfig):
    # Common parameters
    name: Optional[str] = None
    node: Optional[int] = None
    raid_type: str = "raid1"
    performance_type: int = 1
    percentage: int = 10
    priority: int = 0
    auto_configure: bool = True

    # Auto mode parameters
    main_disks_count: Optional[int] = None
    main_groups_count: Optional[int] = None
    main_disks_type: Optional[str] = None
    main_disks_size: Optional[int] = None
    wr_cache_disk_count: Optional[int] = None
    wrc_disk_type: Optional[str] = None
    wrc_disk_size: Optional[int] = None
    rd_cache_disk_count: Optional[int] = None
    rdc_disk_type: Optional[str] = None
    rdc_disk_size: Optional[int] = None
    spare_cache_disk_count: Optional[int] = None
    spare_disk_type: Optional[str] = None
    spare_disk_size: Optional[int] = None

    # Manual mode parameters
    main_disks: Optional[Union[int, List[str]]] = None
    wrc_disks: Optional[Union[int, List[str]]] = None
    rdc_disks: Optional[Union[int, List[str]]] = None
    spare_disks: Optional[Union[int, List[str]]] = None

    _api_mapping = {
        'name': 'name',
        'node': 'node',
        'raid_type': 'raidType',
        'performance_type': 'performanceType',
        'percentage': 'percentage',
        'priority': 'priority',
        'auto_configure': 'autoConfig',
        'main_disks_count': 'mainDisksCount',
        'main_groups_count': 'mainGroupsCount',
        'main_disks_type': 'mainDisksType',
        'main_disks_size': 'mainDisksSize',
        'wr_cache_disk_count': 'wrCacheDiskCount',
        'wrc_disk_type': 'wrcDiskType',
        'wrc_disk_size': 'wrcDiskSize',
        'rd_cache_disk_count': 'rdCacheDiskCount',
        'rdc_disk_type': 'rdcDiskType',
        'rdc_disk_size': 'rdcDiskSize',
        'spare_cache_disk_count': 'spareCacheDiskCount',
        'spare_disk_type': 'spareDiskType',
        'spare_disk_size': 'spareDiskSize',
        'main_disks': 'mainDisks',
        'wrc_disks': 'wrcDisks',
        'rdc_disks': 'rdcDisks',
        'spare_disks': 'spareDisks'
    }

