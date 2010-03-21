import monitor_config
import logging
import types
import sugar
import crm_config
import importar_cliente
import datetime


# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("importar_cliente_batch")

def procesar(instancia, pathname):

    # Leo el archivo de datos.
    arch_datos = open(pathname)
    datos = arch_datos.readlines()

    ahora = datetime.datetime.now()
    err_filename = ahora.isoformat()
    
    hubo_errores = False

    for linea in datos:
        try:
            ret = importar_cliente.procesar_linea(instancia, linea)
        except:
#            logger.error("Hubo error grave: salida a %s" % err_filename)
            ret = False
        
        if(not ret):
            # Si hubo un error al procesar la linea del archivo
            if(not hubo_errores):
                errores = open(monitor_config.DIR_ERR + '/cliente_batch_' +\
                                err_filename, 'w')
            errores.write(linea)
            errores.flush()
            hubo_errores = True
            logger.error("Hubo error: salida a %s" % err_filename)
    
    if(hubo_errores):
        errores.close()
    
    
    return True


if __name__ == '__main__':
    import sys

    # Me conecto a la instancia de SugarCRM.
    logger.debug("Conectando a instancia")
    instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['Contacts'], crm_config.LDAP_KEY,
                    crm_config.LDAP_IV)

    procesar(instancia, sys.argv[1])



