import pytest
import testit
from tests.api.api_client import logger
from tests.api.helpers.extractors import TestExtractor
from tests.api.api_client import request_to_curl
from dataclasses import dataclass, field
from typing import Optional, List, Union
from tests.api.helpers.retry import disk_operation_with_retry
from tests.api.helpers.timer import timer


"""
Модуль для работы с пулами дисков.
Предоставляет функционал для выбора и управления дисками в пуле хранения данных.
"""


@dataclass
class PoolConfig:
    """
    Класс для конфигурации пула дисков.

    Attributes:
        name (str): Имя пула.
        node (int): Идентификатор узла.
        raid_type (str): Тип RAID (по умолчанию "raid1").
        perfomance_type (int): Тип производительности (по умолчанию 1).
        percentage (int): Процент использования дисков (по умолчанию 10).
        priority (int): Приоритет пула (по умолчанию 0).
        auto_configure (bool): Флаг автоматической конфигурации.
        mainDisksCount (Optional[int]): Количество основных дисков.
        mainGroupsCount (Optional[int]): Количество групп дисков.
        mainDisksType (Optional[str]): Тип основных дисков.
        mainDisksSize (Optional[int]): Размер основных дисков.
        wrCacheDiskCount (Optional[int]): Количество дисков кэша записи.
        wrcDiskType (Optional[str]): Тип дисков кэша записи.
        wrcDiskSize (Optional[int]): Размер дисков кэша записи.
        rdCacheDiskCount (Optional[int]): Количество дисков кэша чтения.
        rdcDiskType (Optional[str]): Тип дисков кэша чтения.
        rdcDiskSize (Optional[int]): Размер дисков кэша чтения.
        spareCacheDiskCount (Optional[int]): Количество запасных дисков кэша.
        spareDiskType (Optional[str]): Тип запасных дисков.
        spareDiskSize (Optional[int]): Размер запасных дисков.
    """

    def __str__(self):
        """Обрезает неиспользуемые параметры в отчёте TestIT"""
        return str(self.to_request_data())

    # Common pools parameters
    name: str = None
    node: int = None
    raid_type: str = "raid1"
    perfomance_type: int = 1
    percentage: int = 10
    priority: int = 0
    auto_configure: bool = field(init=False)

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

    def __post_init__(self):
        """Флаг определения режима выбора дисков (manual, auto)"""
        self.auto_configure = self.mainDisksCount is not None

    def to_request_data(self) -> dict:
        """
        Преобразует параметры конфигурации в формат запроса.

        Returns:
            dict: Данные конфигурации в виде словаря для отправки в запросе.
        """

        data = {
            "name": self.name,
            "node": self.node,
            "raid_type": self.raid_type,
            "perfomance_type": self.perfomance_type,
            "percentage": self.percentage,
            "priority": self.priority,
            "auto_configure": self.auto_configure
        }
        if self.auto_configure:
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
            data.update({k: v for k, v in auto_params.items() if v is not None})
        else:
            manual_params = {
                "mainDisks": self.mainDisks,
                "wrcDisks": self.wrcDisks,
                "rdcDisks": self.rdcDisks,
                "spareDisks": self.spareDisks
            }
            data.update({k: v for k, v in manual_params.items() if v is not None})

        return data


class PoolsHelper:
    """
    Класс для помощи в:
     создании конфигурации для пулов,
     выборе необходимых дисков для создания пулов,
     подготовки запросов для создания пулов.

    Attributes:
        MIN_MAIN_DISKS (int): Минимальное количество основных дисков (2).
        MIN_WRC_DISKS (int): Минимальное количество дисков кэша записи (2).
        MAX_RETRIES (int): Максимальное количество попыток выбора дисков (3).
        RETRY_DELAY (int): Задержка между попытками в секундах (5).
    """

    MIN_MAIN_DISKS = 2
    MIN_WRC_DISKS = 2
    MAX_RETRIES = 3
    RETRY_DELAY = 5

    def __init__(self):
        """Инициализация помощника с пустым множеством использованных дисков."""
        self.used_disks = set()


    @staticmethod
    def create_pool_config(raid_type: str, disks_count: int, groups_count: int,
                           disk_type: str, disk_size: int = None,
                           perfomance_type: int = 1,
                           percentage: int = 10,
                           priority: int = 0,
                           wrc_disk_count: int = None,
                           wrc_disk_type: str = None,
                           wrc_disk_size: int = None,
                           rdc_disk_count: int = None,
                           rdc_disk_type: str = None,
                           rdc_disk_size: int = None,
                           spare_disk_count: int = None,
                           spare_disk_type: str = None,
                           spare_disk_size: int = None) -> PoolConfig:
        """
        Создание конфигурации пула
        """
        return PoolConfig(
            raid_type=raid_type,
            perfomance_type=perfomance_type,
            percentage=percentage,
            priority=priority,
            mainDisksCount=disks_count,
            mainGroupsCount=groups_count,
            mainDisksType=disk_type,
            mainDisksSize=disk_size,
            wrCacheDiskCount=wrc_disk_count,
            wrcDiskType=wrc_disk_type,
            wrcDiskSize=wrc_disk_size,
            rdCacheDiskCount=rdc_disk_count,
            rdcDiskType=rdc_disk_type,
            rdcDiskSize=rdc_disk_size,
            spareCacheDiskCount=spare_disk_count,
            spareDiskType=spare_disk_type,
            spareDiskSize=spare_disk_size
        )

    def prepare_pool_config(self, test_context, pool_config: PoolConfig):
        """
        Подготавливает конфигурацию пула.

        Args:
            test_context: Объект контекста теста, содержащий информацию о тесте.
            pool_config (PoolConfig): Конфигурация пула.

        Returns:
            dict: Данные о созданной конфигурации пула.
        """

        with testit.step(f"Подготовка конфигурации пула"):
            test_context.prepare_pool_config(pool_config)

        with testit.step(f"Конфигурация создана: {test_context.pool_data}"):
            return test_context.pool_data


    def _get_priority_disk_type(self, pool_config: PoolConfig) -> str:
        """
        Определяет приоритетный тип дисков на основе perfomance_type

        Args:
            pool_config: Конфигурация пула
        Returns:
            str: Приоритетный тип диска ("SSD" или None для стандартного поведения)
        """
        return "SSD" if pool_config.perfomance_type == 0 else None


    def select_disks(self, test_context, pool_config: PoolConfig):
        """
        Выбирает диски для пула на основе конфигурации.

        Args:
            test_context: Объект контекста теста, содержащий информацию о тесте.
            pool_config (PoolConfig): Конфигурация пула.

        Returns:
            tuple: Выбранные диски для создания пула.

        Raises:
            ValueError: Если выбор дисков не удался или недостаточно подходящих дисков.
        """
        if pool_config.auto_configure:
            test_context.selected_disks = test_context.pool_data
            return test_context.selected_disks

        result = self._select_disks_for_pool(test_context, pool_config)
        main_disks, wrc_disks, rdc_disks, spare_disks = result

        test_context.pool_data.update({
            'mainDisks': main_disks,
            'wrcDisks': wrc_disks,
            'rdcDisks': rdc_disks,
            'spareDisks': spare_disks
        })
        test_context.selected_disks = (main_disks, wrc_disks, rdc_disks, spare_disks)

        with testit.step(f"Выбраны диски: {test_context.selected_disks}"):
            return test_context.selected_disks


    def prepare_request(self, test_context):
        """Подготовка данных запроса"""

        test_context.headers = test_context.request_params['headers']

        with testit.step(f"Сформирован запрос: {test_context.pool_data}"):
            return test_context.pool_data

    def create_pool(self, test_context):
        """
        Создает пул на основе подготовленных данных.

        Args:
            test_context: Объект контекста теста, содержащий информацию о запросе и окружении.

        Returns:
            Response: Ответ от API после создания пула.

        Logs:
            Информация о результате создания пула и статусе ответа.

        Raises:
            Exception: Если создание пула завершилось неудачей с ошибкой статуса ответа.
        """

        # Создаём curl для отображения в TestIT
        curl_command = request_to_curl(
            method='POST',
            url=f"{test_context.base_url}{test_context.post_endpoint}",
            headers=test_context.headers,
            json_data=test_context.pool_data
        )
        testit.addMessage(f"{curl_command}")
        # Выполняем создание пула
        response = test_context.client.post(
            test_context.post_endpoint,
            test_context.pool_data,
            test_context.headers
        )
        with testit.step(f"{response}"):
            if response.status_code == 201:
                logger.info(f"Пул: {test_context.pool_name} успешно создан!")
            else:
                logger.error(f"Ошибка создания пула: {test_context.pool_name}. Status: {response.status_code}")

            return response

    def reset_state(self):
        """
        Очищает набор перед каждым запуском теста, гарантируя,
           что каждый тест начнётся с чистого листа.
        """

        self.used_disks = set()

    # '''____________________________________ ЛОГИКА ВЫБОРА ДИСКОВ ___________________________________________'''

    def select_disks_single(self, extractor, test_context, pool_config):
        """
           Единичная попытка выбора дисков для негативного сценария (для негативных сценариев).

           Args:
               extractor: Экстрактор данных из тестового контекста.
               test_context: Контекст теста с необходимыми данными.
               pool_config (PoolConfig): Конфигурация пула.

           Returns: tuple: Выбранные диски для создания пула.
        """

        cluster_info = extractor.extract_cluster_info(
            test_context.cluster_info,
            test_context.keys_to_extract
        )
        return self._try_select_disks(cluster_info, pool_config)

    @disk_operation_with_retry()
    def _try_select_disks(self, cluster_info, pool_config):
        """
          Попытка выбора дисков из текущей информации о кластере.

          Args:
              cluster_info (dict): Информация о доступных дисках в кластере.
              pool_config (PoolConfig): Конфигурация пула.

          Raises: ValueError: Если недостаточно подходящих дисков по заданным критериям.
          Returns: tuple: Выбранные основные и кэш-диски и запасные диски для создания пула.
        """

        used_disks = set()
        priority_type = self._get_priority_disk_type(pool_config)

        # Получаем количество дисков из конфигурации пула
        main_count = pool_config.mainDisks if isinstance(pool_config.mainDisks, int) else len(pool_config.mainDisks)
        wrc_count = pool_config.wrcDisks if isinstance(pool_config.wrcDisks, int) else len(
            pool_config.wrcDisks) if pool_config.wrcDisks else 0
        rdc_count = pool_config.rdcDisks if isinstance(pool_config.rdcDisks, int) else len(
            pool_config.rdcDisks) if pool_config.rdcDisks else 0
        spare_count = pool_config.spareDisks if isinstance(pool_config.spareDisks, int) else len(
            pool_config.spareDisks) if pool_config.spareDisks else 0

        # Пропускаем валидацию для негативных сценариев(pytest.mark.nc)
        if not hasattr(pytest, "skip_validation"):
            if main_count < self.MIN_MAIN_DISKS:
                logger.error(
                    f"Количество основных дисков должно быть не менее {self.MIN_MAIN_DISKS}, получено {main_count}")
                raise ValueError(
                    f"Количество основных дисков должно быть не менее {self.MIN_MAIN_DISKS}, получено {main_count}")
            if 0 < wrc_count < self.MIN_WRC_DISKS:
                logger.error(
                    f"Количество дисков кэша записи должно быть не менее {self.MIN_WRC_DISKS}, получено {wrc_count}")
                raise ValueError(
                    f"Количество дисков кэша записи должно быть не менее {self.MIN_WRC_DISKS}, получено {wrc_count}")

        # Выбор основных дисков
        main_disks_info = self._select_main_disks(
            cluster_info['free_disks_by_size_and_type'],
            main_count,
            used_disks,
            priority_type=priority_type
        )

        main_disks = main_disks_info['disks']
        main_disk_size = main_disks_info['size']
        main_disk_type = main_disks_info['type']
        used_disks.update(main_disks)
        logger.info(f"Выбранные основные диски: {main_disks} (Тип: {main_disk_type}, Размер: {main_disk_size})")

        # Выбор дисков кэша записи
        wrc_disks = self._select_cache_disks(
            cluster_info,
            wrc_count,
            "write cache",
            used_disks
        )
        used_disks.update(wrc_disks)
        if wrc_disks:
            logger.info(f"Выбранные диски кэша записи: {wrc_disks}")

        # Выбор дисков кэша чтения
        rdc_disks = self._select_cache_disks(
            cluster_info,
            rdc_count,
            "read cache",
            used_disks
        )
        used_disks.update(rdc_disks)
        if rdc_disks:
            logger.info(f"Выбранные диски кэша чтения: {rdc_disks}")

        # Выбор резервных дисков
        spare_disks = self._select_spare_disks(
            cluster_info['free_disks_by_size_and_type'],
            spare_count,
            main_disk_size,
            main_disk_type,
            used_disks
        )
        if spare_disks:
            logger.info(f"Выбранные резервные диски: {spare_disks} (соответствуют типу и размеру основных дисков)")

        return main_disks, wrc_disks, rdc_disks, spare_disks


    def _get_disk_groups(self, cluster_info):
        """Group available disks by type and size"""
        disk_groups = {}

        for (size, dtype), disks in cluster_info['free_disks_by_size_and_type'].items():
            key = (dtype, size)
            disk_groups[key] = list(disks)

        # Sort groups by disk count
        sorted_groups = sorted(disk_groups.items(),
                               key=lambda x: len(x[1]),
                               reverse=True)

        return sorted_groups


    def _select_optimal_disk_group(self, sorted_groups, required_count, disk_type=None):
        """Select optimal disk group based on count and type requirements"""
        for (group_type, size), disks in sorted_groups:
            if disk_type and group_type != disk_type:
                continue
            if len(disks) >= required_count:
                return {'type': group_type, 'size': size, 'disks': disks}

        raise ValueError(f"No suitable disk group found for required count: {required_count}")

    def _select_main_disks(self, disks_by_size_and_type, count, used_disks, disk_type=None, disk_size=None,
                           priority_type=None):
        """
            Выбор основных дисков с приоритетом HDD.

            Эта функция фильтрует доступные диски по заданному типу и размеру и выбирает
            необходимые основные диски из пула. Если указаны тип и размер диска,
            производится фильтрация по этим параметрам. Если нет, используется приоритет
            для выбора HDD.

            Args:
                disks_by_size_and_type (dict): Словарь доступных дисков, сгруппированных по размеру и типу.
                count (int): Количество необходимых основных дисков.
                used_disks (set): Множество уже использованных дисков.
                disk_type (str, optional): Тип диска для фильтрации (например, "HDD" или "SSD").
                disk_size (int, optional): Размер диска для фильтрации.

            Returns:
                dict: Словарь с выбранными дисками, их размером и типом. Формат:
                      {'disks': [список выбранных дисков], 'size': размер выбранного диска, 'type': тип выбранного диска}.

            Raises: ValueError: Если недостаточно одинаковых дисков для основной группы.
        """
        if count == 0:
            return {'disks': [], 'size': None, 'type': None}

        # For performance_type=0, use only SSD
        if priority_type == "SSD":
            filtered_groups = {k: v for k, v in disks_by_size_and_type.items()
                               if k[1] == "SSD"}
        # For manual mode with specific type and size
        elif disk_type and disk_size:
            filtered_groups = {k: v for k, v in disks_by_size_and_type.items()
                               if k[1] == disk_type and k[0] == disk_size}
        # For manual mode without specific requirements - prioritize HDD
        else:
            # First try HDD disks
            hdd_groups = {k: v for k, v in disks_by_size_and_type.items()
                          if k[1] == "HDD"}

            # If no HDDs available or not enough, include SSD groups
            if not any(len(set(disks) - used_disks) >= count for disks in hdd_groups.values()):
                ssd_groups = {k: v for k, v in disks_by_size_and_type.items()
                              if k[1] == "SSD"}
                filtered_groups = {**hdd_groups, **ssd_groups}
            else:
                filtered_groups = hdd_groups

        # Select disks from filtered groups
        for (size, disk_type), disks in filtered_groups.items():
            available = list(set(disks) - used_disks)
            if len(available) >= count:
                selected = available[:count]
                return {'disks': selected, 'size': size, 'type': disk_type}

        raise ValueError(f"Not enough identical disks for main group. Required: {count}")


    def _select_cache_disks(self, cluster_info, count, cache_type, used_disks, disk_size=None):
        """
            Выбор кэш-дисков (только SSD одинакового размера).

            Эта функция выбирает кэш-диски из доступных SSD-дисков в зависимости от типа кэша
            (запись или чтение) и возвращает необходимые кэш-диски.

            Args:
                cluster_info (dict): Информация о кластере с доступными дисками.
                count (int): Количество необходимых кэш-дисков.
                cache_type (str): Тип кэша ("write cache" или "read cache").
                used_disks (set): Множество уже использованных дисков.
                disk_size (int, optional): Размер диска для фильтрации.

            Returns:  list: Список выбранных кэш-дисков.
            Raises: ValueError: Если недостаточно подходящих SSD-дисков одного размера для указанного типа кэша.
        """
        if count == 0:
            return []

        # Enforce SSD requirement for cache disks
        if cache_type == "write cache":
            available_disks = [d for d in cluster_info['free_for_wc']
                               if d not in used_disks and
                               cluster_info['disks_info'][d]['type'] == "SSD"]
        else:
            available_disks = [d for d in cluster_info['free_disks']
                               if d not in used_disks and
                               cluster_info['disks_info'][d]['type'] == "SSD"]

        # Group by size and select largest group
        disks_by_size = {}
        for disk in available_disks:
            size = cluster_info['disks_info'][disk]['size']
            disks_by_size.setdefault(size, []).append(disk)

        sorted_groups = sorted(disks_by_size.items(), key=lambda x: len(x[1]), reverse=True)

        for size, disks in sorted_groups:
            if len(disks) >= count:
                return disks[:count]

        raise ValueError(f"Not enough SSD disks for {cache_type}. Required: {count}")


    def _select_spare_disks(self, disks_by_size_and_type, count, main_size, main_type, used_disks):
        """
            Выбор запасных дисков того же размера и типа, что и основные.

            Эта функция выбирает запасные диски из доступных на основе параметров основных
            дисков и возвращает необходимые запасные диски.

            Args:
                disks_by_size_and_type (dict): Словарь доступных запасных дисков,
                                                сгруппированных по размеру и типу.
                count (int): Количество необходимых запасных дисков.
                main_size (int): Размер основных дисков.
                main_type (str): Тип основных дисков.
                used_disks (set): Множество уже использованных дисков.

            Returns: list: Список выбранных запасных дисков.
            Raises: ValueError: Если недостаточно запасных дисков соответствующего размера и типа.
        """

        if count == 0:
            return []

        key = (main_size, main_type)
        if key not in disks_by_size_and_type:
            raise ValueError(f"Не найдены запасные диски с размером {main_size} и типом {main_type}")

        available = list(set(disks_by_size_and_type[key]) - used_disks)
        if len(available) < count:
            raise ValueError(
                f"Недостаточно запасных дисков, соответствующих параметрам основных дисков. Требуется: {count}")

        return available[:count]

    def _select_disks_auto(self, cluster_info, pool_config):
        """
            Выбор дисков в автоматическом режиме.

            Эта функция выбирает необходимые основные и кэш-диски в автоматическом режиме
            на основе конфигурации пула и информации о кластере.

            Args:
                cluster_info (dict): Информация о кластере с доступными дисками.
                pool_config (dict): Конфигурация пула с параметрами выбора.

            Returns:
                tuple: Кортеж из списков выбранных основных дисков,
                       кэш-дисков записи и чтения и запасных дисков.

            Raises: ValueError: Если недостаточно основных или запасных дисков.
       """

        used_disks = set()
        priority_type = self._get_priority_disk_type(pool_config)

        # Вычисляем общее необходимое количество основных дисков
        total_main_disks = pool_config["mainDisksCount"] * pool_config["mainGroupsCount"]

        # Если установлен perfomance_type=0, переопределяем тип дисков на SSD
        if priority_type == "SSD":
            pool_config["mainDisksType"] = "SSD"

        # Выбираем основные диски по типу и размеру
        main_disks = []
        for (size, disk_type), disks in cluster_info['free_disks_by_size_and_type'].items():
            if (disk_type == pool_config["mainDisksType"] and
                    (pool_config["mainDisksSize"] is None or size == pool_config["mainDisksSize"])):
                available = list(set(disks) - used_disks)
                if len(available) >= total_main_disks:
                    main_disks = available[:total_main_disks]
                    used_disks.update(main_disks)
                    break

        if not main_disks:
            raise ValueError(
                f"Недостаточно основных дисков типа {pool_config['mainDisksType']} и размера {pool_config['mainDisksSize']}")

        # Используем существующую логику выбора кэш-дисков
        wrc_disks = self._select_cache_disks(
            cluster_info,
            pool_config["wrCacheDiskCount"],
            "write cache",
            used_disks
        )
        used_disks.update(wrc_disks)

        rdc_disks = self._select_cache_disks(
            cluster_info,
            pool_config["rdCacheDiskCount"],
            "read cache",
            used_disks
        )
        used_disks.update(rdc_disks)

        # Выбираем запасные диски, соответствующие параметрам основных дисков
        spare_disks = self._select_spare_disks(
            cluster_info['free_disks_by_size_and_type'],
            pool_config["spareCacheDiskCount"],
            pool_config["mainDisksSize"],
            pool_config["mainDisksType"],
            used_disks
        )

        return main_disks, wrc_disks, rdc_disks, spare_disks

    def get_disk_size_by_type(self, cluster_info, disk_type):
        """Returns minimum disk size for specified type from available disks"""
        disks_by_size = cluster_info['free_disks_by_size_and_type']
        sizes = [size for (size, type_), _ in disks_by_size.items() if type_ == disk_type]
        return min(sizes) if sizes else None

    @disk_operation_with_retry()
    def _select_disks_for_pool(self, test_context, pool_config: PoolConfig):
        """
        Выбирает диски для пула с учетом типа теста (позитивный/негативный).

        Args:
            test_context: Контекст теста с необходимыми данными
            pool_config: Параметры конфигурации для создания пула

        Returns:
            tuple: Выбранные диски для создания пула
        """
        extractor = TestExtractor()
        cluster_info = extractor.extract_cluster_info(
            test_context.cluster_info,
            test_context.keys_to_extract
        )

        # Для негативных тестов декоратор retry не будет выполнять повторные попытки
        return self._try_select_disks(cluster_info, pool_config)


