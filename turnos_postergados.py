import sugar
import crm_config
import monitor_config
import logging
import datetime

######################
# Con este script creo llamadas de reprogramacion para aquellos turnos del dia
# que no se hayan cumplido, por ausencia del vehiculo
######################

# A quien le asigno la llamada
usuario_asignado_n = 'ndeamicis'
usuario_asignado_id = 'b017df97-18be-064a-a4ab-4bd1a04ff610'

# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("turnos_postergados")

marcas = ['10', '20', '30']
offset_gmt = -3


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
    
    for turno in busq_todos:
        logger.debug("De hoy: turno_id: %s, hora_turno: %s, marca_codigo: %s" % (turno.obtener_campo('turno_id').a_sugar(), turno.obtener_campo('hora_turno').a_sugar(), turno.obtener_campo('marcas_codigo').a_sugar()))
        
    # Filtro los turnos, dejando aca solo los que tengan hora anterior a la 
    # pasada como argumento
    busq_ant = [turno for turno in busq_todos
                    if turno.obtener_campo('hora_turno').valor <= hora_limite and turno.obtener_campo('marcas_codigo').a_sugar() in marcas]


    # Para todos los turnos de busq_ant, tengo que crear una llamada asociada
    # al cliente, que pida que se le llame para agendar un nuevo turno
    
    for turno in busq_ant:
        logger.debug("Anular: turno_id: %s, hora_turno: %s, marca_codigo: %s" % (turno.obtener_campo('turno_id').a_sugar(), turno.obtener_campo('hora_turno').a_sugar(), turno.obtener_campo('marcas_codigo').a_sugar()))
        turno.importar_campo('estado_turno', '9999')
        turno.importar_campo('resultado_recuperacion', 'Sin contacto')
        turno_id = turno.obtener_campo('id').a_sugar()
        turno.grabar()


        # Creo la llamada nueva
        llamada = sugar.ObjetoSugar(instancia.modulos['Calls'])

        llamada.importar_campo('status', 'Planned')
        llamada.importar_campo('assigned_user_name', usuario_asignado_n)
        llamada.importar_campo('assigned_user_id', usuario_asignado_id)
        llamada.importar_campo('direction', 'Outbound')
        llamada.importar_campo('parent_type', u'mm002_Turnos')
        llamada.importar_campo('parent_id', turno_id)
        llamada.importar_campo('duration_hours', '0')
        llamada.importar_campo('duration_minutes', '5')
        llamada.importar_campo('name', u'Reprogramar turno')
        fecha_anio = turno.obtener_campo('fecha_turno').valor.tm_year
        fecha_mes = turno.obtener_campo('fecha_turno').valor.tm_mon
        fecha_dia = turno.obtener_campo('fecha_turno').valor.tm_mday
        llamada.modificar_campo('date_start', datetime.datetime(fecha_anio, fecha_mes, fecha_dia, hora_limite/100 - offset_gmt, 59).timetuple())
        llamada.importar_campo('description', u"""Llamar al contacto %s para 
        reprogramar el turno de taller por motivo '%s'.
        """ % (turno.obtener_campo('nombre_contacto').a_sugar(), 
                turno.obtener_campo('motivo_turno').a_sugar()))
        
        llamada.grabar()



