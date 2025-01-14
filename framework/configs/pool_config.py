from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class PoolConfig:
    """Pool configuration data class"""
    name: Optional[str] = None
    node: Optional[int] = None
    mainDisksType: Optional[str] = None
    mainDisksCount: Optional[int] = None
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
    performance_type: Optional[int] = None
    auto_configure: bool = False

    def to_request_data(self) -> dict:
        """Convert config to API request format"""
        data = asdict(self)
        # Remove None values and internal fields
        return {k: v for k, v in data.items()
                if v is not None and not k.startswith('_')}

    def update_disks(self, selected_disks: tuple):
        """Update config with selected disks"""
        main_disks, wrc_disks, rdc_disks, spare_disks = selected_disks
        self.mainDisks = main_disks
        self.wrcDisks = wrc_disks
        self.rdcDisks = rdc_disks
        self.spareDisks = spare_disks
