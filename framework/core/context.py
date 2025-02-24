from framework.core.tools_manager import ToolsManager



class TestContext:
    """Main test framework context"""

    def __init__(self, client, base_url, request=None):
        self.client = client
        self.base_url = base_url
        self.request = request
        self.tools_manager: ToolsManager = ToolsManager(self)
        '''Если вдруг нужно будет хранить контекст:'''
        # self.cluster_info = None
        # self.keys_to_extract = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def cleanup(self):
        """Cleanup resources after test execution"""
        if hasattr(self.tools_manager.pool, 'cleanup'):
            self.tools_manager.pool.cleanup()
