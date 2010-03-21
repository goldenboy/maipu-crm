import sugar
import crm_config
import monitor_config
import logging


# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("importar_cliente")


def procesar(instancia, pathname):

    # Leo el archivo de datos.
    arch_datos = open(pathname)
    datos = arch_datos.readlines()
    
    return procesar_linea(instancia, datos[0])
    

def procesar_linea(instancia, linea):

    # Creo un objeto nuevo del modulo Contacts.
    objeto = sugar.ObjetoSugar(instancia.modulos['Contacts'])

    # La lista 'campos' tiene los nombres de las columnas ordenadas.
    campos = ['id_maipu_c', 'last_name', 'birthdate', 'primary_address_street', 
            'domicilio_uno_numero_c', 'domicilio_uno_piso_c',
            'domicilio_uno_barrio_c', 'primary_address_city',
            'primary_address_state', 'primary_address_postalcode',
            'alt_address_street', 'domicilio_dos_numero_c',
            'domicilio_dos_piso_c', 'domicilio_dos_barrio_c',
            'alt_address_city', 'alt_address_state', 'alt_address_postalcode',
            'phone_home', 'phone_work', 'phone_mobile', 'phone_fax', 'email1',
            'dni_tipo_c', 'dni_numero_c', 'cuit_numero_c', 'nacionalidad_c',
            'condicion_iva_c', 'salutation', 'empresa_c', 'actividad_c',
            'profesion_c', 'estado_civil_c', 'sexo_c']
    
    datos = linea.split(',')

    # Cargo todos los valores importados en el objeto que entrara en sugar.
    for campo in zip(campos, datos):
        logger.debug(campo[0] + ' -> ' + campo[1])
        try:
            objeto.importar_campo(campo[0].rstrip(), unicode(campo[1].rstrip(),
                                                        'iso-8859.1'))
        except sugar.ErrorSugar:
            try:
                objeto.importar_campo(campo[0].rstrip(), campo[1].rstrip())
            except sugar.ErrorSugar:
                logger.error("No se puede importar el campo "+campo[0]+ ", con "+\
                        "valor "+campo[1]+".")

    logger.debug("Objeto listo.")
    try:
        logger.debug(objeto.grabar())
    except:
        logger.error("Error al grabar objeto.")
        return False
    logger.debug("1 objeto grabado.")
    
    return True

if __name__ == '__main__':
    import sys
    
    # Me conecto a la instancia de SugarCRM.
    logger.debug("Conectando a instancia")
    instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['Contacts'], crm_config.LDAP_KEY,
                    crm_config.LDAP_IV)
    
    procesar(instancia, sys.argv[1])

