import sugar
import crm_config
import sys


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Turnos', 'mm002_Empleados',
                                        'Contacts', 'mm002_enc_servicios',
                                        'mm002_Ordenes'], crm_config.LDAP_KEY,
                    crm_config.LDAP_IV)

# Creo un objeto nuevo del modulo Ordenes.
objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Ordenes'])

# Leo el archivo de plantilla con los campos, y los guardo en la lista 'campos'.
arch_plantilla = open('plantilla_orden.txt')
campos = arch_plantilla.readlines()

# Lo mismo con el archivo de datos.
arch_datos = open('datos_orden.txt')
datos = arch_datos.readlines()

# Cargo todos los valores importados en el objeto que entrara en sugar.
for campo in zip(campos, datos):
    objeto.importar_campo(campo[0].rstrip(), campo[1].rstrip())

# Verifico que todos los objetos externos referenciados (turno, asesor, cliente)
# existan en Sugar y sean unicos. En caso de que no exista el asesor, lo
# agrego. Y si no son unicos, salgo emitiendo un error.

# Primero, verifico que exista el cliente.
valor = objeto.obtener_campo('id_maipu_cliente').a_sugar()
res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
if len(res) != 1:
    raise sugar.ErrorSugar('No existe un solo cliente con ese ID')
# Guardo el ID de sugar para mas tarde
contacto = res[0]
contact_id = contacto.obtener_campo('id').a_sugar()


# Luego veo que el turno este cargado.
valor = objeto.obtener_campo('turno_id').a_sugar()
res = instancia.modulos['mm002_Turnos'].buscar(turno_id=valor)
if len(res) != 1:
    raise sugar.ErrorSugar('Turno duplicado o inexistente.')


# Luego hago lo mismo con el asesor, y si no esta, lo agrego.
valor = objeto.obtener_campo('asesor_codigo').a_sugar()
res = instancia.modulos['mm002_Empleados'].buscar(empleados_legajo=valor)
if len(res) > 1:
    raise sugar.ErrorSugar('Hay empleados con legajo duplicado')
elif len(res) == 1:
    empleado = res[0]
elif len(res) == 0:
    # Debo crear un objeto empleado nuevo y agregarlo.
    obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Empleados'])
    obj_nuevo.importar_campo('empleados_legajo', valor)
    obj_nuevo.importar_campo('empleados_apellido_nombre',
                        objeto.obtener_campo('asesor_nombre').a_sugar())
    print "Grabando un nuevo Empleado..."
    obj_nuevo.grabar()
    empleado = obj_nuevo


# Voy a darle un valor al campo 'name', utilizando el Id de la orden
orden_id = objeto.obtener_campo('orden_id').a_sugar()
objeto.importar_campo('name', orden_id)



print "Grabando una nueva ORDEN FACTURADA..."
print objeto.grabar()


# Agrego una encuesta de servicios

encuesta = sugar.ObjetoSugar(instancia.modulos['mm002_enc_servicios'])
#objeto.importar_campo('contact_id_c', contact_id)
# Calculo el id de la operacion
operacion_id = objeto.obtener_campo('operacion_id').a_sugar()
encuesta.importar_campo('operacion_id', operacion_id)

# Modifico el campo 'fecha_tentativa' de la encuesta con el dato obtenido de
# la importacion.
fecha = dict(zip(campos, datos))['fecha_tentativa']
# Supongo que viene en formato 'YYYYMMDD'
fecha = fecha[0:4] + '-' + fecha[4:6] + '-' + fecha[6:8]
# Fecha quedaria como 'YYYY-MM-DD'
encuesta.importar_campo('fecha_tentativa', fecha)


encuesta.grabar()

# si se grabo correctamente la encuesta, la deberia poder recuperar.
# Ya no hace falta esto. La libreria recupera el ID automaticamente.
#res = instancia.modulos['mm002_enc_sat_venta'].buscar(operacion_id=operacion_id)
#encuesta = res[0]

# Relaciono la encuesta creada con la orden de servicio
encuesta.relacionar(objeto, 'mm002_enc_servicios_mm002_ordenes_name')


# Relaciono finalmente la encuesta con el asesor, de forma que aparezca su
# nombre en el cuestionario
encuesta.relacionar(empleado, 'mm002_empleados_mm002_enc_servicios')

