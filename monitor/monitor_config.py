
# Configuracion general

DIR_BASE = '/srv/CRM/procesar'
DIR_ERR = '/srv/CRM/error'
DIR_SUGAR = '/home/luis/Documentos/maipu/maipu-crm'
PLUGIN_DIRS = ['plugins/']
LOG_LEVEL = 'debug'



# Configuracion de los scripts a invocar segun el path del archivo importado

PATHS = [   ('/ventas/', 'importar_venta'),
            ('/ventas_batch/', 'importar_venta_batch'),
            ('/turnos/0', 'importar_turno'),
            ('/turnos/1', 'importar_turno'),
            ('/turnos/2', 'importar_turno'),
]



# Extras - no tocar

import logging
LOG_LEVELS = {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}

import sys
sys.path.append(DIR_SUGAR)
