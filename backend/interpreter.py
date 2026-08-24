# --- INTERPRETE ---

import re

class Entorno:
    def __init__(self, padre=None):
        self.variables = {}
        self.padre = padre
        self.etiquetas = {}  # Para loops con etiquetas
        self.structs = {}
    
    def declarar(self, nombre, valor, mutable=False):
        self.variables[nombre] = {
            'valor': valor,
            'mutable': mutable
        }
    
    def obtener(self, nombre):
        if nombre in self.variables:
            return self.variables[nombre]['valor']
        if self.padre:
            return self.padre.obtener(nombre)
        raise Exception(f"Variable no definida: {nombre}")
    
    def asignar(self, nombre, valor):
        if nombre in self.variables:
            if not self.variables[nombre]['mutable']:
                raise Exception(f"Variable inmutable: {nombre}")
            self.variables[nombre]['valor'] = valor
            return
        if self.padre:
            self.padre.asignar(nombre, valor)
            return
        raise Exception(f"Variable no definida: {nombre}")
    
    def existe(self, nombre):
        if nombre in self.variables:
            return True
        if self.padre:
            return self.padre.existe(nombre)
        return False
    
    def crear_hijo(self):
        return Entorno(self)

    def declarar_struct(self, nombre, campos):
        self.structs[nombre] = campos

    def obtener_struct(self, nombre):
        if nombre in self.structs:
            return self.structs[nombre]
        if self.padre:
            return self.padre.obtener_struct(nombre)
        raise Exception(f"Struct no definido: {nombre}")

class Interprete:
    def __init__(self):
        self.entorno_global = Entorno()
        self.entorno_actual = self.entorno_global
        self.funciones = {}
        self.salida = []
        self.errores = []
        self.lineas = {}  # id(nodo_sentencia) -> numero de linea (viene del parser)
        self.lineas_con_error_semantico = set()  # lineas que el semantico ya marco como invalidas
    
    def ejecutar(self, ast, lineas=None, lineas_con_error_semantico=None):
        self.salida = []
        self.errores = []
        self.lineas = lineas or {}
        # Si el analizador semantico ya reporto un error, el interprete no vuelve a ejecutar esa sentencia para no mostrar el mimso problema dos veces
        self.lineas_con_error_semantico = lineas_con_error_semantico or set()
        programa = ast

        # Registrar todas las funciones y structs
        for declaracion in programa[1]:
            if declaracion[0] == 'funcion':
                self.funciones[declaracion[1]] = declaracion
            elif declaracion[0] == 'struct':
                self.entorno_global.declarar_struct(declaracion[1], declaracion[2])

        # Buscar y ejecutar main
        if 'main' not in self.funciones:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': 'No se encontro la funcion main.',
            })
            return self.salida, self.errores
        
        try:
            self._ejecutar_funcion('main', [])
        except Exception as e:
            self.errores.append({'tipo': 'Semantico', 'linea': 0, 'mensaje': str(e)})

        return self.salida, self.errores
    
    def _ejecutar_funcion(self, nombre, argumentos):
        funcion = self.funciones.get(nombre)
        if not funcion:
            raise Exception(f"Funcion no definida: {nombre}")
        
        # Crear nuevo entorno
        entorno_anterior = self.entorno_actual
        self.entorno_actual = Entorno(self.entorno_global)
        
        # Asignar parametros
        params = funcion[2]
        cuerpo = funcion[4] if len(funcion) > 4 else []
        
        for i, (nom_param, tipo_param) in enumerate(params):
            if i < len(argumentos):
                self.entorno_actual.declarar(nom_param, argumentos[i], True)
            else:
                self.entorno_actual.declarar(nom_param, None, True)
        
        # Ejecutar cuerpo
        resultado = self._ejecutar_lista_sentencias(cuerpo)
        self.entorno_actual = entorno_anterior
        if isinstance(resultado, dict) and resultado.get('tipo') == 'return':
            return resultado['valor']
        return None
    
    def _ejecutar_lista_sentencias(self, cuerpo):
        # Ejecuta las sentencias en el entorno actual y si una sentencia falla en la ejecucion se registra el error y continua con el siguiente
        for sentencia in cuerpo:
            linea = self.lineas.get(id(sentencia), 0)
            if linea and linea in self.lineas_con_error_semantico:
                # Ya se reporto un error semantico en esa linea y no se ejecuta
                continue
            try:
                resultado = self._ejecutar_sentencia(sentencia)
            except Exception as e:
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': linea,
                    'mensaje': str(e),
                })
                continue
            if isinstance(resultado, dict) and resultado.get('tipo') in ('return', 'break', 'continue'):
                return resultado
        return None
    
    def _ejecutar_sentencia(self, sentencia):
        tipo = sentencia[0]
        
        if tipo == 'let':
            return self._ejecutar_let(sentencia)
        elif tipo == 'asignar':
            return self._ejecutar_asignacion(sentencia)
        elif tipo == 'if':
            return self._ejecutar_if(sentencia)
        elif tipo == 'while':
            return self._ejecutar_while(sentencia)
        elif tipo == 'loop':
            return self._ejecutar_loop(sentencia)
        elif tipo == 'return':
            return self._ejecutar_return(sentencia)
        elif tipo == 'struct':
            return self._ejecutar_struct(sentencia)
        elif tipo == 'break':
            return {'tipo': 'break', 'etiqueta': sentencia[1]}
        elif tipo == 'continue':
            return {'tipo': 'continue', 'etiqueta': sentencia[1]}
        elif tipo == 'match':
            return self._ejecutar_match(sentencia)
        elif tipo == 'llamada':
            return self._ejecutar_llamada(sentencia)
        elif tipo == 'binop':
            return self._ejecutar_binop(sentencia)
        elif tipo == 'unop':
            return self._ejecutar_unop(sentencia)
        elif tipo == 'literal':
            return sentencia[1]
        elif tipo == 'string':
            return sentencia[1]
        elif tipo == 'char':
            return sentencia[1]
        elif tipo == 'bool':
            return sentencia[1]
        elif tipo == 'var':
            return self.entorno_actual.obtener(sentencia[1])
        
        return None
    
    def _ejecutar_let(self, nodo):
        nombre = nodo[1]
        tipo = nodo[2]
        valor = nodo[3]
        mutable = nodo[4]
        
        valor_ejecutado = None
        if valor is not None:
            valor_ejecutado = self._ejecutar_expresion(valor)
        
        self.entorno_actual.declarar(nombre, valor_ejecutado, mutable)
        return None
    
    def _ejecutar_asignacion(self, nodo):
        nombre = nodo[1]
        valor = nodo[2]
        
        valor_ejecutado = self._ejecutar_expresion(valor)
        self.entorno_actual.asignar(nombre, valor_ejecutado)
        return None
    
    def _ejecutar_if(self, nodo):
        condicion = nodo[1]
        cuerpo_entonces = nodo[2]
        cuerpo_sino = nodo[3] if len(nodo) > 3 else None
        
        condicion_valor = self._ejecutar_expresion(condicion)
        
        if condicion_valor:
            entorno_anterior = self.entorno_actual
            self.entorno_actual = Entorno(self.entorno_actual)
            resultado = self._ejecutar_lista_sentencias(cuerpo_entonces)
            self.entorno_actual = entorno_anterior
            if isinstance(resultado, dict) and resultado.get('tipo') in ('return', 'break', 'continue'):
                return resultado
        elif cuerpo_sino:
            entorno_anterior = self.entorno_actual
            self.entorno_actual = Entorno(self.entorno_actual)
            
            if isinstance(cuerpo_sino, list):
                resultado = self._ejecutar_lista_sentencias(cuerpo_sino)
            else:
                resultado = self._ejecutar_sentencia(cuerpo_sino)
            self.entorno_actual = entorno_anterior
            if isinstance(resultado, dict) and resultado.get('tipo') in ('return', 'break', 'continue'):
                return resultado
        
        return None
    
    def _ejecutar_while(self, nodo):
        condicion = nodo[1]
        cuerpo = nodo[2]
        
        while True:
            condicion_valor = self._ejecutar_expresion(condicion)
            if not condicion_valor:
                break
            
            entorno_anterior = self.entorno_actual
            self.entorno_actual = Entorno(self.entorno_actual)
            resultado = self._ejecutar_lista_sentencias(cuerpo)
            self.entorno_actual = entorno_anterior
            
            if isinstance(resultado, dict):
                if resultado.get('tipo') == 'return':
                    return resultado
                elif resultado.get('tipo') == 'break':
                    # Si el break trae una etiqueta no es para este while, hay que burbujearlo al loop externo correspondiente
                    etiqueta = resultado.get('etiqueta')
                    return None if etiqueta is None else resultado
                elif resultado.get('tipo') == 'continue':
                    etiqueta = resultado.get('etiqueta')
                    if etiqueta is not None:
                        return resultado
                    # etiqueta None: sigue con la siguiente iteracion del while
        
        return None
    
    def _ejecutar_loop(self, nodo):
        etiqueta = nodo[1]
        cuerpo = nodo[2]
        
        while True:
            entorno_anterior = self.entorno_actual
            self.entorno_actual = Entorno(self.entorno_actual)
            resultado = self._ejecutar_lista_sentencias(cuerpo)
            self.entorno_actual = entorno_anterior
            
            if isinstance(resultado, dict):
                if resultado.get('tipo') == 'return':
                    return resultado
                elif resultado.get('tipo') == 'break':
                    etiqueta_break = resultado.get('etiqueta')
                    # Si no trae etiqueta o la etiqueta es la de este loop, se detiene aqui
                    # Si trae otra etiqueta, se burbujea hacia arriba
                    if etiqueta_break is None or etiqueta_break == etiqueta:
                        return None
                    return resultado
                elif resultado.get('tipo') == 'continue':
                    etiqueta_continue = resultado.get('etiqueta')
                    if etiqueta_continue is not None and etiqueta_continue != etiqueta:
                        return resultado
                    # etiqueta None o de este loop: sigue con la siguiente iteracion
    
    def _ejecutar_match(self, nodo):
        valor = self._ejecutar_expresion(nodo[1])
        casos = nodo[2]
        
        cuerpo_a_ejecutar = None
        cuerpo_default = None
        for caso in casos:
            patron, cuerpo = caso[1], caso[2]
            if patron == 'default':
                cuerpo_default = cuerpo
                continue
            if patron == valor:
                cuerpo_a_ejecutar = cuerpo
                break
        
        if cuerpo_a_ejecutar is None:
            cuerpo_a_ejecutar = cuerpo_default
        if cuerpo_a_ejecutar is None:
            return None
        
        entorno_anterior = self.entorno_actual
        self.entorno_actual = Entorno(self.entorno_actual)
        resultado_final = self._ejecutar_lista_sentencias(cuerpo_a_ejecutar)
        self.entorno_actual = entorno_anterior
        return resultado_final
    
    def _ejecutar_return(self, nodo):
        valor = nodo[1]
        if valor is not None:
            valor_ejecutado = self._ejecutar_expresion(valor)
            return {'tipo': 'return', 'valor': valor_ejecutado}
        return {'tipo': 'return', 'valor': None}

    def _ejecutar_struct(self, nodo):
            nombre = nodo[1]
            campos = nodo[2]
            self.entorno_actual.declarar_struct(nombre, campos)
            return None
    
    def _formatear_valor(self, valor):
        # Formatea un valor como Rust lo mostraria con {} (o {:?}) y los booleanos van en minuscula true/false
        if isinstance(valor, bool):
            return 'true' if valor else 'false'
        if isinstance(valor, list):
            return '[' + ', '.join(self._formatear_valor(v) for v in valor) + ']'
        if valor is None:
            return 'None'
        return str(valor)

    def _formatear_println(self, argumentos):
        # Sustituye los marcadores {} y {:?} del primer argumento por los valores siguientes en orden
        if argumentos and isinstance(argumentos[0], str) and re.search(r'\{(:\?)?\}', argumentos[0]):
            formato = argumentos[0]
            resto = list(argumentos[1:])

            def reemplazar(_match):
                if resto:
                    return self._formatear_valor(resto.pop(0))
                return _match.group(0)

            return re.sub(r'\{(:\?)?\}', reemplazar, formato)
        # Sin marcadores {}: se imprimen los argumentos separados por espacio
        return ' '.join(self._formatear_valor(arg) for arg in argumentos)

    def _ejecutar_llamada(self, nodo):
        nombre = nodo[1]
        argumentos = [self._ejecutar_expresion(arg) for arg in nodo[2]]
        
        # FUNCIONES EMBEBIDAS

        # Imprimir en consola
        if nombre == 'println':
            self.salida.append(self._formatear_println(argumentos))
            return None

        # Retornar el tipo de dato
        elif nombre == 'typeof':
            # Debe devolver el nombre de tipo del lenguaje (i32, f64, bool, String...)
            if argumentos:
                valor = argumentos[0]
                if isinstance(valor, bool):
                    return 'bool'
                if isinstance(valor, int):
                    return 'i32'
                if isinstance(valor, float):
                    return 'f64'
                if isinstance(valor, str):
                    return 'String'
                if isinstance(valor, list):
                    return 'array'
                return type(valor).__name__
            return 'null'

        # Retornar la longitud de un string/array
        elif nombre == 'len':
            if argumentos and isinstance(argumentos[0], (str, list)):
                return len(argumentos[0])
            return 0

        # Generar numero random
        elif nombre == 'random':
            import random
            if len(argumentos) >= 2:
                return random.randint(argumentos[0], argumentos[1])
            return random.randint(0, 100)

        # Verificar si un string tiene una subcadena
        elif nombre == 'contains':
            if len(argumentos) >= 2:
                if isinstance(argumentos[0], str):
                    return argumentos[1] in argumentos[0]
                elif isinstance(argumentos[0], list):
                    return argumentos[1] in argumentos[0]
            return False

        # Reemplazar una subcadena por otra en un string
        elif nombre == 'replace':
            if len(argumentos) >= 3:
                if isinstance(argumentos[0], str):
                    return argumentos[0].replace(argumentos[1], argumentos[2])
            return argumentos[0] if argumentos else ''

        # Dividir un string en partes con un separador
        elif nombre == 'split':
            if len(argumentos) >= 2:
                if isinstance(argumentos[0], str):
                    return argumentos[0].split(argumentos[1])
            return [argumentos[0]] if argumentos else []

        # Convertir a mayusculas
        elif nombre == 'to_uppercase':
            if argumentos and isinstance(argumentos[0], str):
                return argumentos[0].upper()
            return ''

        # Convertir a minusculas
        elif nombre == 'to_lowercase':
            if argumentos and isinstance(argumentos[0], str):
                return argumentos[0].lower()
            return ''

        # Invertir un string/lista
        elif nombre == 'reverse':
            if argumentos:
                if isinstance(argumentos[0], str):
                    return argumentos[0][::-1]
                elif isinstance(argumentos[0], list):
                    # Los arreglos son mutables y se invierten en su lugar
                    argumentos[0].reverse()
                    return argumentos[0]
            return argumentos[0] if argumentos else []
        
        # Funciones definidas por el usuario
        return self._ejecutar_funcion(nombre, argumentos)
    
    def _ejecutar_binop(self, nodo):
        operador = nodo[1]

        # && y || se evaluan con cortocircuito: si "izquierda" ya dio el resultado no se evalua "derecha"
        if operador == '&&':
            izquierda = self._ejecutar_expresion(nodo[2])
            if not izquierda:
                return False
            return bool(self._ejecutar_expresion(nodo[3]))
        elif operador == '||':
            izquierda = self._ejecutar_expresion(nodo[2])
            if izquierda:
                return True
            return bool(self._ejecutar_expresion(nodo[3]))

        izquierda = self._ejecutar_expresion(nodo[2])
        derecha = self._ejecutar_expresion(nodo[3])
        
        if operador == '+':
            return izquierda + derecha
        elif operador == '-':
            return izquierda - derecha
        elif operador == '*':
            return izquierda * derecha
        elif operador == '/':
            if derecha == 0:
                raise Exception("Division por cero")
            resultado = izquierda / derecha
            # i32 / i32 debe dar i32 (division entera, truncando hacia 0 como en Rust y no float)
            if isinstance(izquierda, int) and isinstance(derecha, int):
                return int(resultado)  # int() trunca hacia cero, igual que Rust
            return resultado
        elif operador == '%':
            if isinstance(izquierda, int) and isinstance(derecha, int):
                # Rust usa division truncada el signo del resultado sigue al dividendo)
                cociente_truncado = int(izquierda / derecha) if derecha != 0 else 0
                return izquierda - cociente_truncado * derecha
            return izquierda % derecha
        elif operador == '==':
            return izquierda == derecha
        elif operador == '!=':
            return izquierda != derecha
        elif operador == '>':
            return izquierda > derecha
        elif operador == '>=':
            return izquierda >= derecha
        elif operador == '<':
            return izquierda < derecha
        elif operador == '<=':
            return izquierda <= derecha
        
        raise Exception(f"Operador desconocido: {operador}")
    
    def _ejecutar_unop(self, nodo):
        operador = nodo[1]
        operando = self._ejecutar_expresion(nodo[2])
        
        if operador == '!':
            return not operando
        elif operador == '-':
            return -operando
        
        raise Exception(f"Operador unario desconocido: {operador}")
    
    def _ejecutar_expresion(self, expr):
        if isinstance(expr, (int, float, str, bool)):
            return expr
        if isinstance(expr, list):
            return [self._ejecutar_expresion(e) for e in expr]
    
        tipo = expr[0]
    
        if tipo == 'var':
            return self.entorno_actual.obtener(expr[1])
        elif tipo == 'string_from':
            # String::from(x) convierte x a texto (String::new() y llega como ('string', '') desde el parser)
            return str(self._ejecutar_expresion(expr[1]))
        elif tipo == 'array_literal':
            return [self._ejecutar_expresion(e) for e in expr[1]]
        elif tipo == 'array_repeat':
            valor = self._ejecutar_expresion(expr[1])
            count = expr[2]
            return [valor] * count
        elif tipo == 'array_access':
            arreglo = self._ejecutar_expresion(expr[1])
            indice = self._ejecutar_expresion(expr[2])
            if not isinstance(indice, int):
                raise Exception("Indice debe ser un entero")
            if indice < 0 or indice >= len(arreglo):
                raise Exception("Indice fuera de rango")
            return arreglo[indice]
        elif tipo == 'array_slice':
            arreglo = self._ejecutar_expresion(expr[1])
            start = self._ejecutar_expresion(expr[2])
            end = self._ejecutar_expresion(expr[3])
            return arreglo[start:end]
        elif tipo == 'struct_init':
            nombre = expr[1]
            valores = expr[2]
            struct_def = self.entorno_actual.obtener_struct(nombre)
            struct_obj = {}
            for campo, valor in valores:
                struct_obj[campo] = self._ejecutar_expresion(valor)
            # Verificar campos faltantes
            for campo, _ in struct_def:
                if campo not in struct_obj:
                    raise Exception(f"Campo faltante en struct {nombre}: {campo}")
            return struct_obj
        elif tipo == 'field_access':
            struct_obj = self._ejecutar_expresion(expr[1])
            campo = expr[2]
            if campo not in struct_obj:
                raise Exception(f"Campo no existe: {campo}")
            return struct_obj[campo]
        elif tipo == 'llamada':
            return self._ejecutar_llamada(expr)
    
        return self._ejecutar_sentencia(expr)