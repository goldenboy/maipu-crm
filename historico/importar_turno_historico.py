import sugar
import crm_config
import monitor_config
import logging
import datetime

######################
# Con este script doy de alta un turno viejo en el sugar para que quede en el
# historial del cliente
######################

# A quien le asigno los turnos
usuario_asignado_n_tur = 'ndeamicis'
usuario_asignado_id_tur = 'b017df97-18be-064a-a4ab-4bd1a04ff610'

# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("turno_historico")


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
                errores = open('turno_historico-' + err_filename, 'w')
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

    # Para cada turno a importar, hago una busqueda de Turnos por turno_id,
    # por si los turnos fueron ingresados previamente
    busq = instancia.modulos['mm002_Turnos'].buscar(turno_id=datos[0])
    if len(busq) != 0:
        # si hay algun resultado, uso el primero
        objeto = busq[0]
    else:
        # Creo un objeto nuevo del modulo Turnos.
        objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Turnos'])

    # Defino la plantilla con los campos.
    campos = ['turno_id', 'nombre_contacto', 'nombre_cliente',
            'cliente_id', 'cliente_dni', 'telefono_uno',
            'telefono_dos', 'dominio', 'fecha_turno',
            'hora_turno', 'motivo_turno', 'asesor_codigo',
            'asesor_nombre', 'fecha_entrega', 'hora_entrega', 'estado_turno',
            'sucursales_codigo',
            'marcas_codigo', 'marcas_descripcion', 'modelos_codigo', 'modelos_descripcion',
            'catalogos_codigo', 'catalogos_descripcion', 'orden_id', 'garantia']
    # hago copia y quito los elementos que no van al sugar
    campos_utiles = []
    for campo in campos:
        campos_utiles.append(campo)
#    campos_utiles.remove('nombre_cliente')
#    campos_utiles.remove('cliente_dni')
#    campos_utiles.remove('marcas_descripcion')
#    campos_utiles.remove('modelos_descripcion')
#    campos_utiles.remove('catalogos_descripcion')


    # Cargo todos los valores importados en el objeto que entrara en sugar.
    inutiles = zip(campos, datos)
    utiles = [inutil for inutil in inutiles if inutil[0] in campos_utiles]
    for campo in utiles:
        if campo[0] == 'garantia':
            valor_checkbox = (lambda x: x == 'G')(campo[1])
            logger.debug(campo[0] + ' -> ' + str(valor_checkbox))
            objeto.modificar_campo(campo[0].rstrip(), valor_checkbox)
        elif (campo[0] == 'fecha_entrega' or campo[0] == 'fecha_turno') and \
                                    campo[1] == '00000000':
            # No importo este campo, lo dejo en blanco
            pass
        else:
            logger.debug(campo[0] + ' -> ' + unicode(campo[1].rstrip(),
                                                              'iso-8859-1'))
            objeto.importar_campo(campo[0].rstrip(), unicode(campo[1].rstrip(),
                                                              'iso-8859-1'))

    objeto.importar_campo('assigned_user_name', usuario_asignado_n_tur)
    objeto.importar_campo('assigned_user_id', usuario_asignado_id_tur)
    logger.debug("Objeto listo.")

    # Verifico que todos los objetos externos referenciados (marca, modelo, etc...)
    # existan en Sugar y sean unicos. En caso de que no existan, los creo. Y si no
    # son unicos, uso el primero?.

    # Primero, verifico que exista el cliente.
    
    logger.debug("Buscando cliente")
    valor = objeto.obtener_campo('cliente_id').a_sugar()
    if valor == '0':
        logger.debug("No hay dato de cliente cargado en el turno aun")
        existe_cliente = False
    else:
        res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
        if len(res) == 0:
            existe_cliente = False
        else:
            existe_cliente = True
            logger.debug("Existen %i copias del cliente." % len(res))
            # Hay uno o mas. Elijo el primero
            contacto = res[0]
    
    
    # Si no existe el cliente, lo creo.
    if not existe_cliente and objeto.obtener_campo('cliente_id').a_sugar() != '0':
        # No hay un cliente con ese id. Lo creo
        logger.debug("No hay cliente cargado.")
        contacto = sugar.ObjetoSugar(instancia.modulos['Contacts'])
        contacto.importar_campo('last_name', unicode(datos[2], 'iso-8859-1'))
        contacto.importar_campo('phone_home', datos[5])
        contacto.importar_campo('phone_other', datos[6])
        contacto.importar_campo('id_maipu_c', datos[3])
        contacto.importar_campo('dni_numero_c', datos[4])
        logger.debug("Grabando cliente.")
        contacto.grabar()
        
        existe_cliente = True

    
    # Voy a darle un valor al campo 'name', utilizando el ID del turno
    logger.debug("Dando nombre al turno.")
    operacion_id = objeto.obtener_campo('turno_id').a_sugar()
    objeto.importar_campo('name', unicode(operacion_id, 'iso-8859-1'))



    # Aqui ya estan creadas todas las entradas en Sugar de las cuales este
    # turno depende. Ya puedo agrear el turno a la base de datos.

    logger.debug("Grabando un nuevo TURNO...")
    logger.debug(objeto.grabar())

    if existe_cliente:
        # Relaciono el turno tambien con el cliente, para que quede en su historia
        instancia.relacionar(contacto, objeto)
    
    return True


def obtener_instancia():
    # Me conecto a la instancia de SugarCRM.
    instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Turnos', 'mm002_Marcas',
                                        'mm002_Modelo', 'mm002_Encuestas',
                                        'Contacts', 'Calls'],
                    crm_config.LDAP_KEY, crm_config.LDAP_IV)

    return instancia

if __name__ == '__main__':
    import sys

    instancia = obtener_instancia()
    procesar(instancia, sys.argv[1])

