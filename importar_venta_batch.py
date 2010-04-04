import monitor_config
import logging
import types
import sugar
import crm_config
import importar_venta
import datetime


# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("importar_venta_batch")

def procesar(instancia, pathname):

    # Leo el archivo de datos.
    arch_datos = open(pathname)
    datos = arch_datos.readlines()

    ahora = datetime.datetime.now()
    err_filename = ahora.isoformat()
    
    hubo_errores = False

    for linea in datos:
        try:
            ret = importar_venta.procesar_linea(instancia, linea)
        except sugar.ErrorSugar, descripcion:
            logger.error("Hubo error de tipo ErrorSugar: %s", str(descripcion))
            ret = False
        except ValueError:
            ret = False
        
        if(not ret):
            # Si hubo un error al procesar la linea del archivo
            if(not hubo_errores):
                errores = open(monitor_config.DIR_ERR + '/ventas_batch/' +\
                                err_filename, 'w')
            errores.write(linea)
            errores.flush()
            hubo_errores = True
            logger.error("Hubo error: salida a %s" % err_filename)
    
    if(hubo_errores):
        errores.close()
    else:
        logger.debug("No ocurrio ningun error. Aleluya.")
    
    return True


def obtener_instancia():
    # Me conecto a la instancia de SugarCRM.
    logger.debug("Conectando a instancia")
    instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Ventas', 'mm002_Marcas',
                                        'mm002_Modelo', 'mm002_Catalogos',
                                        'mm002_Tipo_venta', 'mm002_Sucursales',
                                        'Contacts', 'mm002_Encuestas'],
                    crm_config.LDAP_KEY, crm_config.LDAP_IV)

    return instancia


if __name__ == '__main__':
    import sys

    instancia = obtener_instancia()
    procesar(instancia, sys.argv[1])
    



