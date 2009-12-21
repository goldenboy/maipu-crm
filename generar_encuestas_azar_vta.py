import sugar
import crm_config
import sys
import random
import commands

cantidad = 1

campos_opc = ['vent_gest_grado_satisfaccion', 'vent_entr_garantias',
        'vent_gest_cumplieron_plazos', 'vent_sop_recomendaria',
        'vent_vend_servicios_adicionale', 'vent_vend_grado_satisfaccion',
        'vent_gest_turno_pactado', 'vent_gest_amable',
        'vent_vend_atendido_rapidamente', 
        'vent_entr_informacion_contacto', 'marca', 'vent_entr_funcionamiento',
        'vent_gral_grado_satisfaccion', 
        'vent_vend_conoce_productos', 'vent_vend_informacion_veraz',
        'vent_entr_unidad_buen_estado', 'vent_vend_informacion_veraz_no',
        'vent_entr_unidad_buen_estad_no', 'vent_entr_grado_satisfaccion',
        'vent_vend_amable_profesional', 'vent_sop_grado_satisfaccion',
        'vent_vend_comprendio_necesidad']

campos_txt = ['por_que_decidio_visitarnos', 'vent_sop_para_muy_satisfecho',]

# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Encuesta', 'Contacts'])


# Tomo una muestra de clientes para asignarles las ventas
contactos = instancia.modulos['Contacts'].buscar()



# Genero las encuestas propiamente dichas
for i in range(cantidad):
    # Creo un objeto nuevo del modulo Encuesta.
    objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Encuesta'])
    objeto.modificar_campo('tipo_encuesta', '1')
    objeto.importar_campo('encuesta_estado', u'Completed')
    contacto_id = random.choice(contactos).obtener_campo('id').a_sugar()
    objeto.importar_campo('contact_id_c', contacto_id)
    objeto.importar_campo('name', u'Encuesta automatica')

    for campo in campos_opc:
        # Elijo una de las opciones posibles (que no sea '')
        eleccion = random.choice((objeto.campos[campo].opciones.keys())[1:])
        objeto.modificar_campo(campo, eleccion)

    for campo in campos_txt:
        texto = commands.getoutput('fortune /usr/share/games/fortunes/bofh-excuses')
        objeto.importar_campo(campo, unicode(texto))
    
    
    # relaciono la encuesta con un contacto
    #objeto.relacionar(random.choice(contactos), 'contact_id_c')
    
    objeto.grabar()
    print "1 objeto grabado satisfactoriamente"
    
