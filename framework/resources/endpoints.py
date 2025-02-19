class ApiEndpoints:
    """API endpoints constants"""

    class Cluster:
        BASE = "/cluster"
        STATUS = "/cluster/status"

    class Pools:
        BASE = "/pools"                                             # Получить список пулов
        GET_POOL = "/pools/{pool_name}"                             # Получить пул
        CREATE_POOL = "/pools/{pool_name}"                          # Создать пул
        DELETE_POOL = "/pools/{pool_name}"                          # Удалить пул
        EXPAND_POOL = "/pools/{pool_name}/expand"                   # Расширить пул
        GET_IMPORT_POOLS = "/importview"                            # Получить список пулов для импорта
        IMPORT_POOL = "/pools/{pool_name}/import"                   # Импорт пула
        EXPORT_POOL = "/pools/{pool_name}/export"                   # Экспорт пула
        ADD_WRC = "/pools/{pool_name}/cache/write"                  # Добавить кэш на запись к пулу
        ADD_RDC = "/pools/{pool_name}/cache/read"                   # Добавить кэш на чтение к пулу
        ADD_SPARE = "/pools/{pool_name}/spare"                      # Добавить запасной диск к пулу
        CHANGE_DISK = "/pools/{pool_name}/disks/{disk}"             # Замена диска в пуле
        DELETE_WRC = "/pools/{pool_name}/cache/write/{disk}"        # Удалить кэш на запись в пуле
        DELETE_RDC = "/pools/{pool_name}/cache/read/{disk}"         # Удалить кэш на чтение в пуле
        DELETE_SPARE = "/pools/{pool_name}/spare/{disk}"            # Удалить запасной диск в пуле
        DELETE_DISKS = "/pools/{pool_name}/auxiliary/disks"         # Удалить несколько дисков по типу и по ID
        RESERV_POOL = "/pools/reserve"                              # Установить % резервирования в пуле


    class FileSystem:
        CREATE_FILESYSTEM = "/pools/{pool_name}/filesystems"        # Создание новой файловой системы


    class Volumes:
        CREATE_VOLUME = "/pools/{pool_name}/volumes"                # Создание тома