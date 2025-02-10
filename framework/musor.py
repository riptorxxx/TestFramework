def _get_disk_configuration(self) -> dict:
    """Get disk configuration using cluster data"""
    cluster_data = self._context.tools_manager.cluster.get_cluster_info(
        keys_to_extract=["name"]
    )

    return self._disk_selector.select_disks(
        cluster_data,
        self._config
    )

def _prepare_request_data(self) -> dict:
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