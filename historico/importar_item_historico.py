import sugar
import crm_config
import monitor_config
import logging
import datetime

######################
# Con este script doy de alta un item viejo en el sugar para que quede en el
# historial del cliente
######################

# Moneda
currency_id = '9f4c22ed-f82e-9aa2-5f77-4c28f762e851'

# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("item_historico")


def procesar(instancia, pathname):

    # Leo el archivo de datos.
    arch_datos = open(pathname)
    datos = arch_datos.readlines()

    ahora = datetime.datetime.now()
    err_filename = ahora.isoformat()
    
    hubo_errores = False

    for linea in datos:
        try:
            ret = procesar_linea(instancia, linea)
        except sugar.ErrorSugar, descripcion:
            logger.error("Hubo error de tipo ErrorSugar: %s", str(descripcion))
            ret = False
        except ValueError:
            ret = False
        
        if(not ret):
            # Si hubo un error al procesar la linea del archivo
            if(not hubo_errores):
                errores = open('item_historico-' + err_filename, 'w')
            errores.write(linea)
            errores.flush()
            hubo_errores = True
            logger.error("Hubo error: salida a %s" % err_filename)
    
    if(hubo_errores):
        errores.close()
    else:
        logger.debug("No ocurrio ningun error. Aleluya.")
    
    return True



def procesar_linea(instancia, linea):
    
    datos = linea.split(';')

    # [3] => Seguros
    # [2] => Tarjetas
    # [1] => Accesorios
    
    if datos[6] == '3':
        modulo_item = 'mm002_Seguros'
        tuplas = [('numero_orden', datos[0]), ('cliente_id', datos[1]),
                    ('fecha_facturacion', datos[2]), ('description', datos[4]),
                    ('importe', datos[5])]
    elif datos[6] == '2':
        modulo_item = 'mm002_Tarjetas'
        tuplas = [('numero_orden', datos[0]), ('cliente_id', datos[1]),
                    ('fecha_facturacion', datos[2]), ('description', datos[4])]
    else:
        modulo_item = 'mm002_Accesorios'
        tuplas = [('numero_orden', datos[0]), ('cliente_id', datos[1]),
                    ('fecha_facturacion', datos[2]), ('marca_codigo', datos[3]),
                    ('description', datos[4]), ('importe', datos[5])]
    
    # Para cada item a importar, hago una busqueda por 
    # numero_orden, por si los items fueron ingresados previamente
    busq = instancia.modulos[modulo_item].buscar(numero_orden=datos[0])
    if len(busq) != 0:
        # si hay algun resultado, uso el primero
        objeto = busq[0]
    else:
        # Creo un objeto nuevo del modulo del item.
        objeto = sugar.ObjetoSugar(instancia.modulos[modulo_item])


    # Cargo todos los valores importados en el objeto que entrara en sugar.
    for campo in tuplas:
        if campo[0].startswith('fecha') and campo[1] == '00000000':
            # No importo este campo, lo dejo en blanco
            pass
        else:
            logger.debug(campo[0] + ' -> ' + unicode(campo[1].rstrip(),
                                                              'iso-8859-1'))
            objeto.importar_campo(campo[0], unicode(campo[1].rstrip(),
                                                              'iso-8859-1'))


    # Verifico que todos los contactos referenciados existan en Sugar y sean
    # unicos. En caso de que no sean unicos, uso el primero?.
    
    logger.debug("Buscando cliente")
    valor = objeto.obtener_campo('cliente_id').a_sugar()
    if valor == '0':
        logger.debug("No hay dato de cliente cargado en el accesorio")
        existe_cliente = False
    else:
        res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
        if len(res) == 0:
            existe_cliente = False
            logger.debug("No existe cliente con ese id.")
        else:
            existe_cliente = True
            logger.debug("Existen %i copias del cliente." % len(res))
            # Hay uno o mas. Elijo el primero
            contacto = res[0]
    

    # Luego veo que la marca este cargada, y si lo esta, agrego la descripcion
    # al accesorio (si el objeto es un accesorio).
    if modulo_item == 'mm002_Accesorios':
        valor = objeto.obtener_campo('marca_codigo').a_sugar()
        res = instancia.modulos['mm002_Marcas'].buscar(marcas_codigo=valor)
        if len(res) > 0:
            # Agarro la primera marca con ese codigo
            marca = res[0]
        
            marca_descripcion = marca.obtener_campo('marcas_descripcion').a_sugar()
        
            # Cargo la descripcion de la marca en el accesorio
            objeto.importar_campo('marca_descripcion', unicode(marca_descripcion))


    # Voy a darle un valor al campo 'name', utilizando la descripcion del item.
    logger.debug("Dando nombre al item.")
    nombre = objeto.obtener_campo('description').a_sugar()
    objeto.importar_campo('name', unicode(nombre))



    # Aqui ya estan creadas todas las entradas en Sugar de las cuales este
    # item depende. Ya puedo agrear el item a la base de datos.
    if modulo_item != 'mm002_Tarjetas':
        objeto.importar_campo('currency_id', currency_id)
    logger.debug("Objeto listo.")

    logger.debug("Grabando un nuevo ITEM...")
    logger.debug(objeto.grabar())

    if existe_cliente:
        # Relaciono el turno tambien con el cliente, para que quede en su historia
        instancia.relacionar(contacto, objeto)
    
    return True


def obtener_instancia():
    # Me conecto a la instancia de SugarCRM.
    instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Accesorios', 'mm002_Tarjetas',
                                'mm002_Seguros', 'mm002_Marcas', 'Contacts'],
                    crm_config.LDAP_KEY, crm_config.LDAP_IV)

    return instancia

if __name__ == '__main__':
    import sys

    instancia = obtener_instancia()
    procesar(instancia, sys.argv[1])

