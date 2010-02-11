#!/usr/bin/python
#
# Cambio masivamente el nombre de las encuestas de acuerdo al contenido de los
# valores de los campos de cada una.
#

import sugar
import crm_config


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Encuesta', 'Contacts'],
                    crm_config.LDAP_KEY, crm_config.LDAP_IV)

# Obtengo todas las encuestas que se puedan traer. Supongo
#  que existen registros.
lista = instancia.modulos['mm002_Encuesta'].buscar()

for encuesta in lista:
    # Defino el string nombre_enc que sera el nombre de la encuesta
    nombre_enc = "Encuesta a "
    # Le doy valores al nombre y apellido por si no estan en la base
    nombre = "NN"
    apellido = ""
    
    # Traigo el objeto que representa el contacto relacionado a la encuesta
    contacto_id = encuesta.obtener_campo('contact_id_c').a_sugar()
    contacto = instancia.modulos['Contacts'].buscar(id=contacto_id)
    # Todo ok si la busqueda arrojo exactamente un solo resultado (es un ID)
    if len(contacto) == 1:
        # Traigo el nombre y el apellido del contacto en cuestion
        nombre = contacto[0].obtener_campo('first_name').a_sugar()
        apellido = contacto[0].obtener_campo('last_name').a_sugar()
    
    # Completo el nombre de la encuesta con la marca
    nombre_enc += nombre + " " + apellido + " para "
    nombre_enc += encuesta.obtener_campo('marca').a_sugar()
    
    # Actualizo con el nombre de la encuesta nuevo y grabo
    encuesta.importar_campo('name', unicode(nombre_enc))
    encuesta.grabar()



