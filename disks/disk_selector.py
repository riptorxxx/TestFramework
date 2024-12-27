import testit
from tests.api.helpers.retry import disk_operation_with_retry
from tests.api.tests.disks.disk_operation_context import DiskOperationContext
from tests.api.tests.pools.pools_helpers import PoolConfig


class DiskSelector:
    """Основной класс для выбора дисков"""

    @disk_operation_with_retry()
    def select_disks(self, test_context, pool_config: PoolConfig) -> tuple:
        """
        Выбирает диски для пула
        """
        context = DiskOperationContext(test_context, pool_config)
        result = context.execute_selection()

        self._update_context(test_context, result)

        with testit.step(f"Выбраны диски: {result}"):
            return result

    def _update_context(self, test_context, result: tuple):
        """Обновляет контекст теста результатами выбора дисков"""
        main_disks, wrc_disks, rdc_disks, spare_disks = result

        test_context.pool_data.update({
            'mainDisks': main_disks,
            'wrcDisks': wrc_disks,
            'rdcDisks': rdc_disks,
            'spareDisks': spare_disks
        })
        test_context.selected_disks = result
