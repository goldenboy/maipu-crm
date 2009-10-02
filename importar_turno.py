import sugar
import crm_config
import sys


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Marcas', 'mm002_Modelos', 
                                        'mm002_Empleados', 'Contacts',
                                        'mm002_Turnos'])

# Creo un objeto nuevo del modulo Turnos.
objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Turnos'])

# Leo el archivo de plantilla con los campos, y los guardo en la lista 'campos'.
arch_plantilla = open('plantilla_turno.txt')
campos = arch_plantilla.readlines()

# Lo mismo con el archivo de datos.
arch_datos = open('datos_turno.txt')
datos = arch_datos.readlines()

# Cargo todos los valores importados en el objeto que entrara en sugar.
for campo in zip(campos, datos):
    objeto.importar_campo(campo[0].rstrip(), campo[1].rstrip())

# Verifico que todos los objetos externos referenciados (marca, modelo, etc...)
# existan en Sugar y sean unicos. En caso de que no existan o no
# sean unicos, salgo emitiendo un error.

# Primero, verifico que exista el cliente.
valor = objeto.obtener_campo('id_maipu_cliente').a_sugar()
res = instancia.modulos['Contacts'].buscar(id_maipu_c=valor)
if len(res) != 1:
    raise sugar.ErrorSugar('No existe un solo cliente con ese ID')


# Luego veo que la marca este cargada, y si no lo esta, la agrego.
valor = objeto.obtener_campo('marcas_codigo').a_sugar()
res = instancia.modulos['mm002_Marcas'].buscar(marcas_codigo=valor)
if len(res) != 1:
    raise sugar.ErrorSugar('No existe la marca o hay dos con el mismo codigo.')


# Luego hago lo mismo con el modelo
valor = objeto.obtener_campo('modelos_codigo').a_sugar()
res = instancia.modulos['mm002_Modelos'].buscar(modelos_codigo=valor)
if len(res) != 1:
    raise sugar.ErrorSugar('No existe el modelo o hay dos con el mismo codigo.')


# Voy a darle un valor al campo 'name', utilizando el nombre del Cliente
nombre_cliente = objeto.obtener_campo('nombre_contacto').a_sugar()
objeto.importar_campo('name', nombre_cliente)


# Aqui ya estan creadas todas las entradas en Sugar de las cuales este turno
# depende. Ya puedo agrear el turno a la base de datos.

print "Grabando un nuevo TURNO..."
print objeto.grabar()


