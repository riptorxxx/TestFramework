import json
from httpx import Response
from typing import Dict, List, Optional, Union
from framework.api.utils.generators import Generates
from framework.api.utils.retry import disk_operation_with_retry
from framework.api.models.pool_models import PoolConfig, PoolData, PoolProps
from .base_tools import BaseTools
from ..core.logger import logger
from ..resources.disks.disk_selector import DiskSelector
from ..resources.endpoints import ApiEndpoints


class PoolTools(BaseTools):
    def __init__(self, context):
        super().__init__(context)
        self._config: Optional[PoolConfig] = None
        self.current_pool = None
        self._pool_names: List[str] = []
        self._disk_selector = DiskSelector(self)

    def configure(self, config: Union[PoolConfig, dict]):
        if isinstance(config, PoolConfig):
            config = config.__dict__
        self._config = PoolConfig(**config)

    def validate(self):
        """валидируем состояние кластера перед началом работ с пулом"""
        self._context.tools_manager.cluster.validate()

    @disk_operation_with_retry()
    def create(self, **custom_params) -> dict:
        """Основной метод создания пула"""
        self.validate()
        # Формирует словарь с параметрами запроса
        request_data = self._prepare_request_data()

        # Отправляет POST запрос, получает объект Response
        response = self._make_create_request(request_data)

        # Преобразует Response в словарь:
        response_data = self._process_response(response)

        # Сохраняет информацию о текущем пуле в экземпляре класса
        self.current_pool = request_data
        # current_pool содержит финальный конфиг пула который уходит в request.
        logger.info(f"POOL => : {self.current_pool}")

        # Добавляет имя пула в список всех созданных пулов
        self._pool_names.append(request_data['name'])

        return response_data

    def _prepare_request_data(self) -> dict:
        """Подготавливаем запрос на создание пула"""
        if not self._config:
            self._config = PoolConfig()

        # Стратегия сама определит что делать на основе auto_configure
        disk_config = self._get_disk_configuration()

        request_data = self._config.to_request()
        request_data.update(self._get_dynamic_params())

        # Для manual режима добавляем выбранные диски в запрос
        if not self._config.auto_configure:
            request_data.update(disk_config)

        return request_data

    def _generate_pool_name(self) -> str:
        """Создаём уникальное имя для пула"""
        return f"{Generates.random_string(8)}"

    def _get_dynamic_params(self) -> dict:
        """Получаем динамические параметры для конфига пула"""
        current_node = self._context.tools_manager.connection.get_current_config()
        node_number = int(current_node.node.replace('NODE_', '')) if current_node else 1
        return {
            'node': node_number,
            'name': self._generate_pool_name() # Вынести хелперы в отдельный tool.
        }

    def _get_disk_configuration(self) -> dict:
        """Получить данные от кластера, конфигурацию дисков."""
        cluster_data = self._context.tools_manager.cluster.get_cluster_info(
            keys_to_extract=["name"]
        )

        return self._disk_selector.select_disks(
            cluster_data,
            self._config
        )

    def _make_create_request(self, request_data: Dict) -> Response:
        """Создаём API запрос на создание пула используя клиент из контекста"""
        return self._context.client.post(
            ApiEndpoints.Pools.CREATE_POOL.format(pool_name=request_data['name']),
            json=request_data
        )

    def _process_response(self, response: Response) -> dict:
        """Process API response"""
        if response.status_code != 201:
            raise ValueError(f"Unexpected status code. Failed to create pool. : {response.text}")

        # Handle empty response
        if not response.content:
            return {"name": self._config.name, "status": "created"}

        try:
            self.current_pool = response.json()
        except json.JSONDecodeError:
            self.current_pool = {"name": self._config.name, "status": "created"}

        return self.current_pool

    def delete_pool(self, pool_name: str) -> None:
        """Delete pool by name"""
        response = self._context.client.delete(
            ApiEndpoints.Pools.DELETE_POOL.format(pool_name=pool_name)
        )

        if response.status_code not in (200, 204):
            raise ValueError(f"Failed to delete pool: {response.text}")

        if pool_name in self._pool_names:
            self._pool_names.remove(pool_name)

        if self.current_pool and self.current_pool['name'] == pool_name:
            self.current_pool = None

    def cleanup(self):
        """Cleanup all created pools"""
        # for pool_name in self._pool_names[:]:
        #     self.delete_pool(pool_name)
        self._pool_names.clear()

    def get_pools(self):
        return self._context.client.get(ApiEndpoints.Pools.BASE)

    def get_pool_by_name(self, pool_name: str) -> dict:
        """Get pool configuration by name"""
        pools = self.get_pools().json()
        for pool in pools['pools']:
            if pool['name'] == pool_name:
                return pool
        raise ValueError(f"Pool {pool_name} not found")

    def expand_pool(self, pool_name: str):
        pass

    def get_pool_to_import(self):
        pass

    def _make_expansion_request(self, pool_name: str, request_data: Dict) -> Response:
        """Send pool expansion request"""
        return self._context.client.put(
            ApiEndpoints.Pools.EXPAND_POOL.format(pool_name=pool_name),
            json=request_data
        )

    @disk_operation_with_retry()
    def expand_pool(self, pool_name: str) -> Response:
        """Расширение существующего пула"""
        self.validate()

        # Получаем текущий пул
        pool_data = self.get_pool_by_name(pool_name)
        # Преобразуем приходящий словарь к PoolData
        current_pool = PoolData(
            name=pool_data['name'],
            type=pool_data['type'],
            props=PoolProps(**pool_data['props'])
        )

        # Получаем диски через стратегию расширения
        cluster_info = self._context.tools_manager.cluster.get_cluster_info()
        expansion_disks = self._disk_selector.select_disks_for_expansion(cluster_info, current_pool)

        # Преобразуем в нужный формат
        request_data = {
            'disks': list(expansion_disks['mainDisks'])
        }

        # Отправляем запрос на расширение
        response = self._make_expansion_request(
            pool_name=pool_name,
            request_data=request_data
        )

        return response
