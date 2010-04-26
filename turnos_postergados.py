import sugar
import crm_config
import monitor_config
import logging

######################
# Con este script creo llamadas de reprogramacion para aquellos turnos del dia
# que no se hayan cumplido, por ausencia del vehiculo
######################


# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("turnos_postergados")


#def procesar(instancia, pathname):
#    

#    # Abro el archivo de datos.
#    arch_datos = open(pathname)
#    datos = arch_datos.readlines()

#    linea = datos[0]
#    datos = linea.split(';')

#    # Para cada turno a importar, hago una busqueda de Turnos por turno_id,
#    # por si los turnos fueron ingresados previamente
#    busq = instancia.modulos['mm002_Turnos'].buscar(turno_id=datos[0])
#    if len(busq) != 0:
#        # si hay algun resultado, uso el primero
#        objeto = busq[0]
#    else:
#        # Creo un objeto nuevo del modulo Turnos.
#        objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Turnos'])

#    # Defino la plantilla con los campos.
#    campos = ['turno_id', 'nombre_contacto', 'nombre_cliente',
#            'cliente_id', 'cliente_dni', 'telefono_uno',
#            'telefono_dos', 'dominio', 'fecha_turno',
#            'hora_turno', 'motivo_turno', 'asesor_codigo',
#            'asesor_nombre', 'fecha_entrega', 'hora_entrega', 'estado_turno',
#            'sucursales_codigo',
#            'marcas_codigo', 'marcas_descripcion', 'modelos_codigo', 'modelos_descripcion',
#            'catalogos_codigo', 'catalogos_descripcion', 'orden_id', 'garantia']
#    # hago copia y quito los elementos que no van al sugar
#    campos_utiles = []
#    for campo in campos:
#        campos_utiles.append(campo)
##    campos_utiles.remove('nombre_cliente')
#    campos_utiles.remove('cliente_dni')
#    campos_utiles.remove('marcas_descripcion')
#    campos_utiles.remove('modelos_descripcion')
#    campos_utiles.remove('catalogos_descripcion')


#    # Cargo todos los valores importados en el objeto que entrara en sugar.
#    inutiles = zip(campos, datos)
#    utiles = [inutil for inutil in inutiles if inutil[0] in campos_utiles]
#    for campo in utiles:
#        if campo[0] == 'garantia':
#            valor_checkbox = (lambda x: x == 'G')(campo[1])
#            logger.debug(campo[0] + ' -> ' + str(valor_checkbox))
#            objeto.modificar_campo(campo[0].rstrip(), valor_checkbox)
#        elif (campo[0] == 'fecha_entrega' or campo[0] == 'fecha_turno') and \
#                                    campo[1] == '00000000':
#            # No importo este campo, lo dejo en blanco
#            pass
#        else:
#            logger.debug(campo[0] + ' -> ' + unicode(campo[1].rstrip(),
#                                                              'iso-8859-1'))
#            objeto.importar_campo(campo[0].rstrip(), unicode(campo[1].rstrip(),
#                                                              'iso-8859-1'))

#    # Si el turno es en mas de 72hs, y estoy dando de alta el turno,
#    # indico que el operador del call debe llamar al "contacto"
#    #  0 es "Sin contacto"
#    #  1 es "Contacto fallido"
#    #  2 es "Contactado satisfactoriamente"
#    if pathname.split('/')[-1][0] == '0' and \
#        objeto.obtener_campo('fecha_turno') >= (datetime.datetime.now() +
#                                        datetime.timedelta(days=2)).timetuple():
#        objeto.importar_campo('estado_contacto', '0')
#    else:
#        objeto.importar_campo('estado_contacto', '2')

#    logger.debug("Objeto listo.")

#    # Verifico que todos los objetos externos referenciados (marca, modelo, etc...)
#    # existan en Sugar y sean unicos. En caso de que no existan, los creo. Y si no
#    # son unicos, uso el primero?.

#    # Primero, verifico que exista el cliente. Si no existe, lo creo
#    logger.debug("Buscando cliente.")
#    valor = objeto.obtener_campo('cliente_id').a_sugar()
#    res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
#    if len(res) == 0:
#        # No hay un cliente con ese id. Lo creo
#        logger.debug("No hay cliente cargado.")
#        contacto = sugar.ObjetoSugar(instancia.modulos['Contacts'])
#        contacto.importar_campo('last_name', unicode(datos[2], 'iso-8859-1'))
#        contacto.importar_campo('phone_home', datos[5])
#        contacto.importar_campo('phone_other', datos[6])
#        contacto.importar_campo('id_maipu_c', datos[3])
#        contacto.importar_campo('dni_numero_c', datos[4])
#        logger.debug("Grabando cliente.")
#        contacto.grabar()
#    else:
#        logger.debug("Existen %i copias del cliente." % len(res))
#        # Hay uno o mas. Elijo el primero
#        contacto = res[0]

#    contact_id = contacto.obtener_campo('id').a_sugar()
#    
#    # Voy a darle un valor al campo 'name', utilizando el ID del turno
#    logger.debug("Dando nombre al turno.")
#    operacion_id = objeto.obtener_campo('turno_id').a_sugar()
#    objeto.importar_campo('name', unicode(operacion_id, 'iso-8859-1'))



#    # Aqui ya estan creadas todas las entradas en Sugar de las cuales esta venta
#    # depende. Ya puedo agrear la venta a la base de datos.

#    logger.debug("Grabando un nuevo TURNO...")
#    logger.debug(objeto.grabar())

#    
##    logger.debug(pathname)
#    if pathname.split('/')[-1][0] == '4':
#        # Orden facturada. Agrego una encuesta de satisfaccion
#        encuesta = sugar.ObjetoSugar(instancia.modulos['mm002_Encuestas'])
#        encuesta.importar_campo('turno_id', operacion_id)
#        encuesta.importar_campo('tipo_encuesta', '0')
#        encuesta.importar_campo('encuesta_estado', 'No iniciada')
#        encuesta.importar_campo('name', unicode(operacion_id, 'iso-8859-1'))

#        # Defino la fecha tentativa de encuesta
#        
#        hoy = datetime.datetime.today()
#        encuesta.modificar_campo('fecha_tentativa_encuesta', (hoy + 
#                                    datetime.timedelta(days=7)).timetuple())
#        
#        encuesta.modificar_campo('fecha_facturacion', hoy.timetuple())

#        logger.debug("Grabando una nueva ENCUESTA...")
#        encuesta.grabar()

#        # Relaciono la encuesta creada con el cliente
#        instancia.relacionar(contacto, encuesta)

#    # Relaciono el turno tambien con el cliente, para que quede en su historia
#    instancia.relacionar(contacto, objeto)
#    
#    return True


def obtener_instancia():
    # Me conecto a la instancia de SugarCRM.
    instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Turnos', 'Calls', 'Contacts'],
                    crm_config.LDAP_KEY, crm_config.LDAP_IV)

    return instancia

if __name__ == '__main__':
    import sys
    import datetime

    hora_limite = int(sys.argv[1])
    # Chequeo argumento
    try:
        if hora_limite < 800 or hora_limite > 2000:
            raise ValueError
    except:
        print "Pasar entero como argumento. P. ej: 1300 o 1800"
        sys.exit(1)
    
    # Obtengo instancia
    instancia = obtener_instancia()

    # Transformo la fecha de hoy en el numero que el modulo de turnos entiende
    hoy = datetime.date.today().strftime('%Y%m%d')

    # Busco todos los turnos de hoy que tengan estado 1366 (no ingresaron aun)
    busq_todos = instancia.modulos['mm002_Turnos'].buscar(cantidad=1000,
                                        fecha_turno=hoy, estado_turno='1366')

    # Filtro los turnos, dejando aca solo los que tengan hora anterior a la 
    # pasada como argumento
    busq_ant = [turno for turno in busq_todos
                    if turno.obtener_campo('hora_turno').valor <= hora_limite]


    # Para todos los turnos de busq_ant, tengo que crear una llamada asociada
    # al cliente, que pida que se le llame para agendar un nuevo turno
    
    for turno in busq_ant:
        # Primero, verifico que exista el cliente. Si no existe, lo creo
        logger.debug("Buscando cliente.")
        valor = turno.obtener_campo('cliente_id').a_sugar()
        res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
        if len(res) == 0:
            # No hay un cliente con ese id. Lo creo
            logger.debug("No hay cliente cargado.")
            contacto = sugar.ObjetoSugar(instancia.modulos['Contacts'])
            contacto.importar_campo('last_name', 
                            turnos.obtener_campo('nombre_cliente').a_sugar())
            contacto.importar_campo('phone_home', 
                            turnos.obtener_campo('telefono_uno').a_sugar())
            contacto.importar_campo('phone_other', 
                            turnos.obtener_campo('telefono_dos').a_sugar())
            contacto.importar_campo('id_maipu_c', 
                            turnos.obtener_campo('cliente_id').a_sugar())
#            contacto.importar_campo('dni_numero_c', 
#                            turnos.obtener_campo('cliente_id').a_sugar())
            logger.debug("Grabando cliente.")
            contacto.grabar()
        else:
            logger.debug("Existen %i copias del cliente." % len(res))
            # Hay uno o mas. Elijo el primero
            contacto = res[0]
    
        contact_id = contacto.obtener_campo('id').a_sugar()


        # Creo la llamada nueva
        llamada = sugar.ObjetoSugar(instancia.modulos['Calls'])

        llamada.importar_campo('status', 'Planned')
        llamada.importar_campo('direction', 'Outbound')
        llamada.importar_campo('parent_type', u'Contacts')
        llamada.importar_campo('parent_id', contact_id)
        llamada.importar_campo('duration_hours', '0')
        llamada.importar_campo('duration_minutes', '5')
        llamada.importar_campo('name', u'Reprogramar turno')
        llamada.importar_campo('description', u"""Llamar al contacto %s para 
        reprogramar el turno de taller por motivo '%s'.
        """ % (turno.obtener_campo('nombre_contacto').a_sugar(), 
                turno.obtener_campo('motivo_turno').a_sugar()))
        
        llamada.grabar()

        logger.debug("Anulo turno en el CRM. Le pongo estado_turno=9999")
        turno.importar_campo('estado_turno', '9999')
        turno.grabar()

        print llamada.obtener_campo('id').a_sugar()


