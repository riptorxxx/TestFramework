import json
from typing import Dict, List, Optional, Union
from framework.utils.generators import Generates
from framework.utils.retry import disk_operation_with_retry
from framework.models.pool_models import PoolConfig
from .base_tools import BaseTools
from ..core.logger import logger
from ..resources.disks.disk_selector import DiskSelector
from ..utils.test_params import get_test_params
from httpx import Response


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
        response = self._make_request(request_data)

        # Преобразует Response в словарь:
        response_data = self._process_response(response)

        # Сохраняет информацию о текущем пуле в экземпляре класса
        self.current_pool = request_data

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
        """Get disk configuration using cluster data"""
        cluster_data = self._context.tools_manager.cluster.get_cluster_info(
            keys_to_extract=["name"]
        )

        return self._disk_selector.select_disks(
            cluster_data,
            self._config
        )

    def _make_request(self, request_data: Dict) -> Response:
        """Создаём API запрос используя клиент из контекста"""
        return self._context.client.post(
            f"/pools/{request_data['name']}",
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
        response = self._context.client.delete(f"/pools/{pool_name}")

        if response.status_code not in (200, 204):
            raise ValueError(f"Failed to delete pool: {response.text}")

        if pool_name in self._pool_names:
            self._pool_names.remove(pool_name)

        if self.current_pool and self.current_pool['name'] == pool_name:
            self.current_pool = None

    def cleanup(self):
        """Cleanup all created pools"""
        for pool_name in self._pool_names[:]:
            self.delete_pool(pool_name)
        self._pool_names.clear()
