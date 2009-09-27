import sugar
import crm_config
import sys


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['mm002_Empleados'])

# La lista 'campos' tiene los nombres de las columnas ordenadas correctamente.
columnas = ['empleados_legajo', 'empleados_apellido_nombre', 'empleados_cargo']

# Leo el archivo de datos.
arch_datos = open('CRM-Empleados.txt')
datos = arch_datos.readlines()


for linea in datos:
    campos = [cadena.rstrip().lstrip() for cadena in linea.split(';')]
    
    # Creo un objeto nuevo del modulo Modelos.
    objeto = sugar.ObjetoSugar(instancia.modulos['mm002_Empleados'])
    for i in range(len(columnas)):
        objeto.importar_campo(columnas[i], unicode(campos[i], 'iso-8859-1'))
        if i == 1:
            objeto.importar_campo('name', unicode(campos[i], 'iso-8859-1'))
#        print unicode(campos[i], 'iso-8859-1')
    objeto.grabar()
    print "1 objeto grabado."
    

print "Fin."


