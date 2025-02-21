from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Set, Union


class DiskType(str, Enum):
    HDD = "HDD"
    SSD = "SSD"
    NVME = "NVME"

class DiskState(str, Enum):
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"

@dataclass
class DiskPartition:
    part_num: int
    dev_name: str
    part_size: str
    type: str
    part_link: str

@dataclass
class DiskInfo:
    name: str
    active: int
    state: DiskState
    ioerr_cnt: int
    dev_name: str
    serial: str
    vendor: str
    model: str
    bus: str
    rotational: int
    size: int
    type: DiskType
    status: str
    rdcache: bool
    spare: bool
    pools: List[str]
    removed: bool
    damaged: bool
    nodes_view: List[int]
    logical_block_size: int
    physical_block_size: int
    hw_sector_size: int
    in_rack: int
    rpm: int
    target_port: str
    cache_size: int
    used_hb: int
    used_as_wc: int
    led_state: int
    enclosure_id: str
    expander_sas_address: str
    slot: int
    path_count: int
    partition_count: int
    partitions: List[DiskPartition] = field(default_factory=list)

@dataclass
class ClusterDisks:
    """Информация о дисках кластера"""
    disks_info: Dict[str, dict]  # Информация о всех дисках
    free_disks: List[str]  # Список свободных дисков
    free_for_wc: List[str]  # Список дисков доступных для write cache
    free_disks_by_size_and_type: Dict[tuple, List[str]]

    # def get_disks_by_type(self, disk_type: str) -> List[str]:
    #     """Получение списка дисков определенного типа"""
    #     return [
    #         disk_id for disk_id in self.free_disks
    #         if self.disks_info[disk_id]['type'] == disk_type
    #     ]
    #
    # def get_disks_by_size(self, size: int) -> List[str]:
    #     """Получение списка дисков определенного размера"""
    #     return [
    #         disk_id for disk_id in self.free_disks
    #         if self.disks_info[disk_id]['size'] == size
    #     ]
    #
    # @property
    # def available_disks(self) -> Dict[str, dict]:
    #     return {
    #         name: disk for name, disk in self.disks.items()
    #         if not disk['pools'] and not disk['damaged'] and not disk['removed']
    #     }


@dataclass
class DiskSelection:
    main_disks: Union[Set[str], List[str]] = field(default_factory=set)
    wrc_disks: Union[Set[str], List[str]] = field(default_factory=set)
    rdc_disks: Union[Set[str], List[str]] = field(default_factory=set)
    spare_disks: Union[Set[str], List[str]] = field(default_factory=set)

    def to_dict(self) -> Dict:
        return {
            'mainDisks': list(self.main_disks),
            'wrcDisks': list(self.wrc_disks),
            'rdcDisks': list(self.rdc_disks),
            'spareDisks': list(self.spare_disks)
        }

    # Если захотим отрезать невыбранные диски (пустой списко []) из payload
    # def to_dict(self) -> Dict:
    #     result = {}
    #     if self.main_disks:
    #         result['mainDisks'] = list(self.main_disks)
    #     if self.wrc_disks:
    #         result['wrcDisks'] = list(self.wrc_disks)
    #     if self.rdc_disks:
    #         result['rdcDisks'] = list(self.rdc_disks)
    #     if self.spare_disks:
    #         result['spareDisks'] = list(self.spare_disks)
    #     return result

# @dataclass
# class DiskSelection:
#     main_disks: set[str] = field(default_factory=set)
#     wrc_disks: set[str] = field(default_factory=set)
#     rdc_disks: set[str] = field(default_factory=set)
#     spare_disks: set[str] = field(default_factory=set)
#     # Множество использованных дисков. Используется для предотвращения повторного выбора одних и тех же дисков
#     # Важно для процесса выбора дисков в разные группы
#     used_disks: Set[str] = field(default_factory=set)


@dataclass
class DiskRequirements:
    type: DiskType
    count: int
    size: Optional[int] = None
    min_main_disks: int = 2
    min_wrc_disks: int = 2
    priority_type: Optional[str] = None