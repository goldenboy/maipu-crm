import sugar
import crm_config
import sys
import random
import commands

cantidad = 19

campos_opc = ['serv_gral_grado_satisfaccion', 'serv_turno_horario_turno_bueno',
            'serv_turno_facil_contactarse', 'serv_turno_horario_respetado',
            'serv_asesor_grado_satisfaccion', 'serv_asesor_educado_amable',
            'serv_asesor_entiende_necesidad', 'serv_asesor_con_conocimiento',
            'serv_asesor_mantuvo_informado', 'serv_entrega_cumple_plazo',
            'serv_entrega_factura_clara', 'serv_entrega_monto_acorde',
            'serv_taller_buena_reparacion', 'serv_taller_ultima_visita',
            'serv_gral_nos_recomendaria', 'serv_grntia_vendrasin_garantia',
            'serv_grntia_auto_en_garantia', 'marca']

campos_txt = ['serv_gral_observaciones', 'serv_grntia_por_que_no_vendra',
            'por_que_decidio_visitarnos']

# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Encuesta', 'Contacts'])


# Tomo una muestra de clientes para asignarles las ventas
contactos = instancia.modulos['Contacts'].buscar()



# Genero las encuestas propiamente dichas
for i in range(cantidad):
    # Creo un objeto nuevo del modulo Encuesta.
    objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Encuesta'])
    objeto.modificar_campo('tipo_encuesta', '0')
    objeto.importar_campo('encuesta_estado', u'Completed')
    objeto.importar_campo('name', u'Encuesta de servicios automatica')

    for campo in campos_opc:
        # Elijo una de las opciones posibles (que no sea '')
        eleccion = random.choice((objeto.campos[campo].opciones.keys())[1:])
        objeto.modificar_campo(campo, eleccion)

    for campo in campos_txt:
        texto = commands.getoutput('fortune /usr/share/games/fortunes/bofh-excuses')
        objeto.importar_campo(campo, unicode(texto))
    
    
    objeto.grabar()
    
    # relaciono la encuesta con un contacto
    objeto.relacionar(random.choice(contactos), 'contact_id_c')
    print "1 objeto grabado satisfactoriamente"
    
