""" Словарь с ошибками сервера """

POOL_ERRORS = {
    'INVALID_DISK_COUNT_RAID1_MAIN': {
        'msg': 'invalid disk count, expected ≥ 2!',
        'code': 1087672872
    },
    'INVALID_DISK_COUNT_RAID5_MAIN': {
        'msg': 'invalid disk count, expected ≥ 3!',
        'code': 1087672872
    },
    'INVALID_DISK_COUNT_RAID6_MAIN': {
        'msg': 'invalid disk count, expected ≥ 4!',
        'code': 1087672872
    },
    'INVALID_DISK_COUNT_RAIDB3_MAIN': {
        'msg': 'invalid disk count, expected ≥ 5!',
        'code': 1087672872
    },
    'INVALID_WRC_DISK_COUNT': {
        'msg': 'invalid disk count for adding disks to wrcache, must be 2!',
        'code': 1076597288
    },
    'DIFFERENT_DISK_SIZES': {
        'msg': 'Main disks must be of the same size',
        'code': 1087672872
    },
    'DIFFERENT_DISK_TYPES': {
        'msg': 'Main disks must be of the same type',
        'code': 1087672873
    },
    'SPARE_SIZE_MISMATCH': {
        'msg': "Size or type of spare disk isn't equal general disks!",
        'code': 1076597800
    },
    'SPARE_TYPE_MISMATCH': {
        'msg': 'Spare disks type mismatch',
        'code': 1087672875
    },
    'WRC_SIZE_MISMATCH': {
        'msg': 'Write cache disks size mismatch',
        'code': 1087672876
    },
    'RDC_TYPE_MISMATCH': {
        'msg': 'Read cache disks type mismatch',
        'code': 1087672877
    }
}