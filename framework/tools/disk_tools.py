from typing import Set, List, Union
from framework.models.disk_models import DiskInfo
from framework.models.pool_models import PoolData
from framework.tools.base_tools import BaseTools
from framework.resources.disks.disk_selector import DiskSelector
from framework.utils.retry import disk_operation_with_retry


class DiskTools(BaseTools):
    """Tools for disk operations"""

    def __init__(self, context):
        super().__init__(context)
        self.disk_selector = DiskSelector(self)

    def validate(self):
        self._context.tools_manager.cluster.validate()

    @disk_operation_with_retry()
    def select_disks_for_pool(self, pool_config):
        """Select disks for pools creation"""
        self.validate()
        cluster_info = self._context.tools_manager.cluster.get_cluster_info()
        return self.disk_selector.select_disks(cluster_info, pool_config)
    #
    # @disk_operation_with_retry()
    # def select_disks_for_expansion(self, current_pool: dict) -> dict:
    #     """Select disks for pool expansion"""
    #     self.validate()
    #     cluster_info = self._context.tools_manager.cluster.get_cluster_info()
    #     pool_config = PoolConfig(**current_pool)
    #     return self.disk_selector.select_disks_for_expansion(cluster_info, pool_config)

    def select_disks_for_expansion(self, current_pool: PoolData) -> dict:
        """Выбор дисков для расширения пула"""
        self.validate()
        cluster_info = self._context.tools_manager.cluster.get_cluster_info()
        return self.disk_selector.select_disks_for_expansion(cluster_info, current_pool)

    # def matches_disks(self, disk1: DiskInfo, disk2: DiskInfo, criteria: List[str] = None) -> bool:
    #     """
    #     Сравнивает два диска по заданным критериям
    #
    #     Args:
    #         disk1: Первый диск для сравнения
    #         disk2: Второй диск для сравнения
    #         criteria: Список атрибутов для сравнения. Например: ['type', 'size', 'vendor']
    #                  Если не указан - сравнивает по type и size
    #
    #     Returns:
    #         bool: True если диски совпадают по всем критериям
    #     """
    #     # Если критерии не заданы - используем базовые
    #     if criteria is None:
    #         criteria = ['type', 'size']
    #
    #     # Проверяем равенство каждого атрибута из списка критериев
    #     return all(getattr(disk1, attr) == getattr(disk2, attr) for attr in criteria)
    #
    # def find_similar_disks(
    #         self,
    #         sample_disk_id: str,
    #         search_group: Union[List[str], Set[str]],
    #         criteria: List[str] = None,
    #         count: int = None
    # ) -> List[str]:
    #     """
    #     Находит диски похожие на образец в указанной группе
    #
    #     Args:
    #         sample_disk_id: ID диска-образца для сравнения
    #         search_group: Группа дисков для поиска (список ID дисков)
    #         criteria: Список атрибутов для сравнения. Например: ['type', 'size', 'vendor']
    #                  Если не указан - сравнивает по type и size
    #         count: Ограничение на количество возвращаемых результатов
    #                Если не указан - возвращает все совпадения
    #
    #     Returns:
    #         List[str]: Список ID дисков, соответствующих критериям
    #     """
    #     # Получаем актуальную информацию о кластере
    #     cluster_info = self._context.tools_manager.cluster.get_cluster_info()
    #
    #     # Создаем объект диска-образца
    #     sample_disk = DiskInfo(**cluster_info['disks_info'][sample_disk_id])
    #
    #     # Проверяем что группа поиска не пустая
    #     if not search_group:
    #         return []
    #
    #     matches = []
    #     # Проверяем каждый диск из группы поиска
    #     for disk_id in search_group:
    #         # Создаем объект текущего диска
    #         disk = DiskInfo(**cluster_info['disks_info'][disk_id])
    #         # Если диск соответствует критериям - добавляем его ID в результат
    #         if self.matches_disks(sample_disk, disk, criteria):
    #             matches.append(disk_id)
    #
    #     # Возвращаем результат с учетом ограничения count
    #     return matches[:count] if count else matches
