class DiskGroupStrategy:
    """Стратегия выбора групп дисков по заданным критериям"""

    def filter_by_type(self, groups: dict, disk_type: str) -> dict:
        """Фильтрация групп по типу диска"""
        return {k: v for k, v in groups.items() if k[1] == disk_type}

    def filter_by_params(self, groups: dict, disk_type: str, disk_size: int) -> dict:
        """Фильтрация групп по типу и размеру"""
        return {k: v for k, v in groups.items()
                if k[1] == disk_type and k[0] == disk_size}

    def apply_hdd_priority_strategy(self, groups: dict, count: int, used_disks: set) -> dict:
        """Применение стратегии с приоритетом HDD"""
        hdd_groups = self.filter_by_type(groups, "HDD")

        if self._has_enough_disks(hdd_groups, count, used_disks):
            return hdd_groups

        ssd_groups = self.filter_by_type(groups, "SSD")
        return {**hdd_groups, **ssd_groups}

    def _has_enough_disks(self, groups: dict, count: int, used_disks: set) -> bool:
        """Проверка наличия достаточного количества дисков"""
        return any(len(set(disks) - used_disks) >= count
                   for disks in groups.values())
