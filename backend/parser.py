# --- ANALIZADOR SINTACTICO ---

import ply.yacc as yacc
from backend.lexer import tokens, lexer, escanear_errores_lexicos, encontrar_columna

errores_parseo = []
lineas_nodo = {}

inicio = 'programa'

precedencia = (
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULT', 'DIV', 'RESTO'),
)

def p_programa(p):
    """programa : lista_declaraciones"""
    p[0] = ('programa', p[1])

def p_lista_declaraciones(p):
    """lista_declaraciones : declaracion
                           | lista_declaraciones declaracion"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_declaracion(p):
    """declaracion : funcion
                   | struct_decl"""
    p[0] = p[1]

def p_funcion(p):
    """funcion : FN ID PARENIZQ lista_parametros PARENDER FLECHA tipo LLAVEIZQ lista_sentencias LLAVEDER
               | FN ID PARENIZQ lista_parametros PARENDER LLAVEIZQ lista_sentencias LLAVEDER"""
    if len(p) == 11:
        p[0] = ('funcion', p[2], p[4], p[7], p[9])
    else:
        p[0] = ('funcion', p[2], p[4], None, p[7])
    lineas_nodo[id(p[0])] = p.lineno(1)

def p_lista_parametros(p):
    """lista_parametros : 
                        | parametro
                        | lista_parametros COMA parametro"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_parametro(p):
    "parametro : ID DOSPUNTOS tipo"
    p[0] = (p[1], p[3])

def p_tipo(p):
    """tipo : I32
            | F64
            | BOOL
            | STRING_TYPE
            | CHAR
            | CORCHIZQ tipo PUNTOCOMA INTEGER CORCHDER
            | ID"""
    if len(p) == 6:  # [T; N
        p[0] = ('array', p[2], p[4])
    else:
        p[0] = p[1]

def p_lista_sentencias(p):
    """lista_sentencias : 
                        | sentencia
                        | lista_sentencias sentencia"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_sentencia(p):
    """sentencia : declaracion_let
                 | asignacion
                 | sentencia_if
                 | sentencia_while
                 | sentencia_loop
                 | sentencia_match
                 | sentencia_return
                 | sentencia_break
                 | sentencia_continue
                 | expresion PUNTOCOMA"""
    p[0] = p[1]
    linea = p.lineno(1)
    if linea and isinstance(p[0], tuple):
        lineas_nodo[id(p[0])] = linea

def p_declaracion_let(p):
    """declaracion_let : LET ID DOSPUNTOS tipo ASIGN expresion PUNTOCOMA
                       | LET ID ASIGN expresion PUNTOCOMA
                       | LET MUT ID DOSPUNTOS tipo ASIGN expresion PUNTOCOMA
                       | LET MUT ID ASIGN expresion PUNTOCOMA
                       | LET ID DOSPUNTOS tipo PUNTOCOMA
                       | LET MUT ID DOSPUNTOS tipo PUNTOCOMA"""
    if len(p) == 8 and p[2] != 'mut':
        p[0] = ('let', p[2], p[4], p[6], False)
    elif len(p) == 6 and p[2] != 'mut':
        p[0] = ('let', p[2], None, p[4], False)
    elif len(p) == 9:
        p[0] = ('let', p[3], p[5], p[7], True)
    elif len(p) == 7 and p[2] == 'mut':
        p[0] = ('let', p[3], None, p[5], True)
    elif len(p) == 6 and p[2] != 'mut':
        p[0] = ('let', p[2], p[4], None, False)
    elif len(p) == 7 and p[2] == 'mut':
        p[0] = ('let', p[3], p[5], None, True)

def p_asignacion(p):
    """asignacion : ID ASIGN expresion PUNTOCOMA
                  | ID MASIGUAL expresion PUNTOCOMA
                  | ID MENOSIGUAL expresion PUNTOCOMA
                  | ID MULTIGUAL expresion PUNTOCOMA
                  | ID DIVIGUAL expresion PUNTOCOMA
                  | ID RESTOIGUAL expresion PUNTOCOMA"""
    tipo_token = p.slice[2].type
    if tipo_token == 'ASIGN':
        p[0] = ('asignar', p[1], p[3])
    else:
        # x += e  se traduce a  x = x + e  (igual con -=, *=, /=, %=)
        operador = {
            'MASIGUAL': '+', 'MENOSIGUAL': '-',
            'MULTIGUAL': '*', 'DIVIGUAL': '/', 'RESTOIGUAL': '%',
        }[tipo_token]
        p[0] = ('asignar', p[1], ('binop', operador, ('var', p[1]), p[3]))

def p_sentencia_if(p):
    """sentencia_if : IF expresion LLAVEIZQ lista_sentencias LLAVEDER
                    | IF expresion LLAVEIZQ lista_sentencias LLAVEDER ELSE LLAVEIZQ lista_sentencias LLAVEDER
                    | IF expresion LLAVEIZQ lista_sentencias LLAVEDER ELSE sentencia_if
                    | IF ID LLAVEIZQ lista_sentencias LLAVEDER
                    | IF ID LLAVEIZQ lista_sentencias LLAVEDER ELSE LLAVEIZQ lista_sentencias LLAVEDER
                    | IF ID LLAVEIZQ lista_sentencias LLAVEDER ELSE sentencia_if"""
    condicion = ('var', p[2]) if p.slice[2].type == 'ID' else p[2]
    if len(p) == 6:
        p[0] = ('if', condicion, p[4], None)
    elif len(p) == 10:
        p[0] = ('if', condicion, p[4], p[8])
    else:
        p[0] = ('if', condicion, p[4], p[7])

def p_sentencia_while(p):
    """sentencia_while : WHILE expresion LLAVEIZQ lista_sentencias LLAVEDER
                       | WHILE ID LLAVEIZQ lista_sentencias LLAVEDER"""
    condicion = ('var', p[2]) if p.slice[2].type == 'ID' else p[2]
    p[0] = ('while', condicion, p[4])

def p_sentencia_loop(p):
    """sentencia_loop : LOOP LLAVEIZQ lista_sentencias LLAVEDER
                      | LABEL DOSPUNTOS LOOP LLAVEIZQ lista_sentencias LLAVEDER"""
    if len(p) == 5:
        p[0] = ('loop', None, p[3])
    else:
        p[0] = ('loop', p[1], p[5])

def p_sentencia_match(p):
    """sentencia_match : MATCH expresion LLAVEIZQ casos_match LLAVEDER
                       | MATCH ID LLAVEIZQ casos_match LLAVEDER"""
    condicion = ('var', p[2]) if p.slice[2].type == 'ID' else p[2]
    p[0] = ('match', condicion, p[4])

def p_casos_match(p):
    """casos_match : caso_match
                   | casos_match caso_match"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_caso_match(p):
    """caso_match : INTEGER FLECHA_GORDA expresion COMA
                  | ID FLECHA_GORDA expresion COMA
                  | INTEGER FLECHA_GORDA LLAVEIZQ lista_sentencias LLAVEDER COMA
                  | ID FLECHA_GORDA LLAVEIZQ lista_sentencias LLAVEDER COMA"""
    # Se soporta las dos formas: "patron => expresion"
    patron = p[1]
    cuerpo = [p[3]] if len(p) == 5 else p[4]
    # "_" se tokeniza como ID normal (empieza con "_"), se compara el valor
    if patron == '_':
        p[0] = ('caso', 'default', cuerpo)
    else:
        p[0] = ('caso', patron, cuerpo)

def p_sentencia_return(p):
    """sentencia_return : RETURN expresion PUNTOCOMA
                        | RETURN PUNTOCOMA"""
    if len(p) == 4:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)

def p_sentencia_break(p):
    """sentencia_break : BREAK PUNTOCOMA
                       | BREAK LABEL PUNTOCOMA"""
    if len(p) == 3:
        p[0] = ('break', None)
    else:
        p[0] = ('break', p[2])

def p_sentencia_continue(p):
    """sentencia_continue : CONTINUE PUNTOCOMA
                          | CONTINUE LABEL PUNTOCOMA"""
    if len(p) == 3:
        p[0] = ('continue', None)
    else:
        p[0] = ('continue', p[2])

def p_expresion_binaria(p):
    """expresion : expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULT expresion
                 | expresion DIV expresion
                 | expresion RESTO expresion
                 | expresion IGUAL expresion
                 | expresion DIFERENTE expresion
                 | expresion MAYOR expresion
                 | expresion MAYORIGUAL expresion
                 | expresion MENOR expresion
                 | expresion MENORIGUAL expresion
                 | expresion Y expresion
                 | expresion O expresion"""
    p[0] = ('binop', p[2], p[1], p[3])

def p_expresion_unaria(p):
    """expresion : NO expresion
                 | RESTA expresion"""
    p[0] = ('unop', p[1], p[2])

def p_expresion_literal(p):
    """expresion : INTEGER
                 | FLOAT
                 | STRING
                 | TRUE
                 | FALSE"""
    tipo_token = p.slice[1].type
    if tipo_token in ('TRUE', 'FALSE'):
        p[0] = ('bool', p[1])
    elif tipo_token == 'STRING':
        p[0] = ('string', p[1])
    else:
        p[0] = ('literal', p[1])

def p_expresion_struct_init(p):
    """expresion : ID LLAVEIZQ valores_struct LLAVEDER"""
    p[0] = ('struct_init', p[1], p[3])

def p_expresion_variable(p):
    "expresion : ID"
    p[0] = ('var', p[1])

def p_expresion_llamada(p):
    """expresion : ID PARENIZQ lista_argumentos PARENDER
                 | PRINTLN NO PARENIZQ lista_argumentos PARENDER"""
    if p.slice[1].type == 'PRINTLN':
        p[0] = ('llamada', 'println', p[4])
    else:
        p[0] = ('llamada', p[1], p[3])

def p_expresion_llamada_metodo(p):
    """expresion : expresion PUNTO ID PARENIZQ lista_argumentos PARENDER"""
    # variable.metodo(args) se traduce a llamada(metodo, [variable] + args)
    p[0] = ('llamada', p[3], [p[1]] + p[5])

def p_expresion_string_estatico(p):
    """expresion : STRING_TYPE DOSDOSPUNTOS ID PARENIZQ lista_argumentos PARENDER"""
    # String::from("texto")  y  String::new()
    if p[3] == 'from':
        p[0] = ('string_from', p[5][0] if p[5] else ('string', ''))
    else:  # String::new()
        p[0] = ('string', '')

def p_lista_argumentos(p):
    """lista_argumentos : 
                        | expresion
                        | lista_argumentos COMA expresion"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_expresion_agrupada(p):
    "expresion : PARENIZQ expresion PARENDER"
    p[0] = p[2]

# --- ARREGLOS ---

def p_expresion_array_literal(p):
    """expresion : CORCHIZQ lista_elementos CORCHDER"""
    p[0] = ('array_literal', p[2])

def p_expresion_array_repetido(p):
    """expresion : CORCHIZQ expresion PUNTOCOMA INTEGER CORCHDER"""
    p[0] = ('array_repeat', p[2], p[4])

def p_lista_elementos(p):
    """lista_elementos : 
                      | expresion
                      | lista_elementos COMA expresion"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# --- ARRAYS ---

def p_expresion_array_access(p):
    """expresion : expresion CORCHIZQ expresion CORCHDER"""
    p[0] = ('array_access', p[1], p[3])

def p_expresion_array_slice(p):
    """expresion : AMPERSAND expresion CORCHIZQ expresion RANGO expresion CORCHDER"""
    p[0] = ('array_slice', p[2], p[4], p[6])

# --- STRUCTS ---

def p_struct_decl(p):
    """struct_decl : STRUCT ID LLAVEIZQ campos_struct LLAVEDER"""
    p[0] = ('struct', p[2], p[4])
    lineas_nodo[id(p[0])] = p.lineno(1)

def p_campos_struct(p):
    """campos_struct : campo_struct
                     | campos_struct campo_struct"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_campo_struct(p):
    """campo_struct : ID DOSPUNTOS tipo COMA
                     | ID DOSPUNTOS tipo"""
    # La coma en el ultimo campo es opcional
    p[0] = (p[1], p[3])

def p_valores_struct(p):
    """valores_struct : valor_struct
                      | valores_struct COMA valor_struct"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_valor_struct(p):
    """valor_struct : ID DOSPUNTOS expresion"""
    p[0] = (p[1], p[3])

def p_expresion_field_access(p):
    """expresion : expresion PUNTO ID"""
    p[0] = ('field_access', p[1], p[3])

def p_sentencia_error(p):
    """sentencia : error PUNTOCOMA
                  | error LLAVEDER"""
    # Recuperacion de errores sintacticos si algo en una sentencia no calza con la gramatica
    # YACC descarta tokens hasta el siguiente ';' o '}' y sigue parseando el resto dela rchivo desde ahi en vez de dat errror
    p[0] = ('error_stmt',)

def p_error(p):
    if p:
        columna = encontrar_columna(p.lexer.lexdata, p.lexpos)
        errores_parseo.append({
            'tipo': 'Sintactico',
            'linea': p.lineno,
            'columna': columna,
            'mensaje': f"Token inesperado: '{p.value}'.",
        })
    else:
        errores_parseo.append({
            'tipo': 'Sintactico',
            'linea': 0,
            'columna': 0,
            'mensaje': 'Fin de archivo inesperado.',
        })

parser = yacc.yacc()

def parsear(codigo):
    global errores_parseo, lineas_nodo
    errores_parseo = []
    lineas_nodo = {}
    # Ver que se detecten todos los errores lexicos del archivo
    errores_lex = escanear_errores_lexicos(codigo)
    lexer.lineno = 1
    resultado = parser.parse(codigo, lexer=lexer, tracking=True)
    return resultado, errores_parseo, errores_lex, lineas_nodo