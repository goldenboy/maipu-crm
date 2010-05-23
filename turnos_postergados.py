import sugar
import crm_config
import monitor_config
import logging

######################
# Con este script creo llamadas de reprogramacion para aquellos turnos del dia
# que no se hayan cumplido, por ausencia del vehiculo
######################

# A quien le asigno la llamada
usuario_asignado_n = 'eamuchastegui'
usuario_asignado_id = '4df5932a-1f1f-c9e9-402d-4bd1a040dbed'

# Configuro el logging
logging.basicConfig(level=monitor_config.LOG_LEVELS[monitor_config.LOG_LEVEL])
logger = logging.getLogger("turnos_postergados")




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
        logger.debug("Anulo turno en el CRM. Le pongo estado_turno=9999")
        turno.importar_campo('estado_turno', '9999')
        turno.grabar()

        # Primero, verifico que exista el cliente. Si no existe, salto el turno
        logger.debug("Buscando cliente.")
        valor = turno.obtener_campo('cliente_id').a_sugar()
        res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)

        if len(res) == 0:
            # No hay un cliente con ese id. Salto este turno
            logger.debug("No hay cliente cargado.")
            continue
        else:
            logger.debug("Existen %i copias del cliente." % len(res))
            # Hay uno o mas. Elijo el primero
            contacto = res[0]
    
        contact_id = contacto.obtener_campo('id').a_sugar()


        # Creo la llamada nueva
        llamada = sugar.ObjetoSugar(instancia.modulos['Calls'])

        llamada.importar_campo('status', 'Planned')
        llamada.importar_campo('assigned_user_name', usuario_asignado_n)
        llamada.importar_campo('assigned_user_id', usuario_asignado_id)
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



