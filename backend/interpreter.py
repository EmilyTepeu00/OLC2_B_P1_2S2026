# INTERPRETE

class Entorno:
    def __init__(self, padre=None):
        self.variables = {}
        self.padre = padre
        self.etiquetas = {}  # Para loops con etiquetas
    
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

class Interprete:
    def __init__(self):
        self.entorno_global = Entorno()
        self.entorno_actual = self.entorno_global
        self.funciones = {}
        self.salida = []
        self.errores = []
    
    def ejecutar(self, ast):
        self.salida = []
        self.errores = []
        programa = ast
        
        # Registrar todas las funciones
        for funcion in programa[1]:
            if funcion[0] == 'funcion':
                self.funciones[funcion[1]] = funcion
        
        # Buscar y ejecutar main
        if 'main' not in self.funciones:
            self.errores.append("Error: No se encontró la funcion main")
            return
        
        try:
            self._ejecutar_funcion('main', [])
        except Exception as e:
            self.errores.append(str(e))
        
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
        resultado = None
        for sentencia in cuerpo:
            resultado = self._ejecutar_sentencia(sentencia)
            if resultado is not None and resultado.get('tipo') == 'return':
                # Restaurar entorno y retornar valor
                self.entorno_actual = entorno_anterior
                return resultado['valor']
        
        # Restaurar entorno
        self.entorno_actual = entorno_anterior
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
        elif tipo == 'break':
            return {'tipo': 'break'}
        elif tipo == 'continue':
            return {'tipo': 'continue'}
        elif tipo == 'llamada':
            self._ejecutar_llamada(sentencia)
        elif tipo == 'binop':
            return self._ejecutar_binop(sentencia)
        elif tipo == 'unop':
            return self._ejecutar_unop(sentencia)
        elif tipo == 'literal':
            return sentencia[1]
        elif tipo == 'string':
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
            
            for sentencia in cuerpo_entonces:
                resultado = self._ejecutar_sentencia(sentencia)
                if resultado is not None:
                    if resultado.get('tipo') == 'return':
                        self.entorno_actual = entorno_anterior
                        return resultado
                    elif resultado.get('tipo') in ['break', 'continue']:
                        self.entorno_actual = entorno_anterior
                        return resultado
            
            self.entorno_actual = entorno_anterior
        elif cuerpo_sino:
            entorno_anterior = self.entorno_actual
            self.entorno_actual = Entorno(self.entorno_actual)
            
            if isinstance(cuerpo_sino, list):
                for sentencia in cuerpo_sino:
                    resultado = self._ejecutar_sentencia(sentencia)
                    if resultado is not None:
                        if resultado.get('tipo') == 'return':
                            self.entorno_actual = entorno_anterior
                            return resultado
                        elif resultado.get('tipo') in ['break', 'continue']:
                            self.entorno_actual = entorno_anterior
                            return resultado
            else:
                resultado = self._ejecutar_sentencia(cuerpo_sino)
                if resultado is not None:
                    if resultado.get('tipo') == 'return':
                        self.entorno_actual = entorno_anterior
                        return resultado
                    elif resultado.get('tipo') in ['break', 'continue']:
                        self.entorno_actual = entorno_anterior
                        return resultado
            
            self.entorno_actual = entorno_anterior
        
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
            
            for sentencia in cuerpo:
                resultado = self._ejecutar_sentencia(sentencia)
                if resultado is not None:
                    if resultado.get('tipo') == 'return':
                        self.entorno_actual = entorno_anterior
                        return resultado
                    elif resultado.get('tipo') == 'break':
                        self.entorno_actual = entorno_anterior
                        return None
                    elif resultado.get('tipo') == 'continue':
                        self.entorno_actual = entorno_anterior
                        break
            
            self.entorno_actual = entorno_anterior
        
        return None
    
    def _ejecutar_loop(self, nodo):
        etiqueta = nodo[1]
        cuerpo = nodo[2]
        
        while True:
            entorno_anterior = self.entorno_actual
            self.entorno_actual = Entorno(self.entorno_actual)
            
            for sentencia in cuerpo:
                resultado = self._ejecutar_sentencia(sentencia)
                if resultado is not None:
                    if resultado.get('tipo') == 'return':
                        self.entorno_actual = entorno_anterior
                        return resultado
                    elif resultado.get('tipo') == 'break':
                        self.entorno_actual = entorno_anterior
                        return None
                    elif resultado.get('tipo') == 'continue':
                        self.entorno_actual = entorno_anterior
                        break
            
            self.entorno_actual = entorno_anterior
    
    def _ejecutar_return(self, nodo):
        valor = nodo[1]
        if valor is not None:
            valor_ejecutado = self._ejecutar_expresion(valor)
            return {'tipo': 'return', 'valor': valor_ejecutado}
        return {'tipo': 'return', 'valor': None}
    
    def _ejecutar_llamada(self, nodo):
        nombre = nodo[1]
        argumentos = [self._ejecutar_expresion(arg) for arg in nodo[2]]
        
        # Funciones embebidas
        if nombre == 'println':
            texto = ' '.join(str(arg) for arg in argumentos)
            self.salida.append(texto)
            return None
        elif nombre == 'typeof':
            if argumentos:
                return type(argumentos[0]).__name__
            return 'null'
        elif nombre == 'len':
            if argumentos and isinstance(argumentos[0], (str, list)):
                return len(argumentos[0])
            return 0
        elif nombre == 'random':
            import random
            if len(argumentos) >= 2:
                return random.randint(argumentos[0], argumentos[1])
            return random.randint(0, 100)
        
        # Funciones definidas por el usuario
        return self._ejecutar_funcion(nombre, argumentos)
    
    def _ejecutar_binop(self, nodo):
        operador = nodo[1]
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
            return izquierda / derecha
        elif operador == '%':
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
        elif operador == '&&':
            return izquierda and derecha
        elif operador == '||':
            return izquierda or derecha
        
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
        return self._ejecutar_sentencia(expr)