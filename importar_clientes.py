import sugar
import crm_config
import sys


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['Contacts'], crm_config.LDAP_KEY,
                    crm_config.LDAP_IV)

# La lista 'campos' tiene los nombres de las columnas ordenadas correctamente.
columnas = ['id_maipu_c', 'last_name', 'birthdate', 'primary_address_street', 
            'domicilio_uno_numero_c', 'domicilio_uno_piso_c',
            'domicilio_uno_barrio_c', 'primary_address_city',
            'primary_address_state', 'primary_address_postalcode',
            'alt_address_street', 'domicilio_dos_numero_c',
            'domicilio_dos_piso_c', 'domicilio_dos_barrio_c',
            'alt_address_city', 'alt_address_state', 'alt_address_postalcode',
            'phone_home', 'phone_work', 'phone_mobile', 'phone_fax', 'email1',
            'dni_tipo_c', 'dni_numero_c', 'cuit_numero_c', 'nacionalidad_c',
            'condicion_iva_c', 'salutation', 'empresa_c', 'actividad_c',
            'estado_civil_c', 'sexo_c']

# Leo el archivo de datos.
arch_datos = open('CRM-Clientes.txt')
datos = arch_datos.readlines()


for linea in datos:
    campos = [cadena.strip() for cadena in linea.split(',')]
    
    # Creo un objeto nuevo del modulo Modelos.
    objeto = sugar.ObjetoSugar(instancia.modulos['Contacts'])
    for i in range(len(columnas)):
        print columnas[i] + ': ' + campos[i]
        try:
            objeto.importar_campo(columnas[i], unicode(campos[i], 'iso-8859-1'))
        except sugar.ErrorSugar:
            try:
                objeto.importar_campo(columnas[i], campos[i])
            except sugar.ErrorSugar:
                print "No pude importar el campo '" + columnas[i] + \
                    "' con el valor '" + campos[i] + "'"
    objeto.grabar()
    print "1 objeto grabado."
    

print "Fin."


