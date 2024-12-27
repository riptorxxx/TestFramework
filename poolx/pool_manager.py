from tests.api.tests.poolx.pool_models import PoolConfig
from tests.api.tests.poolx.pool_constants import *
from tests.api.api_client import logger


class PoolManager:
    @staticmethod
    def create_pool_config(**kwargs) -> PoolConfig:
        """Creates pool configuration with provided parameters"""
        config = PoolConfig(**kwargs)
        logger.info(f"Pool configuration: {config}")
        return config

    @staticmethod
    def validate_disk_counts(main_count: int, wrc_count: int) -> None:
        """Validates disk counts for pool creation"""
        if main_count < MIN_MAIN_DISKS:
            raise ValueError(f"Main disks count must be at least {MIN_MAIN_DISKS}, got {main_count}")
        if 0 < wrc_count < MIN_WRC_DISKS:
            raise ValueError(f"Write cache disks count must be at least {MIN_WRC_DISKS}, got {wrc_count}")
