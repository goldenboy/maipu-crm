import sugar
import crm_config
import monitor_config
import logging
import datetime


# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("importar_venta")

def procesar(instancia, pathname):

    # Leo el archivo de datos.
    arch_datos = open(pathname)
    datos = arch_datos.readlines()
    
    return procesar_linea(instancia, datos[0])


def procesar_linea(instancia, linea):
    
    # Leo el archivo de datos.
    datos = linea.split(';')

    # Creo un objeto nuevo del modulo Ventas.
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
            'patenta_maipu']

    # Cargo todos los valores importados en el objeto que entrara en sugar.
    for campo in zip(campos, datos):
        logger.debug(campo[0] + ' -> ' + campo[1])
        if campo[0] == 'patenta_maipu' and campo[1] == 'M':
            objeto.importar_campo(campo[0].rstrip(), '1')
        elif campo[0] == 'patenta_maipu' and campo[1] != 'M':
            objeto.importar_campo(campo[0].rstrip(), '0')
        else:
            objeto.importar_campo(campo[0].rstrip(), unicode(campo[1].rstrip(),
                                                            'iso-8859-1'))

    logger.debug("Objeto listo.")

    # Verifico que todos los objetos externos referenciados (marca, modelo, etc...)
    # existan en Sugar y sean unicos. En caso de que no existan, los creo. Y si no
    # son unicos, salgo emitiendo un error.

    # Primero, verifico que exista el cliente, y si no lo esta, lo agrego
    valor = objeto.obtener_campo('id_maipu_cliente').a_sugar()
    res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
    if len(res) > 1:
        raise sugar.ErrorSugar('Existen clientes duplicados con ese ID')
    elif len(res) == 0:
        # Debo crear un objeto cliente nuevo y agregarlo.
        obj_nuevo = sugar.ObjetoSugar(instancia.modulos['Contacts'])
        obj_nuevo.importar_campo('id_maipu_c', valor)
        obj_nuevo.importar_campo('last_name',
                        objeto.obtener_campo('nombre_cliente').a_sugar())
        logger.debug("Grabando un nuevo cliente...")
        obj_nuevo.grabar()
        contacto = obj_nuevo
    else:
        contacto = res[0]

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
        obj_nuevo.importar_campo('name',
                        objeto.obtener_campo('catalogos_descripcion').a_sugar())
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
    elif len(res) == 0:
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
    
    # Agrego una encuesta de satisfaccion
    encuesta = sugar.ObjetoSugar(instancia.modulos['mm002_Encuestas'])
    encuesta.importar_campo('venta_id', operacion_id)
    encuesta.importar_campo('name', 'Encuesta de venta %s' % operacion_id)

    # defino la fecha de hoy:
    hoy = datetime.datetime.today()
        
    if datos[10] == '1' or datos[10] == '4':
        # Es venta tradicional o usados
        delta = 7
    else:
        # Sino, debe ser venta especial o planes
        delta = 15

    logger.debug("Antes de tocar encuesta")
    
    encuesta.importar_campo('tipo_encuesta', unicode(datos[10], 'iso-8859-1'))
    encuesta.modificar_campo('fecha_tentativa_encuesta', (hoy + 
                                    datetime.timedelta(days=delta)).timetuple())
    
    encuesta.importar_campo('encuesta_estado', 'No iniciada')
    encuesta.importar_campo('fecha_facturacion', 
                        objeto.obtener_campo('fecha_venta').a_sugar())

    if objeto.obtener_campo('patenta_maipu').a_sugar() == 'M':
        patenta_maipu = '1'
    else:
        patenta_maipu = '0'
    encuesta.importar_campo('patenta_maipu', patenta_maipu)

    encuesta.importar_campo('name', operacion_id)
    logger.debug("Grabando una nueva ENCUESTA...")
    encuesta.grabar()

    # Relaciono la encuesta creada con el cliente
    instancia.relacionar(contacto, encuesta)
    
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


