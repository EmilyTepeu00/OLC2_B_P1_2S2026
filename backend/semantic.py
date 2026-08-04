# ---ANALISIS SEMANTICO ---
# TABLA DE SIMBOLOS

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
        tipo_retorno = nodo_funcion[3]
        
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
        tipo_retorno = nodo_funcion[3]
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
    
    def _analizar_let(self, nodo_let):
        nombre = nodo_let[1]
        tipo = nodo_let[2]
        valor = nodo_let[3]
        mutable = nodo_let[4]
        
        # Si no tiene tipo, inferir del valor
        if tipo is None and valor is not None:
            tipo = self._inferir_tipo(valor)
        
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
    
    def _analizar_if(self, nodo_if):
        condicion = nodo_if[1]
        cuerpo_entonces = nodo_if[2]
        cuerpo_sino = nodo_if[3] if len(nodo_if) > 3 else None
        
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
        self._analizar_expresion(izquierda)
        self._analizar_expresion(derecha)
    
    def _analizar_unario(self, nodo_unario):
        operador = nodo_unario[1]
        operando = nodo_unario[2]
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
    
    def _inferir_tipo(self, valor):
        if valor[0] == 'literal':
            return 'i32' if isinstance(valor[1], int) else 'f64'
        elif valor[0] == 'string':
            return 'String'
        elif valor[0] == 'bool':
            return 'bool'
        elif valor[0] == 'var':
            simbolo, error = self.tabla_actual.obtener(valor[1])
            if not error:
                return simbolo.tipo_dato
        return None