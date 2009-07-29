
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
        self.requerido = 0

class EnteroSugar(TipoSugar):
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
        
        # Obtengo tambien mediante la API se sugar los campos del modulo
        # La API de SOAP tiene varios tipos: id, datetime, assigned_user_name,
        #  text, bool, relate, enum (complicado -> options[name, value]), 
        #  varchar, phone, date, int.
        
        # Si agrego aca un dict con nombre_campo -> ClaseTipo?

