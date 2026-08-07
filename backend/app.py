# API REST CON FLASK

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.parser import parsear
from backend.semantic import AnalizadorSemantico
from backend.interpreter import Interprete

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend

@app.route('/')
def index():
    return jsonify({
        'mensaje': 'API funcionando',
        'endpoints': {
            '/execute': 'POST - Ejecutar codigo OxigenScript'
        }
    })

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
                'tipo': 'error',
                'errores': errores_parseo
            }), 400
        
        # ANALISIS SEMANTICO
        analizador = AnalizadorSemantico()
        errores_semanticos = analizador.analizar(ast)
        
        if errores_semanticos:
            return jsonify({
                'tipo': 'error',
                'errores': errores_semanticos
            }), 400
        
        # EJECUCION
        interprete = Interprete()
        salida, errores_ejecucion = interprete.ejecutar(ast)
        
        # RESPUESTA
        return jsonify({
            'tipo': 'exito',
            'salida': salida,
            'errores': errores_ejecucion if errores_ejecucion else []
        })
        
    except Exception as e:
        return jsonify({
            'tipo': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)