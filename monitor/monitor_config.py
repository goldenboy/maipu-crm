
# Configuracion general

DIR_BASE = '/srv/CRM/procesar'
DIR_ERR = '/srv/CRM/error'
PLUGIN_DIRS = ['plugins/']
LOG_LEVEL = 'debug'



# Configuracion de los scripts a invocar segun el path del archivo importado

PATHS = [('/ventas/', 'importar_venta'),
]



# Extras - no tocar

import logging
LOG_LEVELS = {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}


