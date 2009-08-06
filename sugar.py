
import SOAPpy
import hashlib
import crm_config

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
    def __init__(self):
        pass

class TipoSugar_datetime(TipoSugar):
    """Dato que almacena fecha y hora en SugarCRM."""
    def __init__(self):
        pass

class TipoSugar_int(TipoSugar):
    """Valor entero en SugarCRM."""
    def __init__(self, digitos, inf, sup):
        """Inicializa el tipo de datos. Se pueden proporcionar la cantidad de
        digitos de precision, y las cotas inferior y superior para poder validar
        los datos ingresados posteriormente."""
        self.digitos = digitos
        self.inf = inf
        self.sup = sup
    
    def validar(self, valor):
        if len(str(valor)) > self.digitos:
            raise ErrorSugar("Demasiados digitos.")
        elif not self.inf <= int(valor) <= self.sup:
            raise ErrorSugar("Valor fuera de cota.")
    
    def asignar(self, valor):
        self.validar(valor)
        self.valor = valor

class InstanciaSugar:
    """Una instancia de Sugar es una instalacion en particular, es decir
    los datos para accederla: URL, nombre de usuario, contrasena."""
    
    def __init__(self, url, usuario, clave):
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
        
        # Obtengo la lista de modulos accesibles:
        resultado = self.wsdl.get_available_modules(self.sesion)
        if int(resultado['error']['number']) != 0:
            raise ErrorSugar('Error al obtener la lista de modulos')
        
        # Creo un diccionario dentro de la instancia con todos los modulos disp.
        self.modulos = {}
        for modulo in resultado['modules']:
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
        if int(resultado['error']['number']) != 0:
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
            if campo['type'] = 'enum':
                opciones = {}
                for opcion in campo['options']:
                    opciones[opcion['name']] = opcion['value']
                # Paso este diccionario al diccionario de parametros del tipo.
                self.campos_parametros[campo['name']] = opciones


class ObjetoSugar:
    """Clase que define los elementos de cualquiera de los modulos de Sugar."""
    
    def __init__(self, modulo):
        """Creo una instancia de un objeto nuevo o existente."""

        # Dejo una referencia al modulo al que pertenece el objeto.
        self.modulo = modulo
    
    def validar(self):
        """Verifica que los campos presentes en el objeto sean los apropiados
        para el modulo al que el objeto pertenece. A su vez verifica que los
        tipos de los atributos sean los apropiados."""
    
    def grabar(self):
        """Guarda el objeto en el SugarCRM, a traves de SOAP. Si el campo id
        no esta definido, se creara un objeto nuevo."""




