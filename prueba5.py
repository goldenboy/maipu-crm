import sugar
import crm_config
import sys


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                                    crm_config.CLAVE, ['Contacts'])

# Creo un objeto nuevo del modulo Contacts.
objeto = sugar.ObjetoSugar(instancia.modulos['Contacts'])

# Leo el archivo de plantilla con los campos, y los guardo en la lista 'campos'.
arch_plantilla = open('plantilla.txt')
arch_datos = open('datos.txt')
campos = arch_plantilla.readlines()
datos = arch_datos.readlines()

for campo in zip(campos, datos):
    objeto.importar_campo(campo[0].rstrip(), campo[1].rstrip())

print objeto.grabar()



