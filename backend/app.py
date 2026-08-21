# API REST CON FLASK

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.parser import parsear
from backend.semantic import AnalizadorSemantico
from backend.interpreter import Interprete
from backend.ast_generator import generar_ast

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

@app.route('/execute', methods=['POST'])
def ejecutar():
    try:
        data = request.get_json()
        
        if not data or 'codigo' not in data:
            return jsonify({
                'error': 'Falta el campo "codigo" en la peticion'
            }), 400
        
        codigo = data['codigo']

        # ANALISIS LEXICO Y SINTACTICO
        ast, errores_parseo = parsear(codigo)
        
        if errores_parseo:
            return jsonify({
                'errores': errores_parseo,
                'salida': [],
                'symbols': [],
                'ast': [],
                'ast_image': '',
                'tiempo': '0.000s'
            }), 200

        # ANALISIS SEMANTICO
        analizador = AnalizadorSemantico()
        errores_semanticos = analizador.analizar(ast)
        
        if errores_semanticos:
            return jsonify({
                'errores': errores_semanticos,
                'salida': [],
                'symbols': [],
                'ast': [],
                'ast_image': '',
                'tiempo': '0.000s'
            }), 200

        # EJECUCION
        interprete = Interprete()
        salida, errores_ejecucion = interprete.ejecutar(ast)
        
        # GENERAR TABLA DE SIMBOLOS
        symbols = []
        counter = 1
        
        def recorrer_tabla(tabla, ambito):
            nonlocal counter
            print(f"DEBUG: Tabla en ambito '{ambito}' tiene {len(tabla.simbolos)} simbolos y {len(tabla.hijos)} hijos")
            for nombre, simbolo in tabla.simbolos.items():
                print(f"DEBUG:   Simbolo: {nombre} - {simbolo.tipo_simbolo}")
                if simbolo.tipo_simbolo == 'variable':
                    valor = str(simbolo.valor) if simbolo.valor is not None else '—'
                    symbols.append({
                        'no': counter,
                        'nombre': nombre,
                        'categoria': 'Variable',
                        'tipo': simbolo.tipo_dato or '—',
                        'ambito': ambito,
                        'linea': '—',
                        'valor': valor
                    })
                    counter += 1
                elif simbolo.tipo_simbolo == 'funcion':
                    symbols.append({
                        'no': counter,
                        'nombre': nombre,
                        'categoria': 'Funcion',
                        'tipo': simbolo.tipo_retorno or '—',
                        'ambito': ambito,
                        'linea': '—',
                        'valor': '—'
                    })
                    counter += 1
            for hijo in tabla.hijos:
                recorrer_tabla(hijo, ambito)
        
        recorrer_tabla(analizador.tabla_global, 'global')
        print(f"DEBUG: Total de simbolos encontrados: {len(symbols)}")
        
        # GENERAR AST
        ast_nodes = []
        
        def recorrer_ast(nodo, depth=0):
            if isinstance(nodo, tuple):
                if nodo[0] == 'programa':
                    ast_nodes.append({'label': 'Programa', 'depth': depth})
                    for item in nodo[1]:
                        recorrer_ast(item, depth + 1)
                elif nodo[0] == 'funcion':
                    nombre = nodo[1] if len(nodo) > 1 else 'anonima'
                    ast_nodes.append({'label': 'Funcion ' + nombre, 'depth': depth})
                    for item in nodo[4] if len(nodo) > 4 else []:
                        recorrer_ast(item, depth + 1)
                elif nodo[0] == 'let':
                    nombre = nodo[1] if len(nodo) > 1 else '?'
                    ast_nodes.append({'label': 'Declaracion ' + nombre, 'depth': depth})
                    if len(nodo) > 3 and nodo[3] is not None:
                        recorrer_ast(nodo[3], depth + 1)
                elif nodo[0] == 'asignar':
                    nombre = nodo[1] if len(nodo) > 1 else '?'
                    ast_nodes.append({'label': 'Asignacion ' + nombre, 'depth': depth})
                elif nodo[0] == 'if':
                    ast_nodes.append({'label': 'If', 'depth': depth})
                elif nodo[0] == 'while':
                    ast_nodes.append({'label': 'While', 'depth': depth})
                elif nodo[0] == 'loop':
                    ast_nodes.append({'label': 'Loop', 'depth': depth})
                elif nodo[0] == 'return':
                    ast_nodes.append({'label': 'Return', 'depth': depth})
                elif nodo[0] == 'llamada':
                    nombre = nodo[1] if len(nodo) > 1 else '?'
                    ast_nodes.append({'label': 'Llamada ' + nombre, 'depth': depth})
                elif nodo[0] == 'binop':
                    operador = nodo[1] if len(nodo) > 1 else '?'
                    ast_nodes.append({'label': 'Operacion ' + operador, 'depth': depth})
                elif nodo[0] == 'unop':
                    operador = nodo[1] if len(nodo) > 1 else '?'
                    ast_nodes.append({'label': 'Operacion unaria ' + operador, 'depth': depth})
                elif nodo[0] == 'literal':
                    ast_nodes.append({'label': 'Literal ' + str(nodo[1]), 'depth': depth})
                elif nodo[0] == 'string':
                    ast_nodes.append({'label': 'String "' + nodo[1] + '"', 'depth': depth})
                elif nodo[0] == 'bool':
                    ast_nodes.append({'label': 'Bool ' + str(nodo[1]), 'depth': depth})
                elif nodo[0] == 'var':
                    ast_nodes.append({'label': 'Variable ' + nodo[1], 'depth': depth})
            elif isinstance(nodo, list):
                for item in nodo:
                    recorrer_ast(item, depth + 1)
        
        recorrer_ast(ast)
        
        ast_image = generar_ast(ast_nodes)

        # RESPUESTA
        return jsonify({
            'errores': errores_ejecucion if errores_ejecucion else [],
            'salida': salida,
            'symbols': symbols,
            'ast': ast_nodes,
            'ast_image': ast_image,
            'tiempo': '0.002s'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)