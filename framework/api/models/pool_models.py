from dataclasses import dataclass, field
from typing import Optional, Union, List, Dict
from .base_models import BaseConfig


@dataclass
class PoolConfig(BaseConfig):
    # Common parameters
    name: Optional[str] = None
    node: Optional[int] = None
    raid_type: str = "raid1"
    perfomance_type: int = 1
    percentage: int = 10
    priority: int = 0
    auto_configure: bool = True

    # Auto mode parameters
    mainDisksCount: Optional[int] = None
    mainGroupsCount: Optional[int] = None
    mainDisksType: Optional[str] = None
    mainDisksSize: Optional[int] = None
    wrCacheDiskCount: Optional[int] = None
    wrcDiskType: Optional[str] = None
    wrcDiskSize: Optional[int] = None
    rdCacheDiskCount: Optional[int] = None
    rdcDiskType: Optional[str] = None
    rdcDiskSize: Optional[int] = None
    spareCacheDiskCount: Optional[int] = None
    spareDiskType: Optional[str] = None
    spareDiskSize: Optional[int] = None

    # Manual mode parameters
    mainDisks: Optional[Union[int, List[str]]] = None
    wrcDisks: Optional[Union[int, List[str]]] = None
    rdcDisks: Optional[Union[int, List[str]]] = None
    spareDisks: Optional[Union[int, List[str]]] = None

    def prepare_contract(self, dynamic_params: Dict) -> dict:
        """Подготовка контракта с учетом динамических параметров"""
        base_contract = self._prepare_base_contract(dynamic_params)

        if self.auto_configure:
            return self._add_auto_params(base_contract)
        return self._add_manual_params(base_contract)

    def _prepare_base_contract(self, dynamic_params: Dict) -> dict:
        """Подготовка базовых параметров контракта"""
        return {
            "name": dynamic_params.get('name', self.name),
            "node": dynamic_params.get('node', self.node),
            "raid_type": self.raid_type,
            "perfomance_type": self.perfomance_type,
            "percentage": self.percentage,
            "priority": self.priority,
            "auto_configure": self.auto_configure
        }

    def _add_auto_params(self, contract: dict) -> dict:
        """Добавление параметров автоконфигурации"""
        auto_params = {
            "mainDisksCount": self.mainDisksCount,
            "mainGroupsCount": self.mainGroupsCount,
            "mainDisksType": self.mainDisksType,
            "mainDisksSize": self.mainDisksSize,
            "wrCacheDiskCount": self.wrCacheDiskCount,
            "wrcDiskType": self.wrcDiskType,
            "wrcDiskSize": self.wrcDiskSize,
            "rdCacheDiskCount": self.rdCacheDiskCount,
            "rdcDiskType": self.rdcDiskType,
            "rdcDiskSize": self.rdcDiskSize,
            "spareCacheDiskCount": self.spareCacheDiskCount,
            "spareDiskType": self.spareDiskType,
            "spareDiskSize": self.spareDiskSize
        }
        contract.update({k: v for k, v in auto_params.items() if v is not None})
        return contract

    def _add_manual_params(self, contract: dict) -> dict:
        """Добавление параметров ручной конфигурации и конвертация set в list"""
        manual_params = {
            "mainDisks": self.mainDisks,
            "wrcDisks": self.wrcDisks,
            "rdcDisks": self.rdcDisks,
            "spareDisks": self.spareDisks
        }
        contract.update({k: v for k, v in manual_params.items() if v is not None})
        return contract


@dataclass
class PoolProps:
    guid: str
    status: str
    used: str
    free: str
    size: str
    disks: List[str]
    disks_groups_count: int
    removed_disks: List[str]
    mode: int
    raid: str
    rdcache: List[str]
    wrcache: List[str]
    spare: List[str]
    node: int
    dedupratio: str
    dataset_dedup: List[str]
    freeing: str
    reserved: int
    priority: int
    scan: Dict[str, str]

@dataclass
class PoolData:
    name: str
    type: str
    props: PoolProps
