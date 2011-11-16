import sugar
import crm_config
import monitor_config
import logging
import datetime
import time
import calendar

# Moneda

currency_id = '9f4c22ed-f82e-9aa2-5f77-4c28f762e851'

# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("importar_venta")

def llamada_prueba_manejo(instancia, contacto, operacion_id, venta):

    usuario_asignado_name = 'jastudillo'
    usuario_asignado_id = 'e2b4a923-6279-53ce-66f0-4de3b91bad97'
    # Guardo el ID de sugar para mas tarde
    contacto_id = contacto.obtener_campo('id').a_sugar()

    marca = venta.obtener_campo('marcas_descripcion').a_sugar()
    llamada_name = 'Prueba de manejo %s - %s'%(operacion_id, marca)

    res = instancia.modulos['Calls'].buscar(parent_id=contacto_id, name=llamada_name)
    if len(res) > 0:
        logger.debug("Ya exite una llamada de prueba de manejo")
        return

    # Creo la llamada nueva
    llamada = sugar.ObjetoSugar(instancia.modulos['Calls'])
    logger.debug("Creo nueva llamada de prueba de manejo...")

    llamada.importar_campo('status', 'Planned')
    llamada.importar_campo('assigned_user_name', usuario_asignado_name)
    llamada.importar_campo('assigned_user_id', usuario_asignado_id)
    llamada.importar_campo('direction', 'Outbound')
    llamada.importar_campo('parent_type', u'Contacts')
    llamada.importar_campo('parent_id', contacto_id)
    llamada.importar_campo('duration_hours', '0')
    llamada.importar_campo('duration_minutes', '5')


    # Fecha de llamada de prueba de manejo = now+1hs
    fecha_venta = venta.obtener_campo('fecha_venta').valor
    dia_venta = datetime.datetime.fromtimestamp(time.mktime(fecha_venta))
    logger.debug("Prueba_Manejo: Fecha venta -> %s"%(dia_venta.isoformat(' ')))
    hora = datetime.datetime.time(datetime.datetime.now())
    logger.debug("Prueba_Manejo: Hora actual -> %s"%(hora))
    
    # Fecha de llamada de prueba de manejo = fecha_venta + 1 dia
    delta_hora = datetime.timedelta(days=1, hours=hora.hour, minutes=hora.minute)
    dia_llamada = dia_venta+delta_hora
    logger.debug("Prueba_Manejo: Hora llamada -> %s "%(dia_llamada.isoformat(' ')))
    llamada.modificar_campo('date_start', ((dia_llamada).timetuple()))

    llamada.importar_campo('name', u'%s'%(llamada_name))

    llamada.grabar()
    logger.debug("Grabo nueva llamada de prueba de manejo...")

    # Relaciono al contacto con la llamada
    logger.debug("Relaciono llamada de prueba de manejo con Contacto")
    instancia.relacionar(contacto, llamada)


def procesar(instancia, pathname):

    # Leo el archivo de datos.
    arch_datos = open(pathname)
    datos = arch_datos.readlines()
    
    return procesar_linea(instancia, datos[0])


def procesar_linea(instancia, linea):
    
    # A quien le asigno la encuesta
    usuario_asignado_n = 'eamuchastegui'
    usuario_asignado_id = '4df5932a-1f1f-c9e9-402d-4bd1a040dbed'

    PRUEBA_MANEJO = False
    FECHA_VENTA_PRUEBA_MANEJO = False

    # Leo el archivo de datos.
    datos = linea.split(';')

    # Si no hay operacion_id, ignoro este archivo
    if datos[0].strip() == '':
        logger.debug('Venta sin ID de operacion. Probablemente entrega a reventa.')
	return True

    # Creo un objeto nuevo del modulo Ventas.
    operacion_id=datos[0]
    busq = instancia.modulos['mm002_Ventas'].buscar(operacion_id=datos[0])
    if len(busq) != 0:
        # si hay algun resultado, uso el primero
        objeto = busq[0]
    else:
        # Creo un objeto nuevo del modulo Ventas.
        objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Ventas'])

    # Defino la plantilla con los campos.
    campos = ['operacion_id', 'id_maipu_cliente', 'nombre_cliente', 'marcas_codigo',
            'marcas_descripcion', 'modelos_codigo', 'modelos_descripcion',
            'catalogos_codigo', 'catalogos_descripcion',
            'fecha_venta', 'tipo_venta_codigo', 'tipo_venta_descripcion',
            'vendedor_codigo', 'vendedor_nombre', 'sucursales_codigo',
            'sucursales_descripcion', 'gestor_codigo', 'gestor_nombre',
            'patenta_maipu', 'importe', 'fecha_entrega', 'plan_grupo',
            'plan_orden', 'dominio', 'fecha_patentamiento', 'fecha_apertura_c',
            'fecha_reserva_c', 'entrega_vehiculo_c', 'entregador_codigo',
            'entregador_nombre', 'codigo_reventa_c', 'nombre_reventa_c', 
            'comision_reventa_c']

    # Cargo todos los valores importados en el objeto que entrara en sugar.
    hoy = datetime.date.today().isoformat()
    fecha_limite = (datetime.date.today()-datetime.timedelta(days=7)).isoformat()
    for campo in zip(campos, datos):
	# Si la fecha de entrega no es valida, entonces seteo flag de creacion de llamada
	if campo[0] == 'fecha_entrega':
            try:
                if not (int(campo[1].strip()) > 0 ):
                    PRUEBA_MANEJO = True
                    logger.debug("Debo crear llamada de prueba de manejo.")
            except ValueError:
                PRUEBA_MANEJO = True
                logger.debug("Debo crear llamada de prueba de manejo.")
        logger.debug(campo[0] + ' -> ' + unicode(campo[1], 'iso-8859-1'))
        if campo[0] == 'patenta_maipu' and campo[1] == 'M':
            objeto.importar_campo(campo[0], '1')
        elif campo[0] == 'patenta_maipu' and campo[1] != 'M':
            objeto.importar_campo(campo[0], '0')
        elif campo[0] == 'fecha_venta':
            objeto.importar_campo(campo[0], unicode(campo[1].rstrip(),
                                                            'iso-8859-1'))

            fecha_venta= datetime.date.fromtimestamp(
                time.mktime(time.strptime(campo[1],"%Y%m%d"))).isoformat()
            if (fecha_limite <= fecha_venta <= hoy):
                logger.debug("Fecha venta entre %s y %s"%(fecha_limite, hoy))
                FECHA_VENTA_PRUEBA_MANEJO = True
        elif (campo[0].startswith('fecha')) and campo[1] == '00000000':
            # No importo el campo, lo dejo en blanco
            pass
        else:
            objeto.importar_campo(campo[0], unicode(campo[1].rstrip(),
                                                            'iso-8859-1'))

    objeto.importar_campo('currency_id', currency_id)
    logger.debug("Objeto listo.")

    # Verifico que todos los objetos externos referenciados (marca, modelo, etc...)
    # existan en Sugar y sean unicos. En caso de que no existan, los creo. Y si no
    # son unicos, salgo emitiendo un error.

    # Primero, verifico que exista el cliente, y si no lo esta, lo agrego
    valor = objeto.obtener_campo('id_maipu_cliente').a_sugar()
    res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
    if len(res) > 1:
        logger.warn('Existen clientes duplicados con ese ID')
        contacto = res[0]
    elif len(res) == 1:
        contacto = res[0]
    elif len(res) == 0:
        # Debo crear un objeto cliente nuevo y agregarlo.
        obj_nuevo = sugar.ObjetoSugar(instancia.modulos['Contacts'])
        obj_nuevo.importar_campo('id_maipu_c', valor)
        obj_nuevo.importar_campo('last_name',
                        objeto.obtener_campo('nombre_cliente').a_sugar())
        logger.debug("Grabando un nuevo cliente...")
        obj_nuevo.grabar()
        contacto = obj_nuevo
        

    # Guardo el ID de sugar para mas tarde
    contact_id = contacto.obtener_campo('id').a_sugar()

    # Luego veo que la marca este cargada, y si no lo esta, la agrego.
    valor = objeto.obtener_campo('marcas_codigo').a_sugar()
    res = instancia.modulos['mm002_Marcas'].buscar(marcas_codigo=valor)
    if len(res) > 1:
        raise sugar.ErrorSugar('Hay marcas con ID duplicado')
    elif len(res) == 0:
        # Debo crear un objeto marca nuevo y agregarlo.
        obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Marcas'])
        obj_nuevo.importar_campo('marcas_codigo', valor)
        obj_nuevo.importar_campo('name',
                        objeto.obtener_campo('marcas_descripcion').a_sugar())
        obj_nuevo.importar_campo('marcas_descripcion',
                        objeto.obtener_campo('marcas_descripcion').a_sugar())
        logger.debug("Grabando una nueva Marca...")
        obj_nuevo.grabar()


    # Luego hago lo mismo con el modelo
    valor_marca = valor
    valor = objeto.obtener_campo('modelos_codigo').a_sugar()
    res = instancia.modulos['mm002_Modelo'].buscar(modelos_codigo=valor, marcas_codigo=valor_marca)
    if len(res) > 1:
        raise sugar.ErrorSugar('Hay modelos con ID duplicado')
    elif len(res) == 0:
        # Debo crear un objeto modelo nuevo y agregarlo.
        obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Modelo'])
        obj_nuevo.importar_campo('modelos_codigo', valor)
        obj_nuevo.importar_campo('modelos_descripcion',
                        objeto.obtener_campo('modelos_descripcion').a_sugar())
        obj_nuevo.importar_campo('name',
                        objeto.obtener_campo('modelos_descripcion').a_sugar())
        obj_nuevo.importar_campo('marcas_codigo',
                        objeto.obtener_campo('marcas_codigo').a_sugar())
        logger.debug("Grabando un nuevo Modelo...")
        obj_nuevo.grabar()

    # Luego hago lo mismo con el catalogo
    valor_modelo = valor
    valor = objeto.obtener_campo('catalogos_codigo').a_sugar()
    res = instancia.modulos['mm002_Catalogos'].buscar(modelos_codigo=valor_modelo, marcas_codigo=valor_marca, catalogos_codigo=valor)
    if len(res) > 1:
        raise sugar.ErrorSugar('Hay catalogos con ID duplicado')
    elif len(res) == 0:
        # Debo crear un objeto catalogo nuevo y agregarlo.
        obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Catalogos'])
        obj_nuevo.importar_campo('modelos_codigo', valor_modelo)
        obj_nuevo.importar_campo('marcas_codigo', valor_marca)
        obj_nuevo.importar_campo('catalogos_codigo', valor)
        obj_nuevo.importar_campo('catalogos_descripcion',
                        objeto.obtener_campo('catalogos_descripcion').a_sugar())
        cat_desc = objeto.obtener_campo('catalogos_descripcion').a_sugar()
        if cat_desc == '':
            cat_desc = u'Sin descripcion'
        obj_nuevo.importar_campo('name', cat_desc)
        logger.debug("Grabando un nuevo Catalogo...")
        obj_nuevo.grabar()


    # Veo que el tipo de venta este cargado, y si no lo esta, lo agrego.
    valor = objeto.obtener_campo('tipo_venta_codigo').a_sugar()
    res = instancia.modulos['mm002_Tipo_venta'].buscar(tipo_venta_codigo=valor)
    if len(res) > 1:
        raise sugar.ErrorSugar('Hay tipos de venta con ID duplicado')
    elif len(res) == 0:
        # Debo crear un objeto tipo_venta nuevo y agregarlo.
        obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Tipo_venta'])
        obj_nuevo.importar_campo('tipo_venta_codigo', valor)
        obj_nuevo.importar_campo('name',
                    objeto.obtener_campo('tipo_venta_descripcion').a_sugar())
        obj_nuevo.importar_campo('tipo_venta_descripcion',
                    objeto.obtener_campo('tipo_venta_descripcion').a_sugar())
        logger.debug("Grabando un nuevo tipo_venta...")
        obj_nuevo.grabar()


    # Por ultimo veo que la sucursal este cargada, y si no lo esta, la agrego.
    valor = objeto.obtener_campo('sucursales_codigo').a_sugar()
    res = instancia.modulos['mm002_Sucursales'].buscar(sucursales_codigo=valor)
    if len(res) > 1:
        raise sugar.ErrorSugar('Hay sucursales con ID duplicado')
    elif len(res) == 0 and valor.strip() != '':
        # Debo crear un objeto sucursal nuevo y agregarlo.
        obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Sucursales'])
        obj_nuevo.importar_campo('sucursales_codigo', valor)
        obj_nuevo.importar_campo('name',
                    objeto.obtener_campo('sucursales_descripcion').a_sugar())
        obj_nuevo.importar_campo('sucursales_descripcion',
                    objeto.obtener_campo('sucursales_descripcion').a_sugar())
        logger.debug("Grabando una nueva sucursal...")
        obj_nuevo.grabar()


    # Voy a darle un valor al campo 'name', utilizando el ID de la operacion
    operacion_id = objeto.obtener_campo('operacion_id').a_sugar()
    objeto.importar_campo('name', operacion_id)


    # Aqui ya estan creadas todas las entradas en Sugar de las cuales esta venta
    # depende. Ya puedo agrear la venta a la base de datos.

    logger.debug("Grabando una nueva VENTA...")
    logger.debug(objeto.grabar())

    # Relaciono la venta creada con el cliente
    logger.debug("Relacionando venta con el cliente...")
    instancia.relacionar(contacto, objeto)
    logger.debug("Pase relacionar")

    if PRUEBA_MANEJO and FECHA_VENTA_PRUEBA_MANEJO:
        logger.debug("Voy a crear llamada de prueba de manejo.")
        llamada_prueba_manejo(instancia, contacto, operacion_id, objeto)
    else :
        logger.debug("NO hay que crear llamada de prueba de manejo.")


    # No grabar la encuesta si la venta es anterior al 1/5/2010
    if objeto.obtener_campo('fecha_venta').valor <= \
            datetime.datetime(2010, 05, 01).timetuple():
        logger.debug("No creo la encuesta por ser la venta muy antigua")
        return True

    
    # Agrego una encuesta de satisfaccion solo si la sucursal no es GERENCIA
    # y si la fecha de entrega no es anterior a la de venta (facturacion).
    if not datos[15].startswith('GERENCIA') and \
            (objeto.obtener_campo('fecha_entrega').valor is None or \
            objeto.obtener_campo('fecha_venta').valor is None or \
            objeto.obtener_campo('fecha_entrega').valor >= objeto.obtener_campo('fecha_venta').valor):
        busq = instancia.modulos['mm002_Encuestas'].buscar(venta_id=operacion_id)
        if len(busq) != 0:
            # si hay algun resultado, uso el primero
            encuesta = busq[0]
            existia_encuesta = True
        else:
            # Creo un objeto nuevo del modulo mm002_Encuestas.
            encuesta = sugar.ObjetoSugar(instancia.modulos['mm002_Encuestas'])
            existia_encuesta = False

        encuesta.importar_campo('venta_id', operacion_id)
        encuesta.importar_campo('name', 'Encuesta de venta %s' % operacion_id)

        logger.debug("Antes de tocar encuesta")

        if datos[10] == '1' or datos[10] == '4' or datos[10] == '2':
            tipo_venta_enc = '1'
        elif datos[10] == '3':
            tipo_venta_enc = '2'
        else:
            logger.error("Tipo de venta no soportado")
            raise sugar.ErrorSugar("Tipo de venta codigo no soportado")
        
        if not existia_encuesta:
            encuesta.importar_campo('encuesta_estado', 'No iniciada')
        
        encuesta.importar_campo('tipo_encuesta', unicode(tipo_venta_enc, 'iso-8859-1'))
        encuesta.importar_campo('fecha_facturacion', 
                            objeto.obtener_campo('fecha_venta').a_sugar())
        
        encuesta.importar_campo('patenta_maipu', objeto.obtener_campo('patenta_maipu').a_sugar())
            
        encuesta.importar_campo('name', operacion_id)
        encuesta.importar_campo('assigned_user_name', usuario_asignado_n)
        encuesta.importar_campo('assigned_user_id', usuario_asignado_id)
        
        encuesta.importar_campo('marca', unicode(datos[4], 'iso-8859-1'))
        encuesta.importar_campo('modelo', unicode(datos[6], 'iso-8859-1'))
        
        encuesta.importar_campo('sucursal_codigo_c',
                                        unicode(datos[14], 'iso-8859-1'))
        encuesta.importar_campo('sucursal_descripcion',
                                        unicode(datos[15], 'iso-8859-1'))
        logger.debug("Sucursal de ENCUESTA: " + unicode(datos[15], 'iso-8859-1'))
        

        if datos[10] == '1' or datos[10] == '4':
            # Es venta tradicional o usados
            if (datos[20] == '00000000'):
                # SIN fecha de entrega
                if (datos[27].strip() != 'MAIPU'):
                    # SIN fecha de entrega y SIN entrega MAIPU
                    delta = 15
            else:
                # CON fecha de entrega
                if (datos[27].strip() != 'MAIPU'):
                    # SIN entrea MAIPU
                    if (datos[24] == '00000000'):
                        # SIN fecha de patentamiento
                        delta = 7
                    else:
                        # CON fecha de patentamiento
                        delta = 3
                else:
                    # CON entrega MAIPU
                    delta = 1
        else:
            # Sino, debe ser venta especial o planes
            delta = 15


        # defino la fecha de hoy:
        hoy = datetime.datetime.today()
        if datos[20] == '00000000':
            dia_t_enc_dt = hoy + datetime.timedelta(days=delta)
        else:
            dia_entrega = time.strptime(datos[20], '%Y%m%d')
            dia_entrega_dt = datetime.date(dia_entrega.tm_year,
                                dia_entrega.tm_mon, dia_entrega.tm_mday)
            dia_t_enc_dt = dia_entrega_dt

        if dia_t_enc_dt.weekday() == 5:
            sig_habil = 2
        elif dia_t_enc_dt.weekday() == 4:
            sig_habil = 3
        else:
            sig_habil = 1

        # Despues de sumarle uno o mas dias a la fecha de entrega para
        # encuestar el siguiente dia habil, cargo la fecha de encuesta
        encuesta.modificar_campo('fecha_tentativa_encuesta', (dia_t_enc_dt +
                            datetime.timedelta(days=sig_habil)).timetuple())

        if datos[20] != '00000000':
            encuesta.importar_campo('fecha_entrega', datos[20])

        # Agrego informacion de grupo y orden de planes
        if tipo_venta_enc == '2':
            encuesta.importar_campo('plan_grupo', \
                            objeto.obtener_campo('plan_grupo').a_sugar())
            encuesta.importar_campo('plan_orden', \
                            objeto.obtener_campo('plan_orden').a_sugar())

        # Agrego checkbox en encuesta si pasaron 5 dias entre fecha de
        # facturacion y de patentamiento
        try:
            fecha_fact = time.strptime(datos[9], '%Y%m%d')
            fecha_fact_dt = datetime.date(fecha_fact.tm_year, fecha_fact.tm_mon,
                fecha_fact.tm_mday)
            fecha_pat = time.strptime(datos[24], '%Y%m%d')
            fecha_pat_dt = datetime.date(fecha_pat.tm_year, fecha_pat.tm_mon,
                fecha_pat.tm_mday)
            if fecha_pat_dt > fecha_fact_dt + datetime.timedelta(5):
                # Pasaron mas de 5 dias
                logger.debug("Pasaron + de 5 dias entre facturacion y entrega")
                encuesta.modificar_campo('alerta_fact_patent_flag_c', True)
            else:
                logger.debug("Pasaron - de 5 dias entre facturacion y entrega")
                encuesta.modificar_campo('alerta_fact_patent_flag_c', False)
        except ValueError:
            logger.debug("Capture ValueError en fecha de entrega o factura")
            encuesta.modificar_campo('alerta_fact_patent_flag_c', False)


        logger.debug("Grabando una nueva ENCUESTA...")
        logger.debug(encuesta.grabar())
        
        if not existia_encuesta:
            # Relaciono la encuesta creada con el cliente
            instancia.relacionar(contacto, encuesta)
        
    else:
        logger.debug("No hay encuesta por ser venta de GERENCIA.")
    
    return True


def obtener_instancia():
    # Me conecto a la instancia de SugarCRM.
    logger.debug("Conectando a instancia")
    instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Ventas', 'mm002_Marcas',
                                        'mm002_Modelo', 'mm002_Catalogos',
                                        'mm002_Tipo_venta', 'mm002_Sucursales',
                                        'Contacts', 'mm002_Encuestas','Calls'],
                    crm_config.LDAP_KEY, crm_config.LDAP_IV)

    return instancia


if __name__ == '__main__':
    import sys

    instancia = obtener_instancia()
    procesar(instancia, sys.argv[1])


