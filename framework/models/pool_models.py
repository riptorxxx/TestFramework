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



# from dataclasses import dataclass, asdict
# from typing import Optional, Union, List, Dict
# from .base_models import BaseConfig
# from ..utils.serializer import Serializer
#
#
# @dataclass
# class PoolConfig(BaseConfig):
#     # Common parameters
#     name: Optional[str] = None
#     node: Optional[int] = None
#     raid_type: str = "raid1"
#     perfomance_type: int = 1
#     percentage: int = 10
#     priority: int = 0
#     auto_configure: bool = True
#
#     # Auto mode parameters
#     mainDisksCount: Optional[int] = None
#     mainGroupsCount: Optional[int] = None
#     mainDisksType: Optional[str] = None
#     mainDisksSize: Optional[int] = None
#     wrCacheDiskCount: Optional[int] = None
#     wrcDiskType: Optional[str] = None
#     wrcDiskSize: Optional[int] = None
#     rdCacheDiskCount: Optional[int] = None
#     rdcDiskType: Optional[str] = None
#     rdcDiskSize: Optional[int] = None
#     spareCacheDiskCount: Optional[int] = None
#     spareDiskType: Optional[str] = None
#     spareDiskSize: Optional[int] = None
#
#     # Manual mode parameters
#     mainDisks: Optional[Union[int, List[str]]] = None
#     wrcDisks: Optional[Union[int, List[str]]] = None
#     rdcDisks: Optional[Union[int, List[str]]] = None
#     spareDisks: Optional[Union[int, List[str]]] = None
#
#     # def to_request(self, dynamic_params: Dict) -> dict:
#     #     """Преобразует конфигурацию в формат API запроса"""
#     #     base_params = {
#     #         "name": dynamic_params.get('name', self.name),
#     #         "node": dynamic_params.get('node', self.node),
#     #         "raid_type": self.raid_type,
#     #         "perfomance_type": self.perfomance_type,
#     #         "percentage": self.percentage,
#     #         "priority": self.priority,
#     #         "auto_configure": self.auto_configure
#     #     }
#     #
#     #     if self.auto_configure:
#     #         auto_params = {k: v for k, v in asdict(self).items()
#     #                        if v is not None and k.endswith(('Count', 'Type', 'Size'))}
#     #         base_params.update(auto_params)
#     #     else:
#     #         manual_params = {k: v for k, v in asdict(self).items()
#     #                          if v is not None and k.endswith(('Disks',))}
#     #         base_params.update(manual_params)
#     #
#     #     return {k: v for k, v in base_params.items() if v is not None}
#
#
#     def prepare_contract(self, dynamic_params: Dict) -> dict:
#         contract = {
#             "name": dynamic_params.get('name', self.name),
#             "node": dynamic_params.get('node', self.node),
#             "raid_type": self.raid_type,
#             "perfomance_type": self.perfomance_type,
#             "percentage": self.percentage,
#             "priority": self.priority,
#             "auto_configure": self.auto_configure
#         }
#
#         if self.auto_configure:
#             auto_params = {
#                 "mainDisksCount": self.mainDisksCount,
#                 "mainGroupsCount": self.mainGroupsCount,
#                 "mainDisksType": self.mainDisksType,
#                 "mainDisksSize": self.mainDisksSize,
#                 "wrCacheDiskCount": self.wrCacheDiskCount,
#                 "wrcDiskType": self.wrcDiskType,
#                 "wrcDiskSize": self.wrcDiskSize,
#                 "rdCacheDiskCount": self.rdCacheDiskCount,
#                 "rdcDiskType": self.rdcDiskType,
#                 "rdcDiskSize": self.rdcDiskSize,
#                 "spareCacheDiskCount": self.spareCacheDiskCount,
#                 "spareDiskType": self.spareDiskType,
#                 "spareDiskSize": self.spareDiskSize
#             }
#             contract.update({k: v for k, v in auto_params.items() if v is not None})
#         else:
#             # Добавляем параметры из конфигурации
#             manual_params = {
#                 "mainDisks": self.mainDisks,
#                 "wrcDisks": self.wrcDisks,
#                 "rdcDisks": self.rdcDisks,
#                 "spareDisks": self.spareDisks
#             }
#             contract.update({k: v for k, v in manual_params.items() if v is not None})
#
#         return Serializer.serialize(contract)
