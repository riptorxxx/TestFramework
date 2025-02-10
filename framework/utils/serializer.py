from typing import Any, Dict, Optional, Type, TypeVar
from dataclasses import is_dataclass, asdict
import pytest
# from framework.models.pool_models import PoolConfig
# from framework.models.disk_models import DiskSelection, ClusterDisks

T = TypeVar('T')


class Serializer:
    current_test = None

    @staticmethod
    def is_negative_test() -> bool:
        """Определяет негативный тест по маркеру nc из pytest.ini"""
        if not Serializer.current_test:
            return False
        return Serializer.current_test.get_closest_marker('nc') is not None

    @staticmethod
    def serialize(data: Any, model_type: Optional[Type[T]] = None) -> Any:
        """
        Универсальный метод сериализации данных
        :param data: Данные для сериализации
        :param model_type: Тип модели для специальной обработки
        :return: Сериализованные данные
        """
        keep_none = Serializer.is_negative_test()
        return Serializer._serialize_impl(data, keep_none)

    @staticmethod
    def _serialize_impl(data: Any, keep_none: bool) -> Any:
        handlers = {
            type(None): lambda x: None if keep_none else None,
            dict: lambda x: Serializer._handle_dict(x, keep_none),
            list: lambda x: Serializer._handle_sequence(x, keep_none),
            tuple: lambda x: Serializer._handle_sequence(x, keep_none),
            set: lambda x: Serializer._handle_set(x, keep_none),
            (str, int, float, bool): lambda x: x
        }

        # Проверка на dataclass
        if is_dataclass(data):
            return Serializer._handle_dataclass(data, keep_none)

        # Проверка на to_dict
        if hasattr(data, 'to_dict'):
            return Serializer.serialize(data.to_dict())

        # Обработка примитивных типов
        for types, handler in handlers.items():
            if isinstance(data, types):
                return handler(data)

        # Fallback для неизвестных типов
        return str(data)

    @staticmethod
    def _handle_dataclass(data: Any, keep_none: bool) -> Dict:
        """Обработка dataclass объектов"""
        result = {}
        for key, value in asdict(data).items():
            if key.startswith('_'):
                continue
            serialized_value = Serializer._serialize_impl(value, keep_none)
            if serialized_value is not None or keep_none:
                result[key] = serialized_value
        return result

    @staticmethod
    def _handle_dict(data: Dict, keep_none: bool) -> Dict:
        """Обработка словарей"""
        return {
            key: Serializer._serialize_impl(value, keep_none)
            for key, value in data.items()
            if value is not None or keep_none
        }

    @staticmethod
    def _handle_sequence(data: Any, keep_none: bool) -> list:
        """Обработка последовательностей"""
        return [
            Serializer._serialize_impl(item, keep_none)
            for item in data
            if item is not None or keep_none
        ]

    @staticmethod
    def _handle_set(data: set, keep_none: bool) -> list:
        """Обработка множеств"""
        return Serializer._handle_sequence(list(data), keep_none)


class RequestSerializer:
    """Базовый класс для сериализации запросов"""

    @staticmethod
    def serialize_request(data: Any) -> Dict:
        return Serializer.serialize(data)


# from typing import Any, Dict, Optional
# from dataclasses import is_dataclass, asdict
# import pytest
# from framework.models.pool_models import PoolConfig
# from framework.models.disk_models import DiskSelection, ClusterDisks
#
#
# class Serializer:
#
#     current_test = None
#
#     @staticmethod
#     def is_negative_test() -> bool:
#         """Определяет негативный тест по маркеру nc из pytest.ini"""
#         if not Serializer.current_test:
#             return False
#         return Serializer.current_test.get_closest_marker('nc') is not None
#
#     @staticmethod
#     def serialize(data: Any) -> Any:
#         """
#         Универсальный метод сериализации данных с автоопределением режима
#         :param data: Данные для сериализации
#         :return: Сериализованные данные
#         """
#         keep_none = Serializer.is_negative_test()
#         return Serializer._serialize_impl(data, keep_none)
#
#     @staticmethod
#     def _serialize_impl(data: Any, keep_none: bool) -> Any:
#         if data is None:
#             return None if keep_none else None
#
#         if is_dataclass(data):
#             return Serializer._handle_dataclass(data, keep_none)
#
#         if isinstance(data, dict):
#             return Serializer._handle_dict(data, keep_none)
#
#         if isinstance(data, (list, tuple)):
#             return Serializer._handle_sequence(data, keep_none)
#
#         if isinstance(data, set):
#             return Serializer._handle_set(data, keep_none)
#
#         if isinstance(data, (str, int, float, bool)):
#             return data
#
#         if hasattr(data, 'to_dict'):
#             return Serializer.serialize(data.to_dict())
#
#         return str(data)
#
#     @staticmethod
#     def _handle_dataclass(data: Any, keep_none: bool) -> Dict:
#         """Обработка dataclass объектов"""
#         result = {}
#         for key, value in asdict(data).items():
#             serialized_value = Serializer._serialize_impl(value, keep_none)
#             if serialized_value is not None or keep_none:
#                 result[key] = serialized_value
#         return result
#
#     @staticmethod
#     def _handle_dict(data: Dict, keep_none: bool) -> Dict:
#         """Обработка словарей"""
#         result = {}
#         for key, value in data.items():
#             serialized_value = Serializer._serialize_impl(value, keep_none)
#             if serialized_value is not None or keep_none:
#                 result[key] = serialized_value
#         return result
#
#     @staticmethod
#     def _handle_sequence(data: Any, keep_none: bool) -> list:
#         """Обработка последовательностей"""
#         return [
#             Serializer._serialize_impl(item, keep_none)
#             for item in data
#             if item is not None or keep_none
#         ]
#
#     @staticmethod
#     def _handle_set(data: set, keep_none: bool) -> list:
#         """Обработка множеств"""
#         return Serializer._handle_sequence(list(data), keep_none)
#
#
# class PoolRequestSerializer:
#     @staticmethod
#     def to_request(
#             pool_config: PoolConfig,
#             disk_selection: Optional[DiskSelection] = None
#     ) -> Dict:
#         """
#         Формирует данные запроса для создания пула
#         :param pool_config: Конфигурация пула
#         :param disk_selection: Выбранные диски
#         :return: Данные для API запроса
#         """
#         request_data = Serializer.serialize(pool_config)
#
#         if disk_selection:
#             disk_data = Serializer.serialize(disk_selection)
#             request_data.update(disk_data)
#
#         return request_data
