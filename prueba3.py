#!/usr/bin/python
#
# Obtener un registro de SugarCRM y escribirlo en la salida estandar,
# un atributo por linea.
#

import sugar
import crm_config


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                                    crm_config.CLAVE, ['Contacts'])

# Obtengo los contactos que tengan como parte del primer nombre "Edna". Supongo
#  que existen registros.
res = instancia.modulos['Contacts'].buscar(first_name='Edna')

# Tomo el primero de los resultados.
objeto = res[0]

# Itero sobre los campos del objeto y los escribo en el archivo.
for campo in objeto.campos.keys():
#    print campo + ':' + objeto.obtener_campo(campo)
    print campo + ':' + objeto.obtener_campo(campo).a_sugar()


