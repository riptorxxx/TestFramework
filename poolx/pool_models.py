from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PoolConfig:
    name: str
    node: int = 1
    raid_type: str = "raid1"
    performance_type: int = 1
    main_disks: List[str] = field(default_factory=list)
    wrc_disks: List[str] = field(default_factory=list)
    rdc_disks: List[str] = field(default_factory=list)
    spare_disks: List[str] = field(default_factory=list)
    percentage: int = 10
    priority: int = 0

@dataclass
class DiskGroup:
    disks: List[str]
    size: Optional[int] = None
    type: Optional[str] = None
