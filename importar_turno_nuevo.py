import sugar
import crm_config
import monitor_config
import logging
import datetime

######################
# Con este script doy de alta un turno nuevo en el sugar, y le indico a los
# operadores del call que deben llamar al contacto (habra un dashlet en el
# sugar que presente los turnos del dia siguiente).
######################

# A quien le asigno la encuesta
usuario_asignado_n = 'eamuchastegui'
usuario_asignado_id = '4df5932a-1f1f-c9e9-402d-4bd1a040dbed'

# A quien le asigno los turnos
usuario_asignado_n_tur = 'ndeamicis'
usuario_asignado_id_tur = 'b017df97-18be-064a-a4ab-4bd1a04ff610'

# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("importar_turno")


def procesar(instancia, pathname):
    

    # Abro el archivo de datos.
    arch_datos = open(pathname)
    datos = arch_datos.readlines()

    linea = datos[0]
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
    campos_utiles.remove('cliente_dni')
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

    # Si el turno es en mas de 72hs, y estoy dando de alta el turno,
    # indico que el operador del call debe llamar al "contacto"
    if pathname.split('/')[-1][0] == '0' and \
        objeto.obtener_campo('fecha_turno').valor >= (datetime.datetime.now() +
                                        datetime.timedelta(days=2)).timetuple():
        objeto.importar_campo('estado_recordatorio', 'Sin contacto')
    else:
        # Auto listo, pongo estado_recordatorio en 'OK'
        objeto.importar_campo('estado_recordatorio', 'OK')


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
    # En realidad hago esto solamente cuando se factura la orden.
    if pathname.split('/')[-1][0] == '4' and not existe_cliente and \
        objeto.obtener_campo('cliente_id').a_sugar() != '0':
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

    
    # Voy a darle un valor al campo 'name', utilizando el ID del turno
    logger.debug("Dando nombre al turno.")
    operacion_id = objeto.obtener_campo('turno_id').a_sugar()
    objeto.importar_campo('name', unicode(operacion_id, 'iso-8859-1'))



    # Aqui ya estan creadas todas las entradas en Sugar de las cuales esta venta
    # depende. Ya puedo agrear la venta a la base de datos.

    logger.debug("Grabando un nuevo TURNO...")
    logger.debug(objeto.grabar())


    # Creo encuesta de satisfaccion si estoy en el estado 4    
    if pathname.split('/')[-1][0] == '4' and \
            len(instancia.modulos['mm002_Encuestas'].buscar(turno_id=operacion_id)) == 0:
        logger.debug("Es una orden facturada. No existia encuesta")
        # Orden facturada. Agrego una encuesta de satisfaccion
        encuesta = sugar.ObjetoSugar(instancia.modulos['mm002_Encuestas'])
        encuesta.importar_campo('turno_id', operacion_id)
        encuesta.importar_campo('tipo_encuesta', '0')
        encuesta.importar_campo('encuesta_estado', 'No iniciada')
        encuesta.importar_campo('name', unicode(operacion_id, 'iso-8859-1'))
        encuesta.importar_campo('assigned_user_name', usuario_asignado_n)
        encuesta.importar_campo('assigned_user_id', usuario_asignado_id)
        
        encuesta.importar_campo('marca', unicode(datos[18], 'iso-8859-1'))
        encuesta.importar_campo('modelo', unicode(datos[20], 'iso-8859-1'))
        # Defino la fecha tentativa de encuesta
        
        hoy = datetime.datetime.today()
        logger.debug("Hoy (fecha_facturacion): %s" % str(hoy))
        manana = hoy + datetime.timedelta(days=3)
        logger.debug("Maniana (fecha_tentativa_encuesta): %s" % str(manana))

        encuesta.modificar_campo('fecha_tentativa_encuesta', manana.timetuple())
        encuesta.modificar_campo('fecha_facturacion', hoy.timetuple())

        logger.debug("Grabando una nueva ENCUESTA...")
        logger.debug(encuesta.grabar())

        # Relaciono la encuesta creada con el cliente
        instancia.relacionar(contacto, encuesta)

    elif pathname.split('/')[-1][0] == '4':
        logger.debug("Es una orden facturada. Ya existia la encuesta")
    
    
    if existe_cliente:
        # Relaciono el turno tambien con el cliente, para que quede en su historia
        instancia.relacionar(contacto, objeto)
    
    return True


def obtener_instancia():
    # Me conecto a la instancia de SugarCRM.
    instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Turnos', 'mm002_Marcas',
                                        'mm002_Modelo', 'mm002_Encuestas',
                                        'Contacts'],
                    crm_config.LDAP_KEY, crm_config.LDAP_IV)

    return instancia

if __name__ == '__main__':
    import sys

    instancia = obtener_instancia()
    procesar(instancia, sys.argv[1])

