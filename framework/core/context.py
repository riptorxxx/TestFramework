from framework.core.tools_manager import ToolsManager


class TestContext:
    """Main test framework context"""

    def __init__(self, client, base_url, cluster_info=None, keys_to_extract=None):
        self.client = client
        self.base_url = base_url
        # self.request_params = request_params
        self.cluster_info = cluster_info
        self.keys_to_extract = keys_to_extract or []
        self.tools_manager = ToolsManager(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def cleanup(self):
        """Cleanup resources after test execution"""
        if hasattr(self.tools_manager.pool, 'cleanup'):
            self.tools_manager.pool.cleanup()
