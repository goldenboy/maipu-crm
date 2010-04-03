import sugar
import crm_config
import sys


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['Users'], crm_config.LDAP_KEY,
                    crm_config.LDAP_IV)

# La lista 'campos' tiene los nombres de las columnas ordenadas correctamente.
columnas = ['description', 'last_name', 'user_name', 'title']

# Leo el archivo de datos.
arch_datos = open('../datos/ListadelCall.csv')
datos = arch_datos.readlines()


for linea in datos:
    campos = [cadena.strip() for cadena in linea.split(';')]

    # Para cada usuario a importar, hago una busqueda de Usuarios por user_name,
    # por si los usuarios fueron ingresados previamente
    busq = instancia.modulos['Users'].buscar(user_name=datos[2])
    if len(busq) != 0:
        # si hay algun resultado, uso el primero
        objeto = busq[0]
    else:
        # Creo un objeto nuevo del modulo Users.
        objeto = sugar.ObjetoSugar(instancia.modulos['Users'])

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


