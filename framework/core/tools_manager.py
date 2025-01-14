from typing import Dict, Type
from framework.tools.base_tools import BaseTools
from framework.tools.pool_tools import PoolTools
from framework.tools.disk_tools import DiskTools
from framework.tools.cluster_tools import ClusterTools
from framework.tools.auth_tools import AuthTools
from framework.tools.connection_tools import ConnectionTools


class ToolsManager:
    """Tools manager for test context"""

    def __init__(self, context):
        self._context = context
        self._tools: Dict[str, BaseTools] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool('pools', PoolTools)
        self.register_tool('disk', DiskTools)
        self.register_tool('cluster', ClusterTools)
        self.register_tool('auth', AuthTools)
        self.register_tool('connection', ConnectionTools)

    def register_tool(self, name: str, tool_class: Type[BaseTools]):
        self._tools[name] = tool_class(self._context)

    def get_tool(self, name: str) -> BaseTools:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not registered")
        return self._tools[name]

    @property
    def pool(self) -> PoolTools:
        return self.get_tool('pools')

    @property
    def disk(self) -> DiskTools:
        return self.get_tool('disk')

    @property
    def cluster(self) -> ClusterTools:
        return self.get_tool('cluster')

    @property
    def auth(self) -> AuthTools:
        return self.get_tool('auth')

    @property
    def connection(self) -> ConnectionTools:
        return self.get_tool('connection')
