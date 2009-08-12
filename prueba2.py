#!/usr/bin/python

import sugar
import crm_config


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                                    crm_config.CLAVE, ['Contacts'])

# Obtengo los contactos que tengan como primer nombre "Hai". Supongo que existen
# registros.
res = instancia.modulos['Contacts'].buscar('first_name', 'Edna')

# Tomo el primero de los resultados.
objeto = res[0]

# Cambio el pais por "Argentina"
objeto.modificar_campo('primary_address_country', 'Argentina')

# Actualizo el registro en SugarCRM.
objeto.grabar()

