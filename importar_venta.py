import sugar
import crm_config
import sys


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Ventas', 'mm002_Marcas',
                                        'mm002_Modelos', 'mm002_Tipo_venta',
                                        'mm002_Empleados', 'mm002_Sucursales',
                                        'Contacts', 'mm002_Encuesta'])

# Creo un objeto nuevo del modulo Ventas.
objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Ventas'])

# Leo el archivo de plantilla con los campos, y los guardo en la lista 'campos'.
arch_plantilla = open('plantilla_venta.txt')
campos = arch_plantilla.readlines()

# Lo mismo con el archivo de datos.
arch_datos = open('datos_venta.txt')
datos = arch_datos.readlines()

# Cargo todos los valores importados en el objeto que entrara en sugar.
for campo in zip(campos, datos):
    print campo[0] + ' -> ' + campo[1]
    objeto.importar_campo(campo[0].rstrip(), unicode(campo[1].rstrip()))

print "Objeto listo."

# Verifico que todos los objetos externos referenciados (marca, modelo, etc...)
# existan en Sugar y sean unicos. En caso de que no existan, los creo. Y si no
# son unicos, salgo emitiendo un error.

# Primero, verifico que exista el cliente.
valor = objeto.obtener_campo('id_maipu_cliente').a_sugar()
res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
if len(res) != 1:
    raise sugar.ErrorSugar('No existe un solo cliente con ese ID')
# Guardo el ID de sugar para mas tarde
contacto = res[0]
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
    obj_nuevo.importar_campo('marcas_descripcion',
                        objeto.obtener_campo('marcas_descripcion').a_sugar())
    print "Grabando una nueva Marca..."
    obj_nuevo.grabar()


# Luego hago lo mismo con el modelo
valor = objeto.obtener_campo('modelos_codigo').a_sugar()
res = instancia.modulos['mm002_Modelos'].buscar(modelos_codigo=valor)
if len(res) > 1:
    raise sugar.ErrorSugar('Hay modelos con ID duplicado')
elif len(res) == 0:
    # Debo crear un objeto modelo nuevo y agregarlo.
    obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Modelos'])
    obj_nuevo.importar_campo('modelos_codigo', valor)
    obj_nuevo.importar_campo('modelos_descripcion',
                        objeto.obtener_campo('modelos_descripcion').a_sugar())
    obj_nuevo.importar_campo('marcas_codigo',
                        objeto.obtener_campo('marcas_codigo').a_sugar())
    print "Grabando un nuevo Modelo..."
    obj_nuevo.grabar()


# Luego veo que el tipo de venta este cargado, y si no lo esta, lo agrego.
valor = objeto.obtener_campo('tipo_venta_codigo').a_sugar()
res = instancia.modulos['mm002_Tipo_venta'].buscar(tipo_venta_codigo=valor)
if len(res) > 1:
    raise sugar.ErrorSugar('Hay tipos de venta con ID duplicado')
elif len(res) == 0:
    # Debo crear un objeto tipo_venta nuevo y agregarlo.
    obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Tipo_venta'])
    obj_nuevo.importar_campo('tipo_venta_codigo', unicode(valor))
    obj_nuevo.importar_campo('tipo_venta_descripcion',
                    objeto.obtener_campo('tipo_venta_descripcion').a_sugar())
    print "Grabando un nuevo Tipo de Venta..."
    obj_nuevo.grabar()


# Luego veo que el vendedor este cargado, y si no lo esta, lo agrego.
valor = objeto.obtener_campo('vendedor_codigo').a_sugar()
res = instancia.modulos['mm002_Empleados'].buscar(empleados_legajo=valor)
if len(res) > 1:
    raise sugar.ErrorSugar('Hay empleados con ID duplicado')
elif len(res) == 0:
    # Debo crear un objeto empleado nuevo y agregarlo como vendedor.
    obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Empleados'])
    obj_nuevo.importar_campo('empleados_legajo', valor)
    obj_nuevo.importar_campo('empleados_apellido_nombre',
                    objeto.obtener_campo('vendedor_nombre').a_sugar())
    obj_nuevo.importar_campo('empleados_cargo', unicode('V'))
    print "Grabando un nuevo vendedor..."
    obj_nuevo.grabar()


# Luego veo que el gestor este cargado, y si no lo esta, lo agrego.
valor = objeto.obtener_campo('gestor_codigo').a_sugar()
res = instancia.modulos['mm002_Empleados'].buscar(empleados_legajo=valor)
if len(res) > 1:
    raise sugar.ErrorSugar('Hay empleados con ID duplicado')
elif len(res) == 0:
    # Debo crear un objeto empleado nuevo y agregarlo como gestor.
    obj_nuevo = sugar.ObjetoSugar(instancia.modulos['mm002_Empleados'])
    obj_nuevo.importar_campo('empleados_legajo', valor)
    obj_nuevo.importar_campo('empleados_apellido_nombre',
                    objeto.obtener_campo('gestor_nombre').a_sugar())
    obj_nuevo.importar_campo('empleados_cargo', unicode('G'))
    print "Grabando un nuevo gestor..."
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
    obj_nuevo.importar_campo('sucursales_descripcion',
                    objeto.obtener_campo('sucursales_descripcion').a_sugar())
    print "Grabando una nueva sucursal..."
    obj_nuevo.grabar()


# Voy a darle un valor al campo 'name', utilizando el ID de la operacion
operacion_id = objeto.obtener_campo('operacion_id').a_sugar()
objeto.importar_campo('name', operacion_id)



# Aqui ya estan creadas todas las entradas en Sugar de las cuales esta venta
# depende. Ya puedo agrear la venta a la base de datos.

print "Grabando una nueva VENTA..."
print objeto.grabar()


# Agrego una encuesta de satisfaccion

encuesta = sugar.ObjetoSugar(instancia.modulos['mm002_Encuesta'])
#objeto.importar_campo('contact_id_c', contact_id)
encuesta.importar_campo('venta_id', operacion_id)
encuesta.importar_campo('name', operacion_id)
encuesta.grabar()

# si se grabo correctamente la encuesta, la deberia poder recuperar.
# Ya no hace falta esto. La libreria recupera el ID automaticamente.
#res = instancia.modulos['mm002_enc_sat_venta'].buscar(operacion_id=operacion_id)
#encuesta = res[0]

# Relaciono la encuesta creada con el cliente
encuesta.relacionar(contacto, 'contact_id_c')



