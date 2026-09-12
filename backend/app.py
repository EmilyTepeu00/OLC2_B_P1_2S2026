# API REST CON FLASK

from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.parser import parsear
from backend.semantic import AnalizadorSemantico
from backend.interpreter import Interprete
from backend.ast_generator import generar_ast

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde el frontend


def formatear_error(error):
    # Convierte un error estructurado al formato de dos lineas
    etiquetas = {'Lexico': 'Léxico', 'Sintactico': 'Sintáctico', 'Semantico': 'Semántico'}
    tipo = etiquetas.get(error.get('tipo'), error.get('tipo', '?'))
    linea = error.get('linea', 0)
    columna = error.get('columna')
    encabezado = f"[Error {tipo}] Línea {linea}" + (f", Columna {columna}" if columna else "")
    return f"{encabezado}\n{error.get('mensaje', '')}"


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
        ast, errores_sintacticos, errores_lexicos, lineas, columnas = parsear(codigo)

        errores_totales = list(errores_lexicos) + list(errores_sintacticos)

        salida = []
        symbols = []
        ast_nodes = []
        ast_image = ''

        # Si no se pudo construir el AST, no se sigue con el semantico y se reportan errores
        if ast is not None:
            # ANALISIS SEMANTICO (sigue corriendo aunque haya habido siempre que exista el AST
            analizador = AnalizadorSemantico()
            errores_semanticos = analizador.analizar(ast, lineas=lineas, columnas=columnas)
            errores_totales += errores_semanticos

            # EJECUCION (siempre que haya AST)
            lineas_con_error_semantico = {
                e['linea'] for e in errores_semanticos
                if e.get('linea')
                and 'no permitido entre' not in str(e.get('mensaje', ''))
                and not str(e.get('mensaje', '')).startswith('Tipos incompatibles')
            }
            interprete = Interprete()
            salida, errores_ejecucion = interprete.ejecutar(
                ast, lineas=lineas, lineas_con_error_semantico=lineas_con_error_semantico
            )
            errores_totales += errores_ejecucion

            # TABLA DE SIMBOLOS
            symbols = generar_tabla_simbolos(analizador)

            # AST (nodos aplanados + imagen con Graphviz)
            ast_nodes = generar_nodos_ast(ast)
            ast_image = generar_ast(ast_nodes)

        # Cada error trae un campo 'formato' con el texto de dos lineas
        for e in errores_totales:
            e['formato'] = formatear_error(e)

        return jsonify({
            'errores': errores_totales,
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


def _formatear_valor_ast(nodo):
    # Convierte el nodo AST de la expresion a un texto legible (como RUST) para la columna valor
    if nodo is None:
        return '—'
    if not isinstance(nodo, tuple):
        return str(nodo)
    tipo = nodo[0]
    if tipo == 'literal':
        return str(nodo[1])
    if tipo == 'string':
        return f'"{nodo[1]}"'
    if tipo == 'bool':
        return 'true' if nodo[1] else 'false'
    if tipo == 'char':
        return f"'{nodo[1]}'"
    if tipo == 'string_from':
        return _formatear_valor_ast(nodo[1])
    if tipo == 'array_literal':
        return '[' + ', '.join(_formatear_valor_ast(e) for e in nodo[1]) + ']'
    if tipo == 'array_repeat':
        return f'[{_formatear_valor_ast(nodo[1])}; {nodo[2]}]'
    if tipo == 'struct_init':
        campos = ', '.join(f'{c}: {_formatear_valor_ast(v)}' for c, v in nodo[2])
        return f'{nodo[1]} {{ {campos} }}'
    if tipo == 'var':
        return nodo[1]
    if tipo == 'binop':
        return f'{_formatear_valor_ast(nodo[2])} {nodo[1]} {_formatear_valor_ast(nodo[3])}'
    if tipo == 'unop':
        return f'{nodo[1]}{_formatear_valor_ast(nodo[2])}'
    if tipo == 'llamada':
        args = ', '.join(_formatear_valor_ast(a) for a in nodo[2])
        return f'{nodo[1]}({args})'
    if tipo == 'array_access':
        return f'{_formatear_valor_ast(nodo[1])}[{_formatear_valor_ast(nodo[2])}]'
    if tipo == 'array_slice':
        return f'&{_formatear_valor_ast(nodo[1])}[{_formatear_valor_ast(nodo[2])}..{_formatear_valor_ast(nodo[3])}]'
    if tipo == 'field_access':
        return f'{_formatear_valor_ast(nodo[1])}.{nodo[2]}'
    return str(nodo)


def generar_tabla_simbolos(analizador):
    # Recorre la tabla de simbolos del analizador semantico y agrega los stucts declarados
    symbols = []
    counter = 1

    def recorrer_tabla(tabla, ambito):
        nonlocal counter
        ambito = tabla.nombre_ambito  # el ambito real de esta tabla (global o el nombre de la funcion)
        # Se recorre el historial y no tabla.simbolos
        for simbolo in tabla.historial:
            nombre = simbolo.nombre
            if simbolo.tipo_simbolo == 'variable':
                valor = _formatear_valor_ast(simbolo.valor)
                symbols.append({
                    'no': counter,
                    'nombre': nombre,
                    'categoria': 'Variable',
                    'tipo': simbolo.tipo_dato or '—',
                    'ambito': ambito,
                    'linea': simbolo.linea if simbolo.linea else '—',
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
                    'linea': simbolo.linea if simbolo.linea else '—',
                    'valor': '—'
                })
                counter += 1
        for hijo in tabla.hijos:
            recorrer_tabla(hijo, hijo.nombre_ambito)

    recorrer_tabla(analizador.tabla_global, 'global')

    # Structs: se guardan aparte (analizador.structs: con nombre {campo: tipo})
    for nombre, campos in analizador.structs.items():
        campos_txt = ', '.join(f"{c}: {t}" for c, t in campos.items())
        symbols.append({
            'no': counter,
            'nombre': nombre,
            'categoria': 'Struct',
            'tipo': campos_txt or '—',
            'ambito': 'global',
            'linea': '—',
            'valor': '—'
        })
        counter += 1

    return symbols


def generar_nodos_ast(ast):
    # Aplana el AST a una lista que se usa para generar el ast [{'label', 'depth'}, ...]
    ast_nodes = []

    def recorrer(nodo, depth=0):
        if isinstance(nodo, tuple):
            tipo = nodo[0]
            if tipo == 'programa':
                ast_nodes.append({'label': 'Programa', 'depth': depth})
                for item in nodo[1]:
                    recorrer(item, depth + 1)
            elif tipo == 'funcion':
                nombre = nodo[1] if len(nodo) > 1 else 'anonima'
                ast_nodes.append({'label': 'Funcion ' + nombre, 'depth': depth})
                for item in nodo[4] if len(nodo) > 4 else []:
                    recorrer(item, depth + 1)
            elif tipo == 'struct':
                nombre = nodo[1] if len(nodo) > 1 else '?'
                ast_nodes.append({'label': 'Struct ' + nombre, 'depth': depth})
                for campo, tipo_campo in (nodo[2] if len(nodo) > 2 else []):
                    ast_nodes.append({'label': f'Campo {campo}: {tipo_campo}', 'depth': depth + 1})
            elif tipo == 'let':
                nombre = nodo[1] if len(nodo) > 1 else '?'
                ast_nodes.append({'label': 'Declaracion ' + nombre, 'depth': depth})
                if len(nodo) > 3 and nodo[3] is not None:
                    recorrer(nodo[3], depth + 1)
            elif tipo == 'asignar':
                nombre = nodo[1] if len(nodo) > 1 else '?'
                ast_nodes.append({'label': 'Asignacion ' + nombre, 'depth': depth})
                if len(nodo) > 2:
                    recorrer(nodo[2], depth + 1)
            elif tipo == 'asignar_indice':
                ast_nodes.append({'label': 'Asignacion a indice', 'depth': depth})
                recorrer(nodo[1], depth + 1)
                recorrer(nodo[2], depth + 1)
                recorrer(nodo[3], depth + 1)
            elif tipo == 'asignar_campo':
                ast_nodes.append({'label': 'Asignacion a campo .' + str(nodo[2]), 'depth': depth})
                recorrer(nodo[1], depth + 1)
                recorrer(nodo[3], depth + 1)
            elif tipo == 'if':
                ast_nodes.append({'label': 'If', 'depth': depth})
                recorrer(nodo[1], depth + 1)
                for item in nodo[2]:
                    recorrer(item, depth + 1)
                if len(nodo) > 3 and nodo[3]:
                    cuerpo_sino = nodo[3]
                    if isinstance(cuerpo_sino, list):
                        for item in cuerpo_sino:
                            recorrer(item, depth + 1)
                    else:
                        recorrer(cuerpo_sino, depth + 1)
            elif tipo == 'while':
                ast_nodes.append({'label': 'While', 'depth': depth})
                recorrer(nodo[1], depth + 1)
                for item in nodo[2]:
                    recorrer(item, depth + 1)
            elif tipo == 'loop':
                etiqueta = f" {nodo[1]}" if len(nodo) > 1 and nodo[1] else ''
                ast_nodes.append({'label': 'Loop' + etiqueta, 'depth': depth})
                for item in nodo[2]:
                    recorrer(item, depth + 1)
            elif tipo == 'bloque':
                ast_nodes.append({'label': 'Bloque', 'depth': depth})
                for item in nodo[1]:
                    recorrer(item, depth + 1)
            elif tipo == 'match':
                ast_nodes.append({'label': 'Match', 'depth': depth})
                recorrer(nodo[1], depth + 1)
                for caso in nodo[2]:
                    patron = caso[1]
                    ast_nodes.append({'label': f'Caso {patron}', 'depth': depth + 1})
                    for item in caso[2]:
                        recorrer(item, depth + 2)
            elif tipo == 'return':
                ast_nodes.append({'label': 'Return', 'depth': depth})
                if len(nodo) > 1 and nodo[1] is not None:
                    recorrer(nodo[1], depth + 1)
            elif tipo == 'break':
                etiqueta = f" {nodo[1]}" if len(nodo) > 1 and nodo[1] else ''
                ast_nodes.append({'label': 'Break' + etiqueta, 'depth': depth})
            elif tipo == 'continue':
                etiqueta = f" {nodo[1]}" if len(nodo) > 1 and nodo[1] else ''
                ast_nodes.append({'label': 'Continue' + etiqueta, 'depth': depth})
            elif tipo == 'error_stmt':
                ast_nodes.append({'label': 'Sentencia con error', 'depth': depth})
            elif tipo == 'llamada':
                nombre = nodo[1] if len(nodo) > 1 else '?'
                ast_nodes.append({'label': 'Llamada ' + nombre, 'depth': depth})
                for arg in (nodo[2] if len(nodo) > 2 else []):
                    recorrer(arg, depth + 1)
            elif tipo == 'binop':
                operador = nodo[1] if len(nodo) > 1 else '?'
                ast_nodes.append({'label': 'Operacion ' + operador, 'depth': depth})
                if len(nodo) > 3:
                    recorrer(nodo[2], depth + 1)
                    recorrer(nodo[3], depth + 1)
            elif tipo == 'unop':
                operador = nodo[1] if len(nodo) > 1 else '?'
                ast_nodes.append({'label': 'Operacion unaria ' + operador, 'depth': depth})
                if len(nodo) > 2:
                    recorrer(nodo[2], depth + 1)
            elif tipo == 'literal':
                ast_nodes.append({'label': 'Literal ' + str(nodo[1]), 'depth': depth})
            elif tipo == 'string':
                ast_nodes.append({'label': 'String "' + str(nodo[1]) + '"', 'depth': depth})
            elif tipo == 'string_from':
                ast_nodes.append({'label': 'String::from', 'depth': depth})
                recorrer(nodo[1], depth + 1)
            elif tipo == 'bool':
                ast_nodes.append({'label': 'Bool ' + str(nodo[1]), 'depth': depth})
            elif tipo == 'char':
                ast_nodes.append({'label': 'Char ' + str(nodo[1]), 'depth': depth})
            elif tipo == 'var':
                ast_nodes.append({'label': 'Variable ' + str(nodo[1]), 'depth': depth})
            elif tipo == 'array_literal':
                ast_nodes.append({'label': 'Arreglo literal', 'depth': depth})
                for elem in nodo[1]:
                    recorrer(elem, depth + 1)
            elif tipo == 'array_repeat':
                ast_nodes.append({'label': f'Arreglo repetido x{nodo[2]}', 'depth': depth})
                recorrer(nodo[1], depth + 1)
            elif tipo == 'array_access':
                ast_nodes.append({'label': 'Acceso a arreglo', 'depth': depth})
                recorrer(nodo[1], depth + 1)
                recorrer(nodo[2], depth + 1)
            elif tipo == 'array_slice':
                ast_nodes.append({'label': 'Slice de arreglo', 'depth': depth})
                recorrer(nodo[1], depth + 1)
                recorrer(nodo[2], depth + 1)
                recorrer(nodo[3], depth + 1)
            elif tipo == 'struct_init':
                nombre = nodo[1] if len(nodo) > 1 else '?'
                ast_nodes.append({'label': 'Instancia de ' + nombre, 'depth': depth})
                for campo, val in nodo[2]:
                    ast_nodes.append({'label': 'Campo ' + campo, 'depth': depth + 1})
                    recorrer(val, depth + 2)
            elif tipo == 'field_access':
                ast_nodes.append({'label': 'Acceso a campo .' + str(nodo[2]), 'depth': depth})
                recorrer(nodo[1], depth + 1)
        elif isinstance(nodo, list):
            for item in nodo:
                recorrer(item, depth + 1)

    recorrer(ast)
    return ast_nodes


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)