import sugar
import crm_config
import sys


def arbol(padre, nivel):
    for i in range(nivel):
        print "\t",
    print '"%s"' % padre
    while len(relacion[padre]) > 0:
        hijo = relacion[padre].pop(0)
        arbol(hijo, nivel + 1)


# Me conecto a la instancia de SugarCRM.
instancia = sugar.InstanciaSugar(crm_config.WSDL_URL, crm_config.USUARIO,
                    crm_config.CLAVE, ['CETeams'])

res = instancia.modulos['CETeams'].buscar()

relacion = {}
raices = []
for team in res:
    relacion[team.obtener_campo('name').a_sugar()] = []

for team in res:
    if team.obtener_campo('parent_team_name').a_sugar() != '':
        relacion[team.obtener_campo('parent_team_name').a_sugar()].append(team.obtener_campo('name').a_sugar())
    else:
        raices.append(team.obtener_campo('name').a_sugar())

for equipo in raices:
    arbol(equipo, 0)

