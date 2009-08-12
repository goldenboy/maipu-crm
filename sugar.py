
import SOAPpy
import hashlib
import crm_config
import types

class ErrorSugar(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class TipoSugar:
    """Tipo de datos abstracto que representa los diferentes atributos de los
    elementos en SugarCRM."""
    def __init__(self):
        pass

# La API de SOAP tiene varios tipos: id, datetime, assigned_user_name, text,
#  bool, relate, enum (complicado -> options[name, value]), varchar, phone,
#  date, int.

class TipoSugar_id(TipoSugar):
    """Identificador unico en SugarCRM."""
    def __init__(self, opciones = None):
        self.valor = ''

    def validar(self):
        if type(self.valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True

class TipoSugar_datetime(TipoSugar):
    """Dato que almacena fecha y hora en SugarCRM.
    En SugarCRM el formato es YYYY-MM-DD HH:mm:SS"""
    def __init__(self, opciones = None):
        self.valor = ''

    def validar(self):
        if type(self.valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True

class TipoSugar_assigned_user_name(TipoSugar):
    """Dato que almacena un nombre de usuario en SugarCRM."""
    def __init__(self, opciones = None):
        self.valor = ''

    def validar(self):
        if type(self.valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True

class TipoSugar_text(TipoSugar):
    """Dato que almacena el contenido de un campo de texto en SugarCRM."""
    def __init__(self, opciones = None):
        self.valor = ''

    def validar(self):
        if type(self.valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True

class TipoSugar_bool(TipoSugar):
    """Dato que almacena un dato booleano en SugarCRM."""
    def __init__(self, opciones = None):
        self.valor = True

    def validar(self):
        if type(self.valor) != types.BooleanType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un booleano.")
        return True

class TipoSugar_relate(TipoSugar):
    """Dato que almacena una relacion entre campos en SugarCRM."""
    def __init__(self, opciones = None):
        self.valor = ''

    def validar(self):
        if type(self.valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True

class TipoSugar_enum(TipoSugar):
    """Dato que almacena un dato que puede tomar multiples valores en
    SugarCRM."""
    def __init__(self, opciones):
        # Inicializo el valor como el primer dato disponible en las opciones de
        #  inicializacion.
        self.valor = opciones.keys()[0]
        self.opciones = opciones
##################### Que pasa si no hay opciones???

    def validar(self):
        if self.valor in self.opciones.keys():
            return True
        else:
            raise ErrorSugar("Valor de la opcion incorrecto.")

class TipoSugar_varchar(TipoSugar):
    """Dato que almacena un string en SugarCRM."""
    def __init__(self, opciones = None):
        self.valor = ''

    def validar(self):
        if type(self.valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True

class TipoSugar_phone(TipoSugar):
    """Dato que almacena un numero telefonico en SugarCRM."""
    def __init__(self, opciones = None):
        self.valor = ''
    
    def validar(self):
        if type(self.valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True

class TipoSugar_date(TipoSugar):
    """Dato que almacena una fecha en SugarCRM.
    En SugarCRM el formato es YYYY-MM-DD"""
    def __init__(self, opciones = None):
        self.valor = ''
    
    def validar(self):
        if type(self.valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True

class TipoSugar_int(TipoSugar):
    """Dato que almacena un valor entero en SugarCRM."""
    def __init__(self, opciones = None):
        self.valor = 0
        
    def validar(self):
        if type(self.valor) != types.IntType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un entero.")
        return True

class InstanciaSugar:
    """Una instancia de Sugar es una instalacion en particular, es decir
    los datos para accederla: URL, nombre de usuario, contrasena."""
    
    def __init__(self, url, usuario, clave, modulos):
        self.url = url
        self.usuario = usuario
        self.clave = clave
        
        self.wsdl = SOAPpy.WSDL.Proxy(url)
        #self.wsdl.soapproxy.config.dumpSOAPOut = 1
        #self.wsdl.soapproxy.config.dumpSOAPIn = 1
        
        resultado = self.wsdl.login({'user_name': usuario,
                            'password': hashlib.md5(clave).hexdigest(),
                            'version': '0.1'}, 'Sugar.py')
        if int(resultado['error']['number']) != 0:
            raise ErrorSugar('Error en parametros de autenticacion.')
        
        self.sesion = resultado['id']
        
        self.modulos = {}
        for modulo in modulos:
            self.modulos[modulo] = ModuloSugar(self, modulo)


class ModuloSugar:
    """Clase que define un modulo accesible sobre Sugar."""
    
    def __init__(self, instancia, nombre_modulo):
        self.nombre_modulo = nombre_modulo
        self.instancia = instancia
        
        # Obtengo mediante la API de SugarCRM los campos del modulo.
        # La API de SOAP tiene varios tipos: id, datetime, assigned_user_name,
        #  text, bool, relate, enum (complicado -> options[name, value]), 
        #  varchar, phone, date, int.
        
        # Agrego un mapeo entre los nombres de los campos y sus respectivos
        # tipos.
        resultado = self.instancia.wsdl.get_module_fields(self.instancia.sesion,
                                                         self.nombre_modulo)
        print nombre_modulo
        print resultado
        if resultado['error'] != '' and resultado['error']['number'] != None:
            raise ErrorSugar('Error al obtener la lista de campos del modulo')
        
        self.campos = []            # Todos los campos del modulo.
        self.campos_requeridos = [] # Aquellos campos que son requeridos
        self.campos_tipo = {}       # Mapeo entre los campos y el nombre de la
                                    #  clase hija de TipoSugar correspondiente.
        self.campos_parametros = {} # Mapeo entre los campos y el diccionario
                                    # de parametros a pasarle al constructor del
                                    # tipo definido en campos_tipo.
        for campo in resultado['module_fields']:
            self.campos.append(campo['name'])
            if campo['required'] != 0:
                # Agrego este campo a la lista de campos requeridos.
                self.campos_requeridos.append(campo['name'])
            
            # Ahora determino el tipo del campo.
            self.campos_tipo[campo['name']] = 'TipoSugar_' + campo['type']
            
            # Si el campo es de tipo enum, en los parametros del campo tengo que
            #  almacenar un dict con los pares name => value.
            if campo['type'] == 'enum':
                opciones = {}
                for opcion in campo['options']:
                    opciones[opcion['name']] = opcion['value']
                # Paso este diccionario al diccionario de parametros del tipo.
                self.campos_parametros[campo['name']] = opciones
            else:
                self.campos_parametros[campo['name']] = None


#    def buscar(self, nombre_campo, valor, campos_devueltos):
    def buscar(self, nombre_campo, valor):
        """Devuelve la lista de objetos que cumplen con el criterio
        especificado."""
        resultado = self.instancia.wsdl.get_entry_list(self.instancia.sesion,
                                        self.nombre_modulo,
                                        self.nombre_modulo.lower() +'.'+ nombre_campo + 
                                        ' LIKE "' + valor + '"', ''
#                                        , 0, campos_devueltos)
                                        , 0)
#        print resultado['result_count'] + ' resultados'
        
        lista = []
        for i in range(resultado['result_count']):
            nuevo = ObjetoSugar(self)
            for atributo in resultado['entry_list'][i]['name_value_list']:
                nuevo.modificar_campo(atributo['name'], atributo['value'])
            lista.append(nuevo)
        return lista


class ObjetoSugar:
    """Clase que define los elementos de cualquiera de los modulos de Sugar."""
    
    def __init__(self, modulo):
        """Creo una instancia de un objeto nuevo o existente."""

        # Dejo una referencia al modulo al que pertenece el objeto.
        self.modulo = modulo
        
        # El objeto tiene un campo con el mapeo 'nombre_campo' => valor para 
        # cada uno de los campos del objeto (valor es algo de tipo TipoSugar).
        self.campos = {}
        for campo in self.modulo.campos:
            # Para cada campo posible en el modulo, hago:
            opciones = self.modulo.campos_parametros[campo]
            self.campos[campo] = eval(self.modulo.campos_tipo[campo])(opciones)
    

    def validar(self):
        """Verifica que los campos presentes en el objeto sean los apropiados
        para el modulo al que el objeto pertenece. A su vez verifica que los
        tipos de los atributos sean los apropiados."""
        
        for campo in self.campos.keys():
            self.campos[campo].validar()
        
    def obtener_campo(self, nombre_campo):
        """Devuelve el valor del campo pasado como parametro."""
        return self.campos[nombre_campo]
    
    def modificar_campo(self, nombre_campo, nuevo_valor):
        """Escribe el nuevo valor del campo pasado como parametro."""
        self.campos[nombre_campo] = nuevo_valor

    def grabar(self):
        """Guarda el objeto en el SugarCRM, a traves de SOAP. Si el campo id
        no esta definido, se creara un objeto nuevo."""
        
        # nvl es la name_value_list, que tiene la lista de atributos.
        nvl = []
        for campo in self.campos.keys():
            # defino un name_value individual.
            nv = {}
            nv['name'] = campo
            nv['value'] = self.obtener_campo(campo)
#            print nv
            nvl.append(nv)
        
        # utilizo set_entry para actualizar el registro en SugarCRM.
        resultado = self.modulo.instancia.wsdl.set_entry(self.modulo.instancia.sesion,
                                                            self.modulo.nombre_modulo,
                                                            nvl)
        print 'resultado: '
        print resultado



