from typing import Dict, Optional
from dataclasses import dataclass
import os
from dotenv import load_dotenv
from ..tools.base_tools import BaseTools
import logging


@dataclass
class ConnectionConfig:
    node: str
    url: str


class ConnectionTools(BaseTools):
    def __init__(self, context):
        super().__init__(context)
        load_dotenv()
        self._config: Optional[ConnectionConfig] = None
        self._available_nodes = self._load_available_nodes()
        self.logger = logging.getLogger(__name__)

    def configure(self, node: str = None) -> 'ConnectionTools':
        """Configure connection parameters"""
        node = node or "NODE_1"
        if node not in self._available_nodes:
            raise ValueError(f"Unknown node: {node}. Available nodes: {list(self._available_nodes.keys())}")

        url = self._available_nodes[node]
        self._config = ConnectionConfig(node=node, url=url)
        return self

    def switch_node(self, node: str) -> None:
        """Switch connection to different node"""
        if node not in self._available_nodes:
            raise ValueError(f"Unknown node: {node}")
        self.configure(node=node)

    def _load_available_nodes(self) -> Dict[str, str]:
        """Load all available nodes from environment variables"""
        nodes = {}
        for key, value in os.environ.items():
            if key.startswith('NODE_') and key.upper() == key:
                nodes[key] = value
        return nodes

    def get_current_config(self) -> ConnectionConfig:
        """Get current connection configuration"""
        return self._config

    def get_available_nodes(self) -> Dict[str, str]:
        """Get dictionary of available nodes"""
        return self._available_nodes.copy()

    def validate(self) -> bool:
        """Validate current connection configuration"""
        if not self._config:
            return False

        try:
            response = self._context.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            return False
