
# Descripcion: libreria de sugar

import SOAPpy
import hashlib
import types
import time

class ErrorSugar(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class TipoSugar:
    """Tipo de datos abstracto que representa los diferentes atributos de los
    elementos en SugarCRM."""
    
    def asignar(self, valor):
        self.validar(valor)
        self.valor = valor
    
    def a_sugar(self):
        if self.valor != None:
            return self.valor
        else:
            return ''
    
    def de_string(self, valor):
        return valor

# La API de SOAP tiene varios tipos: id, datetime, assigned_user_name, text,
#  bool, relate, enum (complicado -> options[name, value]), varchar, phone,
#  date, int.

class TipoSugar_id(TipoSugar):
    """Identificador unico en SugarCRM."""
    def __init__(self, valor_inicial = None, opciones = None):
        self.valor = valor_inicial

    def validar(self, valor):
        if type(valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True


class TipoSugar_datetime(TipoSugar):
    """Dato que almacena fecha y hora en SugarCRM.
    En SugarCRM el formato es YYYY-MM-DD HH:mm:SS"""
    def __init__(self, valor_inicial = None, opciones = None):
        try:
            self.valor = time.strptime(valor_inicial, '%Y-%m-%d %H:%M:%S')
        except Exception:
            self.valor = None
            
    def validar(self, valor):
        if type(valor) != type(time.strptime('2009', '%Y')):
            raise ErrorSugar("Tipo incorrecto. Esperaba un struct_time.")
        return True
    
    def a_sugar(self):
        try:
            valor = "%04i-%02i-%02i %02i:%02i:%02i" % (self.valor.tm_year,
                    self.valor.tm_mon, self.valor.tm_mday, self.valor.tm_hour,
                    self.valor.tm_min, self.valor.tm_sec)
            return valor
        except AttributeError:
            return ''

    def de_string(self, valor):
        return time.strptime(valor, '%Y-%m-%d %H:%M:%S')


class TipoSugar_assigned_user_name(TipoSugar):
    """Dato que almacena un nombre de usuario en SugarCRM."""
    def __init__(self, valor_inicial = None, opciones = None):
        self.valor = valor_inicial

    def validar(self, valor):
        if type(valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True


class TipoSugar_text(TipoSugar):
    """Dato que almacena el contenido de un campo de texto en SugarCRM."""
    def __init__(self, valor_inicial = None, opciones = None):
        self.valor = valor_inicial

    def validar(self, valor):
        if type(valor) != types.UnicodeType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True


class TipoSugar_bool(TipoSugar):
    """Dato que almacena un dato booleano en SugarCRM."""
    def __init__(self, valor_inicial = '0', opciones = None):
        if valor_inicial == '0':
            self.valor = False
        else:
            self.valor = True

    def validar(self, valor):
        if type(valor) != types.BooleanType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un booleano.")
        return True
    
    def a_sugar(self):
        if self.valor == True:
            return '1'
        else:
            return '0'

    def de_string(self, valor):
        if valor == '0':
            return False
        else:
            return True


class TipoSugar_relate(TipoSugar):
    """Dato que almacena una relacion entre campos en SugarCRM."""
    def __init__(self, valor_inicial = None, opciones = None):
        self.valor = valor_inicial

    def validar(self, valor):
        if type(valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True


class TipoSugar_enum(TipoSugar):
    """Dato que almacena un dato que puede tomar multiples valores en
    SugarCRM."""
    def __init__(self, valor_inicial = None, opciones = None):
        # Inicializo el valor como el primer dato disponible en las opciones de
        #  inicializacion, si no hay un valor inicial disponible.
        if valor_inicial == None or valor_inicial not in opciones.keys():
            self.valor = opciones.keys()[0]
        else:
            self.valor = valor_inicial
        
        self.opciones = opciones

    def validar(self, valor):
        if valor in self.opciones.keys():
            return True
        else:
            raise ErrorSugar("Valor de la opcion incorrecto.")

    def de_string(self, valor):
        if valor in self.opciones:
            return valor
        else:
            raise ValueError


class TipoSugar_varchar(TipoSugar):
    """Dato que almacena un string en SugarCRM."""
    def __init__(self, valor_inicial = None, opciones = None):
        self.valor = valor_inicial

    def validar(self, valor):
        if type(valor) != types.UnicodeType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True


class TipoSugar_phone(TipoSugar):
    """Dato que almacena un numero telefonico en SugarCRM."""
    def __init__(self, valor_inicial = None, opciones = None):
        self.valor = valor_inicial
    
    def validar(self, valor):
        if type(valor) != types.StringType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un string.")
        return True


class TipoSugar_date(TipoSugar):
    """Dato que almacena una fecha en SugarCRM.
    En SugarCRM el formato es YYYY-MM-DD"""
    def __init__(self, valor_inicial = None, opciones = None):
        try:
            self.valor = time.strptime(valor_inicial, '%Y-%m-%d')
        except Exception:
            self.valor = None
    
    def validar(self, valor):
        if type(valor) != type(time.strptime('2009', '%Y')):
            raise ErrorSugar("Tipo incorrecto. Esperaba un struct_time.")
        return True
    
    def a_sugar(self):
        try:
            valor = "%04i-%02i-%02i" % (self.valor.tm_year, self.valor.tm_mon,
                                    self.valor.tm_mday)
            return valor
        except AttributeError:
            return ''

    def de_string(self, valor):
        try:
            valor_nuevo = time.strptime(valor, '%Y-%m-%d')
            return valor_nuevo
        except ValueError:
            return None


class TipoSugar_int(TipoSugar):
    """Dato que almacena un valor entero en SugarCRM."""
    def __init__(self, valor_inicial = None, opciones = None):
        if valor_inicial not in [None, '']:
            self.valor = int(valor_inicial)
        else:
            self.valor = None
        
    def validar(self, valor):
        if type(valor) != types.IntType:
            raise ErrorSugar("Tipo incorrecto. Esperaba un entero.")
        return True
    
    def a_sugar(self):
        if self.valor != None:
            return str(self.valor)
        else:
            return ''

    def de_string(self, valor):
        try:
            valor_nuevo = int(valor)
            return valor_nuevo
        except ValueError:
            return None


TipoSugar_name = TipoSugar_varchar
TipoSugar_parent_type = TipoSugar_varchar
TipoSugar_user_name = TipoSugar_varchar


class InstanciaSugar:
    """Una instancia de Sugar es una instalacion en particular, es decir
    los datos para accederla: URL, nombre de usuario, contrasena."""
    
    def __init__(self, url, usuario, clave, modulos):
        self.url = url
        self.usuario = usuario
        self.clave = clave
        
        self.wsdl = SOAPpy.WSDL.Proxy(url)
#        self.wsdl.soapproxy.config.dumpSOAPOut = 1
#        self.wsdl.soapproxy.config.dumpSOAPIn = 1
        password = hashlib.md5()
        password.update(clave)
        resultado = self.wsdl.login({'user_name': usuario,
                            'password': password.hexdigest(),
                            'version': '0.1'}, 'Sugar.py')
        if int(resultado['error']['number']) != 0:
            raise ErrorSugar('Error en parametros de autenticacion.')
        
        self.sesion = resultado['id']
        
        self.modulos = {}
        for modulo in modulos:
            self.modulos[modulo] = ModuloSugar(self, modulo)
    
    def relacionar(self, principal, secundario):
        rel = {}
        rel['module1'] = principal.modulo.nombre_modulo
        rel['module1_id'] = principal.obtener_campo('id').a_sugar()
        rel['module2'] = secundario.modulo.nombre_modulo
        rel['module2_id'] = secundario.obtener_campo('id').a_sugar()
        
        self.wsdl.set_relationship(self.sesion, rel)
        

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


    def buscar(self, inicio = 0, cantidad = 20, **consulta):
        """Devuelve la lista de objetos que cumplen con el criterio
        especificado."""
        
        # Debo construir es string de la consulta a partir de los valores
        #  obtenidos mediante el parametro 'consulta'.
        str_cons = ''
        for clave in consulta.keys():
            # Si ya habia agregado alguna condicion antes, pongo un AND al medio
            if str_cons != '':
                str_cons += ' AND '
            
            if_cstm = ''
            if clave.endswith('_c'):
                if_cstm = '_cstm'
            
            str_cons += self.nombre_modulo.lower() + if_cstm + '.' + clave + \
                                ' = "' + consulta[clave] + '"'
#        print str_cons        
        resultado = self.instancia.wsdl.get_entry_list(self.instancia.sesion,
                                        self.nombre_modulo, str_cons, '', inicio,
                                        [], cantidad, 0)
        
        lista = []
        for i in range(resultado['result_count']):
            # Defino el diccionario con los valores de inicializacion del objeto
            valores_iniciales = {}
            for atributo in resultado['entry_list'][i]['name_value_list']:
                valores_iniciales[atributo['name']] = atributo['value']
            
            nuevo = ObjetoSugar(self, valores_iniciales)
            lista.append(nuevo)
        return lista


class ObjetoSugar:
    """Clase que define los elementos de cualquiera de los modulos de Sugar."""
    
    def __init__(self, modulo, valores_iniciales = {}):
        """Creo una instancia de un objeto nuevo o existente."""

        # Dejo una referencia al modulo al que pertenece el objeto.
        self.modulo = modulo
        
        # El objeto tiene un campo con el mapeo 'nombre_campo' => valor para 
        # cada uno de los campos del objeto (valor es algo de tipo TipoSugar).
        self.campos = {}
        self.campos_sucios = []
        for campo in self.modulo.campos:
            # Para cada campo posible en el modulo, hago:
            opciones = self.modulo.campos_parametros[campo]
            self.campos[campo] = eval(self.modulo.campos_tipo[campo])\
                                    (valores_iniciales.get(campo), opciones)
    

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
        
        self.campos[nombre_campo].asignar(nuevo_valor)
        self.campos_sucios.append(nombre_campo)
        

    def importar_campo(self, nombre_campo, nuevo_valor):
        """Escribe el nuevo valor del campo con el string del parametro."""
        
        valor = self.campos[nombre_campo].de_string(nuevo_valor)
        self.modificar_campo(nombre_campo, valor)


    def grabar(self):
        """Guarda el objeto en el SugarCRM, a traves de SOAP. Si el campo id
        no esta definido, se creara un objeto nuevo."""
        
        # Si 'id' no estaba en blanco, lo agrego a los campos sucios, para que
        # sugar actualice el objeto, en vez de crear uno nuevo.
        if self.obtener_campo('id').a_sugar() != '':
            self.campos_sucios.append('id')
        
        # nvl es la name_value_list, que tiene la lista de atributos.
        nvl = []
        for campo in set(self.campos_sucios):
            # defino un name_value individual.
            nv = {}
            nv['name'] = campo
            nv['value'] = self.obtener_campo(campo).a_sugar()
            nvl.append(nv)
        
        # utilizo set_entry para actualizar el registro en SugarCRM.
        resultado = self.modulo.instancia.wsdl.set_entry(
                                                self.modulo.instancia.sesion,
                                                self.modulo.nombre_modulo, nvl)
        self.modificar_campo('id', resultado['id'])
        if resultado['error']['number'] == '0':
            self.campos_sucios = []

        
        return resultado['error']


    def relacionar(self, obj_principal, nombre_campo):
        """Relaciona este objeto con el objeto obj_principal, siendo este
        objeto el related. Usa nombre_campo como el campo de referencia para
        conectarlos."""
        
        # nvl es la name_value_list que guarda el par de identificadores que se
        # insertaran en la relacion
        id = self.obtener_campo('id').a_sugar()
        relacionar_con = obj_principal.obtener_campo('id').a_sugar()
        nvl = []
        nvl.append({'name': 'id', 'value': id})
        nvl.append({'name': nombre_campo, 'value': relacionar_con})
        resultado = self.modulo.instancia.wsdl.set_entry(
                self.modulo.instancia.sesion, self.modulo.nombre_modulo, nvl)


