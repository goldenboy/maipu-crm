#!/usr/bin/python
#
# Leer un registro de SugarCRM desde la entrada estandar, un atributo por linea,
# y guardarlo en SugarCRM.
#

import sugar
import crm_config
import sys


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                                    crm_config.CLAVE, ['Contacts'])

# Creo un objeto nuevo del modulo Contacts.
objeto = sugar.ObjetoSugar(instancia.modulos['Contacts'])

# Leo la entrada estandar y guardo sus lineas en la lista.
lineas = sys.stdin.readlines()

for linea in lineas:
    (nombre_campo, s, valor_campo) = linea.partition(':')
    objeto.modificar_campo(nombre_campo, valor_campo.rstrip())

objeto.grabar()

