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
        self.linea = None           # Linea real donde se declaro (para la de tabla de simbolos)

class TablaSimbolos:
    def __init__(self, padre=None):
        self.simbolos = {}
        self.padre = padre
        self.hijos = []
    
    def agregar(self, nombre, simbolo, permitir_sombreado=True):
        # se puede sobreescribir en el mismo ambito, para funciones y structs
        #  se llama con permitir_sombreado=False.
        if nombre in self.simbolos and not permitir_sombreado:
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
        self.lineas = {}       # id(nodo_sentencia) -> numero de linea (viene del parser)
        self.linea_actual = 0  # ultima linea conocida, se actualiza al recorrer sentencias
        self.structs = {}      # nombre_struct -> {nombre_campo: tipo_campo}
    
    def _linea_de(self, nodo):
        # Devuelve la linea real de un nodo si esta registrada o la ultima linea conocida
        if isinstance(nodo, tuple) and id(nodo) in self.lineas:
            self.linea_actual = self.lineas[id(nodo)]
        return self.linea_actual
    
    def analizar(self, ast, lineas=None):
        self.errores = []
        self.lineas = lineas or {}
        self.linea_actual = 0
        self.structs = {}
        programa = ast
        
        # PRIMERA PASADA: registrar todas las funciones y structs
        for funcion in programa[1]:
            if funcion[0] == 'struct':
                self.structs[funcion[1]] = dict(funcion[2])
            else:
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
        simbolo.linea = self._linea_de(nodo_funcion)

        ok, error = self.tabla_global.agregar(nombre, simbolo, permitir_sombreado=False)
        if not ok:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': self._linea_de(nodo_funcion),
                'mensaje': f"Funcion ya declarada: {nombre}"
            })
    
    def _analizar_funcion(self, nodo_funcion):
        nombre = nodo_funcion[1]
        parametros = nodo_funcion[2]
        tipo_retorno = nodo_funcion[3] if len(nodo_funcion) > 3 else None
        cuerpo = nodo_funcion[4] if len(nodo_funcion) > 4 else []
        linea_funcion = self._linea_de(nodo_funcion)

        # Crear ambito para la funcion
        nueva_tabla = TablaSimbolos(self.tabla_global)
        self.tabla_global.hijos.append(nueva_tabla)
        self.tabla_actual = nueva_tabla

        # Registrar parametros como variables
        for nom_param, tipo_param in parametros:
            simbolo = Simbolo(nom_param, 'variable', tipo_param, True)
            simbolo.linea = linea_funcion
            ok, error = self.tabla_actual.agregar(nom_param, simbolo)
            if not ok:
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': linea_funcion,
                    'mensaje': f"Error registrando parametro: {nom_param}"
                })
        
        # Analizar cuerpo
        self.linea_actual = linea_funcion
        for sentencia in cuerpo:
            self._analizar_sentencia(sentencia)
        
        # Volver al ambito anterior
        self.tabla_actual = self.tabla_actual.padre
    
    def _analizar_sentencia(self, sentencia):
        self._linea_de(sentencia)  # actualiza self.linea_actual para los errores de esta sentencia
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
                    'linea': self.linea_actual,
                    'mensaje': f"Tipos incompatibles: no se puede asignar {tipo_valor} a {tipo} en variable {nombre}"
                })
        
        simbolo = Simbolo(nombre, 'variable', tipo, mutable, valor)
        simbolo.linea = self.linea_actual
        ok, error = self.tabla_actual.agregar(nombre, simbolo)
        if not ok:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': self.linea_actual,
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
                'linea': self.linea_actual,
                'mensaje': f"Variable no declarada: {nombre}"
            })
            return
        
        # Verificar que sea mutable
        if not simbolo.mutable:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': self.linea_actual,
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
                    'linea': self.linea_actual,
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
                'linea': self.linea_actual,
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
                'linea': self.linea_actual,
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
            for arg in argumentos:
                self._analizar_expresion(arg)
            return
        
        # Verificar que la funcion exista
        simbolo, error = self.tabla_actual.obtener(nombre)
        if error:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': self.linea_actual,
                'mensaje': f"Funcion no declarada: {nombre}"
            })
            return
        
        # Validar numero de argumentos
        if simbolo.parametros is not None:
            if len(argumentos) != len(simbolo.parametros):
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': self.linea_actual,
                    'mensaje': f"Numero incorrecto de argumentos para {nombre}: esperaba {len(simbolo.parametros)}, recibio {len(argumentos)}"
                })
    
    def _analizar_variable(self, nodo_var):
        nombre = nodo_var[1]
        simbolo, error = self.tabla_actual.obtener(nombre)
        if error:
            self.errores.append({
                'tipo': 'Semantico',
                'linea': self.linea_actual,
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
                        'linea': self.linea_actual,
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
                        'linea': self.linea_actual,
                        'mensaje': f"Operador '*' no permitido entre {tipo_izq} y {tipo_der}"
                    })

            # Resta, Division, Modulo: solo numeros
            elif operador in ['-', '/', '%']:
                if tipo_izq in ['i32', 'f64'] and tipo_der in ['i32', 'f64']:
                    pass
                elif tipo_izq is not None and tipo_der is not None:
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': self.linea_actual,
                        'mensaje': f"Operador '{operador}' no permitido entre {tipo_izq} y {tipo_der}"
                    })
        
        # OPERADORES RELACIONALES: ==, !=, >, <, >=, <=
        elif operador in ['==', '!=', '>', '<', '>=', '<=']:
            if tipo_izq is not None and tipo_der is not None:
                if not self._son_tipos_compatibles(tipo_izq, tipo_der):
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': self.linea_actual,
                        'mensaje': f"Operador '{operador}' no permitido entre {tipo_izq} y {tipo_der}"
                    })
        
        # OPERADORES LOGICOS: &&, ||
        elif operador in ['&&', '||']:
            if tipo_izq is not None and tipo_der is not None:
                if tipo_izq != 'bool' or tipo_der != 'bool':
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': self.linea_actual,
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
                    'linea': self.linea_actual,
                    'mensaje': f"Operador '!' solo funciona con booleanos, pero se encontró {tipo_op}"
                })
        elif operador == '-':
            if tipo_op is not None and tipo_op not in ['i32', 'f64']:
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': self.linea_actual,
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
        elif expr[0] == 'string_from':
            self._analizar_expresion(expr[1])
        elif expr[0] == 'array_literal':
            for elem in expr[1]:
                self._analizar_expresion(elem)
        elif expr[0] == 'array_repeat':
            self._analizar_expresion(expr[1])
        elif expr[0] == 'array_access':
            self._analizar_expresion(expr[1])
            self._analizar_expresion(expr[2])
            tipo_indice = self._obtener_tipo_expresion(expr[2])
            if tipo_indice is not None and tipo_indice != 'i32':
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': self.linea_actual,
                    'mensaje': f"El indice de un arreglo debe ser i32, se recibio {tipo_indice}"
                })
            # Verificar rango solo en tiempo de analisis cuando el indice es un literal y el arreglo es una variable declarada con un arreglo literal
            if expr[2][0] == 'literal' and isinstance(expr[2][1], int) and expr[1][0] == 'var':
                simbolo, error = self.tabla_actual.obtener(expr[1][1])
                if not error and simbolo.valor is not None and simbolo.valor[0] == 'array_literal':
                    tam = len(simbolo.valor[1])
                    if expr[2][1] < 0 or expr[2][1] >= tam:
                        self.errores.append({
                            'tipo': 'Semantico',
                            'linea': self.linea_actual,
                            'mensaje': f"Indice fuera de los limites del arreglo '{expr[1][1]}' (tamano {tam})."
                        })
        elif expr[0] == 'array_slice':
            self._analizar_expresion(expr[1])
            self._analizar_expresion(expr[2])
            self._analizar_expresion(expr[3])
        elif expr[0] == 'struct_init':
            nombre_struct = expr[1]
            campos_dados = expr[2]
            campos_decl = self.structs.get(nombre_struct)
            if campos_decl is None:
                self.errores.append({
                    'tipo': 'Semantico',
                    'linea': self.linea_actual,
                    'mensaje': f"Struct no declarado: {nombre_struct}"
                })
            else:
                nombres_dados = set()
                for campo, val_expr in campos_dados:
                    self._analizar_expresion(val_expr)
                    nombres_dados.add(campo)
                    if campo not in campos_decl:
                        self.errores.append({
                            'tipo': 'Semantico',
                            'linea': self.linea_actual,
                            'mensaje': f"El struct '{nombre_struct}' no tiene el campo '{campo}'"
                        })
                    else:
                        tipo_campo = campos_decl[campo]
                        tipo_val = self._obtener_tipo_expresion(val_expr)
                        if tipo_val is not None and not self._son_tipos_compatibles(tipo_campo, tipo_val):
                            self.errores.append({
                                'tipo': 'Semantico',
                                'linea': self.linea_actual,
                                'mensaje': f"Tipos incompatibles en el campo '{campo}' de '{nombre_struct}': se esperaba {tipo_campo}, se recibio {tipo_val}"
                            })
                faltantes = set(campos_decl.keys()) - nombres_dados
                if faltantes:
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': self.linea_actual,
                        'mensaje': f"Faltan campos al inicializar '{nombre_struct}': {', '.join(sorted(faltantes))}"
                    })
        elif expr[0] == 'field_access':
            self._analizar_expresion(expr[1])
            tipo_base = self._obtener_tipo_expresion(expr[1])
            if tipo_base is not None and tipo_base in self.structs:
                if expr[2] not in self.structs[tipo_base]:
                    self.errores.append({
                        'tipo': 'Semantico',
                        'linea': self.linea_actual,
                        'mensaje': f"El struct '{tipo_base}' no tiene el campo '{expr[2]}'"
                    })

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
        elif expr[0] == 'string_from':
            return 'String'
        elif expr[0] == 'array_literal':
            if expr[1]:
                tipo_elem = self._obtener_tipo_expresion(expr[1][0])
                return f'[{tipo_elem}]' if tipo_elem else None
            return None
        elif expr[0] == 'array_repeat':
            tipo_elem = self._obtener_tipo_expresion(expr[1])
            return f'[{tipo_elem}]' if tipo_elem else None
        elif expr[0] == 'array_access':
            tipo_base = self._obtener_tipo_expresion(expr[1])
            if tipo_base and tipo_base.startswith('[') and tipo_base.endswith(']'):
                return tipo_base[1:-1]
            return None
        elif expr[0] == 'array_slice':
            return self._obtener_tipo_expresion(expr[1])
        elif expr[0] == 'struct_init':
            return expr[1]  # el "tipo" de una instancia es el nombre del struct
        elif expr[0] == 'field_access':
            tipo_base = self._obtener_tipo_expresion(expr[1])
            if tipo_base and tipo_base in self.structs:
                return self.structs[tipo_base].get(expr[2])
            return None
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