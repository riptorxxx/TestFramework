from dataclasses import dataclass, asdict
from typing import Optional, Union, List
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


    @classmethod
    def create(cls, **kwargs) -> dict:
        """Create pool configuration dictionary"""
        return kwargs

    def to_request(self) -> dict:
        """Convert configuration to API request format"""
        data = super().to_request()
        if self.auto_configure:
            # Конфиг для автовыбора дисков
            return {k: v for k, v in data.items()
                    # Исключаем поля
                   if not k.startswith(('mainDisks', 'wrcDisks', 'rdcDisks', 'spareDisks'))
                    # Берём поля оканчивающиеся на
                   or k.endswith('Count')}
        # Конфиг для ручного выбора дисков
        return {k: v for k, v in data.items()
                # Исключаем поля
               if not k.endswith(('Count', 'Type', 'Size'))}

