from typing import Dict, List, Optional, Union
from framework.helpers.generators import Generates
from framework.helpers.retry import disk_operation_with_retry
from framework.models.pool_models import PoolConfig
from .base_tools import BaseTools
from ..core.logger import logger
from ..resources.disks.disk_selector import DiskSelector
from ..helpers.test_params import get_test_params
from httpx import Response



class PoolTools(BaseTools):
    def __init__(self, context):
        super().__init__(context)
        self._config: Optional[PoolConfig] = None
        self.current_pool = None
        self._pool_names: List[str] = []
        # self._disk_selector = self._context.tools_manager.disk_selector
        # Initialize disk_selector later when needed
        self._disk_selector = DiskSelector(self)


    @property
    def disk_selector(self):
        if self._disk_selector is None:
            self._disk_selector = self._context.tools_manager.disk_selector
        return self._disk_selector

    def configure(self, config: Union[PoolConfig, dict]):
        if isinstance(config, PoolConfig):
            config = config.__dict__
        self._config = PoolConfig(**config)

    # def configure(self, **kwargs) -> 'PoolTools':
    #     """Configure pool parameters"""
    #     self._config = PoolConfig(**kwargs)
    #     return self

    def validate(self):
        """Validate cluster state before pool operations"""
        self._context.tools_manager.cluster.validate()

    @disk_operation_with_retry()
    def create(self, **custom_params) -> dict:
        self.validate()
        request_data = self._prepare_request_data()
        response = self._make_request(request_data)
        return self._process_response(response)

    def _prepare_request_data(self) -> dict:
        if not self._config:
            self._config = PoolConfig()

        request_data = self._config.to_request()
        request_data.update(self._get_dynamic_params())

        if not self._config.auto_configure:
            request_data.update(self._get_disk_configuration())

        return request_data

    def _get_dynamic_params(self) -> dict:
        # Gets node number from already configured connection
        current_node = self._context.tools_manager.connection.get_current_config()
        node_number = int(current_node.node.replace('NODE_', '')) if current_node else 1
        return {
            'node': node_number,
            'name': self._generate_pool_name() # Вынести хелперы в отдельный tool.
        }

    def _get_disk_configuration(self) -> dict:
        cluster_data = self._context.tools_manager.cluster.get_cluster_info(
            keys_to_extract=get_test_params(self._context).get('keys_to_extract')
        )
        return self._disk_selector.select_disks(cluster_data, self._config)

    def _make_request(self, request_data: Dict) -> Response:
        """Make API request using context client"""
        return self._context.client.post(
            f"/pools/{request_data['name']}",
            json=request_data
        )

    def _process_response(self, response: Response) -> dict:
        """Process API response"""
        if response.status_code != 201:
            raise ValueError(f"Unexpected status code. Failed to create pool. : {response.text}")
        self.current_pool = response.json()
        return self.current_pool


    def _generate_pool_name(self) -> str:
        """Generate unique pool name"""
        return f"{Generates.random_string(8)}"

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

    # @disk_operation_with_retry()
    # def create(self, **custom_params) -> dict:
    #     """
    #     Create pool with automatic or custom parameters
    #
    #     Args:
    #         **custom_params: Optional parameters to override defaults
    #     """
    #     self.validate()
    #
    #     if not self._config and not custom_params:
    #         self._config = PoolConfig()
    #
    #     # Get current node from connection context
    #     current_node = self._context.tools_manager.connection.get_current_config()
    #     node_number = int(current_node.node.replace('NODE_', '')) if current_node else 1
    #
    #     # Get keys_to_extract from context if available
    #     keys_to_extract = get_test_params(self._context).get('keys_to_extract')
    #     logger.info(f"keys_to_extract: {keys_to_extract}")
    #
    #     # Pass keys_to_extract to get_cluster_info
    #     cluster_data = self._context.tools_manager.cluster.get_cluster_info(keys_to_extract=keys_to_extract)
    #     logger.info(f"cluster_data: {cluster_data}")
    #     selected_disks = self._disk_selector.select_disks(cluster_data, self._config)
    #     logger.info(f"Debug: selected_disks = {selected_disks}")
    #
    #     # Generate pool name
    #     pool_name = custom_params.get('name') or self._generate_pool_name()
    #     self._pool_names.append(pool_name)
    #
    #     # Prepare base parameters
    #     params = {
    #         'name': pool_name,
    #         'node': node_number,
    #         'raid_type': custom_params.get('raid_type', self._config.raid_type),
    #         'performance_type': self._config.perfomance_type,
    #         'percentage': self._config.percentage,
    #         'priority': self._config.priority,
    #         'auto_configure': self._config.auto_configure,
    #         'main_disks': selected_disks['main_disks'],
    #         'wrc_disks': selected_disks['wrc_disks'],
    #         'rdc_disks': selected_disks['rdc_disks'],
    #         'spare_disks': selected_disks['spare_disks']
    #     }
    #
    #     response = self._context.client.post(f"/pools/{pool_name}", json=params)
    #
    #     if response.status_code != 201:
    #         raise ValueError(f"Failed to create pool: {response.text}")
    #
    #     self.current_pool = response.json()
    #     return self.current_pool


    # def _select_disks_for_pool(self, cluster_data) -> tuple:
    #     if self._config.auto_configure:
    #         return self._disk_selector.select_disks_auto(
    #             cluster_data,
    #             main_type=self._config.main_disks_type,
    #             main_count=self._config.main_disks_count,
    #             wrc_type=self._config.wrc_disk_type,
    #             wrc_count=self._config.wr_cache_disk_count,
    #             rdc_type=self._config.rdc_disk_type,
    #             rdc_count=self._config.rd_cache_disk_count,
    #             spare_type=self._config.spare_disk_type,
    #             spare_count=self._config.spare_cache_disk_count
    #         )
    #     return self._disk_selector.select_disks_manual(
    #         cluster_data,
    #         main_disks=self._config.main_disks,
    #         wrc_disks=self._config.wrc_disks,
    #         rdc_disks=self._config.rdc_disks,
    #         spare_disks=self._config.spare_disks
    #     )


