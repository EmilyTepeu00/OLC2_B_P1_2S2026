# --- ANALISIS SEMANTICO ---
# TABLA DE SIMBOLOS Y VALIDACION DE TIPOS

class Simbolo:
    def __init__(self, nombre, tipo_simbolo, tipo_dato, mutable=False, valor=None):
        self.nombre = nombre
        self.tipo_simbolo = tipo_simbolo  # 'variable', 'funcion', 'estructura'
        self.tipo_dato = tipo_dato        # 'i32', 'f64', 'bool', 'char', 'String'
        self.mutable = mutable
        self.valor = valor
        self.parametros = None      # Para funciones
        self.tipo_retorno = None    # Para funciones

class TablaSimbolos:
    def __init__(self, padre=None):
        self.simbolos = {}
        self.padre = padre
        self.hijos = []
    
    def agregar(self, nombre, simbolo):
        if nombre in self.simbolos:
            return False, f"Simbolo ya declarado: {nombre}"
        self.simbolos[nombre] = simbolo
        return True, None
    
    def obtener(self, nombre):
        if nombre in self.simbolos:
            return self.simbolos[nombre], None
        if self.padre:
            return self.padre.obtener(nombre)
        return None, f"Simbolo no encontrado: {nombre}"
    
    def crear_hijo(self):
        hijo = TablaSimbolos(self)
        self.hijos.append(hijo)
        return hijo

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_global = TablaSimbolos()
        self.tabla_actual = self.tabla_global
        self.errores = []
    
    def analizar(self, ast):
        self.errores = []
        programa = ast
        
        # PRIMERA PASADA: registrar todas las funciones
        for funcion in programa[1]:
            self._registrar_funcion(funcion)
        
        # SEGUNDA PASADA: analizar el cuerpo de las funciones
        for funcion in programa[1]:
            if funcion[0] == 'funcion':
                self._analizar_funcion(funcion)
        
        return self.errores
    
    def _registrar_funcion(self, nodo_funcion):
        nombre = nodo_funcion[1]
        parametros = nodo_funcion[2]
        tipo_retorno = nodo_funcion[3] if len(nodo_funcion) > 3 else None

        simbolo = Simbolo(nombre, 'funcion', tipo_retorno)
        simbolo.parametros = parametros
        simbolo.tipo_retorno = tipo_retorno

        ok, error = self.tabla_global.agregar(nombre, simbolo)
        if not ok:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': f"Funcion ya declarada: {nombre}"
            })
    
    def _analizar_funcion(self, nodo_funcion):
        nombre = nodo_funcion[1]
        parametros = nodo_funcion[2]
        tipo_retorno = nodo_funcion[3] if len(nodo_funcion) > 3 else None
        cuerpo = nodo_funcion[4] if len(nodo_funcion) > 4 else []

        # Crear ambito para la funcion
        self.tabla_actual = TablaSimbolos(self.tabla_global)

        # Registrar parametros como variables
        for nom_param, tipo_param in parametros:
            simbolo = Simbolo(nom_param, 'variable', tipo_param, True)
            ok, error = self.tabla_actual.agregar(nom_param, simbolo)
            if not ok:
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': 0,
                    'mensaje': f"Error registrando parametro: {nom_param}"
                })
        
        # Analizar cuerpo
        for sentencia in cuerpo:
            self._analizar_sentencia(sentencia)
        
        # Volver al ambito anterior
        self.tabla_actual = self.tabla_actual.padre
    
    def _analizar_sentencia(self, sentencia):
        if sentencia[0] == 'let':
            self._analizar_let(sentencia)
        elif sentencia[0] == 'asignar':
            self._analizar_asignacion(sentencia)
        elif sentencia[0] == 'if':
            self._analizar_if(sentencia)
        elif sentencia[0] == 'while':
            self._analizar_while(sentencia)
        elif sentencia[0] == 'loop':
            self._analizar_loop(sentencia)
        elif sentencia[0] == 'return':
            self._analizar_retorno(sentencia)
        elif sentencia[0] == 'llamada':
            self._analizar_llamada(sentencia)
        elif sentencia[0] == 'var':
            self._analizar_variable(sentencia)
        elif sentencia[0] == 'binop':
            self._analizar_binario(sentencia)
        elif sentencia[0] == 'unop':
            self._analizar_unario(sentencia)
        elif sentencia[0] == 'literal':
            pass
        elif sentencia[0] == 'string':
            pass
        elif sentencia[0] == 'bool':
            pass
        elif sentencia[0] == 'char':
            pass
    
    def _analizar_let(self, nodo_let):
        nombre = nodo_let[1]
        tipo = nodo_let[2]
        valor = nodo_let[3]
        mutable = nodo_let[4]
        
        # Si tiene valor, validar la expresion y obtener su tipo
        tipo_valor = None
        if valor is not None:
            self._analizar_expresion(valor)
            tipo_valor = self._obtener_tipo_expresion(valor)
        
        # Si no tiene tipo, inferir del valor
        if tipo is None and valor is not None:
            tipo = tipo_valor
        
        # Si tiene tipo y valor, validar compatibilidad
        if tipo is not None and valor is not None and tipo_valor is not None:
            if not self._son_tipos_compatibles(tipo, tipo_valor):
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': 0,
                    'mensaje': f"Tipos incompatibles: no se puede asignar {tipo_valor} a {tipo} en variable {nombre}"
                })
        
        simbolo = Simbolo(nombre, 'variable', tipo, mutable, valor)
        ok, error = self.tabla_actual.agregar(nombre, simbolo)
        if not ok:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': f"Variable ya declarada: {nombre}"
            })
    
    def _analizar_asignacion(self, nodo_asign):
        nombre = nodo_asign[1]
        valor = nodo_asign[2]
        
        # Verificar que la variable exista
        simbolo, error = self.tabla_actual.obtener(nombre)
        if error:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': f"Variable no declarada: {nombre}"
            })
            return
        
        # Verificar que sea mutable
        if not simbolo.mutable:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': f"Variable inmutable: {nombre}"
            })
            return
        
        # Validar la expresion
        self._analizar_expresion(valor)
        
        # Validar compatibilidad de tipos
        tipo_var = simbolo.tipo_dato
        tipo_valor = self._obtener_tipo_expresion(valor)
        
        if tipo_var is not None and tipo_valor is not None:
            if not self._son_tipos_compatibles(tipo_var, tipo_valor):
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': 0,
                    'mensaje': f"Tipos incompatibles: no se puede asignar {tipo_valor} a {tipo_var} en {nombre}"
                })
    
    def _analizar_if(self, nodo_if):
        condicion = nodo_if[1]
        cuerpo_entonces = nodo_if[2]
        cuerpo_sino = nodo_if[3] if len(nodo_if) > 3 else None
        
        # Validar que la condicion sea bool
        tipo_cond = self._obtener_tipo_expresion(condicion)
        if tipo_cond is not None and tipo_cond != 'bool':
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': f"La condicion del if debe ser booleana, pero es {tipo_cond}"
            })
        
        # Nuevo ambito para el bloque
        self.tabla_actual = TablaSimbolos(self.tabla_actual)
        for sentencia in cuerpo_entonces:
            self._analizar_sentencia(sentencia)
        self.tabla_actual = self.tabla_actual.padre
        
        if cuerpo_sino:
            self.tabla_actual = TablaSimbolos(self.tabla_actual)
            if isinstance(cuerpo_sino, list):
                for sentencia in cuerpo_sino:
                    self._analizar_sentencia(sentencia)
            else:
                self._analizar_sentencia(cuerpo_sino)
            self.tabla_actual = self.tabla_actual.padre
    
    def _analizar_while(self, nodo_while):
        condicion = nodo_while[1]
        cuerpo = nodo_while[2]
        
        # Validar que la condicion sea bool
        tipo_cond = self._obtener_tipo_expresion(condicion)
        if tipo_cond is not None and tipo_cond != 'bool':
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': f"La condicion del while debe ser booleana, pero es {tipo_cond}"
            })
        
        self.tabla_actual = TablaSimbolos(self.tabla_actual)
        for sentencia in cuerpo:
            self._analizar_sentencia(sentencia)
        self.tabla_actual = self.tabla_actual.padre
    
    def _analizar_loop(self, nodo_loop):
        etiqueta = nodo_loop[1]
        cuerpo = nodo_loop[2]
        
        self.tabla_actual = TablaSimbolos(self.tabla_actual)
        for sentencia in cuerpo:
            self._analizar_sentencia(sentencia)
        self.tabla_actual = self.tabla_actual.padre
    
    def _analizar_retorno(self, nodo_retorno):
        valor = nodo_retorno[1]
        if valor:
            self._analizar_expresion(valor)
    
    def _analizar_llamada(self, nodo_llamada):
        nombre = nodo_llamada[1]
        argumentos = nodo_llamada[2]
        
        # Funciones embebidas no necesitan validacion
        embebidas = ['println', 'typeof', 'random', 'len', 'contains', 
                    'replace', 'split', 'to_uppercase', 'to_lowercase', 'reverse']
        if nombre in embebidas:
            return
        
        # Verificar que la funcion exista
        simbolo, error = self.tabla_actual.obtener(nombre)
        if error:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': f"Funcion no declarada: {nombre}"
            })
            return
        
        # Validar numero de argumentos
        if simbolo.parametros is not None:
            if len(argumentos) != len(simbolo.parametros):
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': 0,
                    'mensaje': f"Numero incorrecto de argumentos para {nombre}: esperaba {len(simbolo.parametros)}, recibio {len(argumentos)}"
                })
    
    def _analizar_variable(self, nodo_var):
        nombre = nodo_var[1]
        simbolo, error = self.tabla_actual.obtener(nombre)
        if error:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': 0,
                'mensaje': f"Variable no declarada: {nombre}"
            })
    
    def _analizar_binario(self, nodo_binario):
        operador = nodo_binario[1]
        izquierda = nodo_binario[2]
        derecha = nodo_binario[3]
        
        tipo_izq = self._obtener_tipo_expresion(izquierda)
        tipo_der = self._obtener_tipo_expresion(derecha)
        
        # OPERADORES ARITMETICOS: +, -, *, /, %
        if operador in ['+', '-', '*', '/', '%']:
            # Suma: permite i32/f64 y String+String
            if operador == '+':
                if tipo_izq == 'String' and tipo_der == 'String':
                    pass
                elif tipo_izq in ['i32', 'f64'] and tipo_der in ['i32', 'f64']:
                    pass
                elif tipo_izq is not None and tipo_der is not None:
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': 0,
                        'mensaje': f"Operador '+' no permitido entre {tipo_izq} y {tipo_der}"
                    })

            # Multiplicacion: i32 * String
            elif operador == '*':
                if tipo_izq in ['i32', 'f64'] and tipo_der in ['i32', 'f64']:
                    pass
                elif tipo_izq == 'i32' and tipo_der == 'String':
                    pass
                elif tipo_izq is not None and tipo_der is not None:
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': 0,
                        'mensaje': f"Operador '*' no permitido entre {tipo_izq} y {tipo_der}"
                    })

            # Resta, Division, Modulo: solo numeros
            elif operador in ['-', '/', '%']:
                if tipo_izq in ['i32', 'f64'] and tipo_der in ['i32', 'f64']:
                    pass
                elif tipo_izq is not None and tipo_der is not None:
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': 0,
                        'mensaje': f"Operador '{operador}' no permitido entre {tipo_izq} y {tipo_der}"
                    })
        
        # OPERADORES RELACIONALES: ==, !=, >, <, >=, <=
        elif operador in ['==', '!=', '>', '<', '>=', '<=']:
            if tipo_izq is not None and tipo_der is not None:
                if not self._son_tipos_compatibles(tipo_izq, tipo_der):
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': 0,
                        'mensaje': f"Operador '{operador}' no permitido entre {tipo_izq} y {tipo_der}"
                    })
        
        # OPERADORES LOGICOS: &&, ||
        elif operador in ['&&', '||']:
            if tipo_izq is not None and tipo_der is not None:
                if tipo_izq != 'bool' or tipo_der != 'bool':
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': 0,
                        'mensaje': f"Operador '{operador}' solo funciona con booleanos, pero se encontró {tipo_izq} y {tipo_der}"
                    })
        
        # Analizar sub expresiones
        self._analizar_expresion(izquierda)
        self._analizar_expresion(derecha)
    
    def _analizar_unario(self, nodo_unario):
        operador = nodo_unario[1]
        operando = nodo_unario[2]
        
        tipo_op = self._obtener_tipo_expresion(operando)
        
        if operador == '!':
            if tipo_op is not None and tipo_op != 'bool':
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': 0,
                    'mensaje': f"Operador '!' solo funciona con booleanos, pero se encontró {tipo_op}"
                })
        elif operador == '-':
            if tipo_op is not None and tipo_op not in ['i32', 'f64']:
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': 0,
                    'mensaje': f"Operador '-' unario solo funciona con numeros, pero se encontró {tipo_op}"
                })
        
        self._analizar_expresion(operando)
    
    def _analizar_expresion(self, expr):
        if expr[0] == 'var':
            self._analizar_variable(expr)
        elif expr[0] == 'llamada':
            self._analizar_llamada(expr)
        elif expr[0] == 'binop':
            self._analizar_binario(expr)
        elif expr[0] == 'unop':
            self._analizar_unario(expr)
        elif expr[0] == 'literal':
            pass
        elif expr[0] == 'string':
            pass
        elif expr[0] == 'bool':
            pass
        elif expr[0] == 'char':
            pass

    # OBTENER EL TIPO DE LA EXPRESION
    def _obtener_tipo_expresion(self, expr):
        if expr[0] == 'literal':
            return 'i32' if isinstance(expr[1], int) else 'f64'
        elif expr[0] == 'string':
            return 'String'
        elif expr[0] == 'bool':
            return 'bool'
        elif expr[0] == 'char':
            return 'char'
        elif expr[0] == 'var':
            simbolo, error = self.tabla_actual.obtener(expr[1])
            if not error:
                return simbolo.tipo_dato
            return None
        elif expr[0] == 'binop':
            operador = expr[1]
            tipo_izq = self._obtener_tipo_expresion(expr[2])
            tipo_der = self._obtener_tipo_expresion(expr[3])
            
            # Suma: permite numeros y String+String
            if operador == '+':
                if tipo_izq == 'String' and tipo_der == 'String':
                    return 'String'
                if tipo_izq in ['i32', 'f64'] and tipo_der in ['i32', 'f64']:
                    return 'f64' if (tipo_izq == 'f64' or tipo_der == 'f64') else 'i32'
                return None
            
            # Resta, Division, Modulo: solo numeros
            elif operador in ['-', '/', '%']:
                if tipo_izq in ['i32', 'f64'] and tipo_der in ['i32', 'f64']:
                    return 'f64' if (tipo_izq == 'f64' or tipo_der == 'f64') else 'i32'
                return None
            
            # Multiplicacion: numeros o i32 * String (SOLO i32 * String)
            elif operador == '*':
                if tipo_izq in ['i32', 'f64'] and tipo_der in ['i32', 'f64']:
                    return 'f64' if (tipo_izq == 'f64' or tipo_der == 'f64') else 'i32'
                if tipo_izq == 'i32' and tipo_der == 'String':
                    return 'String'
                return None
            
            # Relacionales: todos devuelven bool
            elif operador in ['==', '!=', '>', '<', '>=', '<=']:
                if self._son_tipos_compatibles(tipo_izq, tipo_der):
                    return 'bool'
                return None
            
            # Logicos: solo bool
            elif operador in ['&&', '||']:
                if tipo_izq == 'bool' and tipo_der == 'bool':
                    return 'bool'
                return None
        
        elif expr[0] == 'unop':
            operador = expr[1]
            if operador == '!':
                return 'bool'
            elif operador == '-':
                return self._obtener_tipo_expresion(expr[2])
        elif expr[0] == 'llamada':
            nombre = expr[1]
            if nombre == 'len':
                return 'i32'
            elif nombre in ['println', 'typeof']:
                return None
            elif nombre in ['to_uppercase', 'to_lowercase', 'replace']:
                return 'String'
            elif nombre == 'contains':
                return 'bool'
            elif nombre == 'random':
                return 'i32'
            elif nombre == 'split':
                return 'array'
            elif nombre == 'reverse':
                return 'array'
            else:
                simbolo, error = self.tabla_actual.obtener(nombre)
                if not error:
                    return simbolo.tipo_retorno
        return None

    # VERIFICAR SI LOS TIPOS SON COMPATIBLES
    def _son_tipos_compatibles(self, tipo1, tipo2):
        if tipo1 is None or tipo2 is None:
            return True
        
        # Tipos iguales
        if tipo1 == tipo2:
            return True
        
        # i32 <-> f64
        if (tipo1 == 'f64' and tipo2 == 'i32') or (tipo1 == 'i32' and tipo2 == 'f64'):
            return True
        
        # i32 <-> char
        if (tipo1 == 'i32' and tipo2 == 'char') or (tipo1 == 'char' and tipo2 == 'i32'):
            return True
        
        # char <-> char
        if tipo1 == 'char' and tipo2 == 'char':
            return True
        
        # String <-> String
        if tipo1 == 'String' and tipo2 == 'String':
            return True
        
        # bool <-> bool
        if tipo1 == 'bool' and tipo2 == 'bool':
            return True
        
        return False