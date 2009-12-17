import sugar
import crm_config
import sys
import random
import commands

cantidad = 10

RESPUESTA_SI_NO = ['Si', 'No']
GRADO_SATISFACCION = ['1', '2', '3', '4', '5']

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
                    crm_config.CLAVE, ['mm002_Encuesta'])

for i in range(cantidad):
    # Creo un objeto nuevo del modulo Encuesta.
    objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Encuesta'])
    objeto.modificar_campo('tipo_encuesta', '1')
    objeto.importar_campo('encuesta_estado', u'Completed')
    objeto.importar_campo('name', u'Encuesta automatica')

    for campo in campos_opc:
        print campo
        print objeto.campos[campo].opciones.keys()[1:]
        # Elijo una de las opciones posibles (que no sea '')
        eleccion = random.choice((objeto.campos[campo].opciones.keys())[1:])
        objeto.modificar_campo(campo, eleccion)

    for campo in campos_txt:
        texto = commands.getoutput('fortune /usr/share/games/fortunes/bofh-excuses')
        objeto.importar_campo(campo, unicode(texto))
    
    objeto.grabar()

