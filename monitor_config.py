
# Configuracion general

DIR_BASE = '/srv/CRM/procesar'
DIR_ERR = '/srv/CRM/error'
PLUGIN_DIRS = ['./']
LOG_LEVEL = 'debug'



# Configuracion de los scripts a invocar segun el path del archivo importado

PATHS = [   ('/ventas/', 'importar_venta'),
            ('/ventas_batch/', 'importar_venta_batch'),
            ('/cliente/', 'importar_cliente'),
            ('/cliente_batch/', 'importar_cliente_batch'),
            ('/turnos/0', 'importar_turno_nuevo'),
            ('/turnos/2', 'importar_turno_nuevo'),
            ('/turnos/4', 'importar_turno_nuevo'),
]



# Extras - no tocar

import logging
LOG_LEVELS = {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}

