from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict


class DiskType(str, Enum):
    HDD = "HDD"
    SSD = "SSD"
    NVME = "NVME"


class DiskState(str, Enum):
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass
class DiskRequirements:
    type: DiskType
    count: int
    size: Optional[int] = None


@dataclass
class DiskSelection:
    main_disks: List[dict]
    wrc_disks: List[dict]
    rdc_disks: List[dict]
    spare_disks: List[dict]


@dataclass
class ClusterDisks:
    disks: Dict[str, dict]

    @property
    def available_disks(self) -> Dict[str, dict]:
        return {
            name: disk for name, disk in self.disks.items()
            if not disk['pools'] and not disk['damaged'] and not disk['removed']
        }


#
# @dataclass
# class DiskInfo:
#     name: str
#     active: int
#     state: DiskState
#     ioerr_cnt: int
#     dev_name: str
#     serial: str
#     vendor: str
#     model: str
#     bus: str
#     rotational: int
#     size: int
#     type: DiskType
#     status: str
#     rdcache: bool
#     spare: bool
#     pools: List[str]
#     removed: bool
#     damaged: bool
#     nodes_view: List[int]
#     logical_block_size: int
#     physical_block_size: int
#     hw_sector_size: int
#     in_rack: int
#     rpm: int
#     target_port: str
#     cache_size: int
#     used_hb: int
#     used_as_wc: int
#     led_state: int
#     enclosure_id: str
#     expander_sas_address: str
#     slot: int
#     path_count: int
#     partition_count: int
#     partitions: List[DiskPartition] = field(default_factory=list)

# @dataclass
# class DiskSelection:
#     main_disks: List[DiskInfo]
#     spare_disks: Optional[List[DiskInfo]] = None
#     wrc_disks: Optional[List[DiskInfo]] = None
#     rdc_disks: Optional[List[DiskInfo]] = None


# @dataclass
# class DiskPartition:
#     part_num: int
#     dev_name: str
#     part_size: str
#     type: str
#     part_link: str

