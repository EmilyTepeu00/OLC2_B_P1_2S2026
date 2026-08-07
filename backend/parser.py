# --- ANALIZADOR SINTACTICO ---

import ply.yacc as yacc
from backend.lexer import tokens, lexer

errores_parseo = []

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
               | FN ID PARENIZQ lista_parametros PARENDER LLAVEIZQ lista_sentencias LLAVEDER
               | FN MAIN PARENIZQ lista_parametros PARENDER LLAVEIZQ lista_sentencias LLAVEDER"""
    if len(p) == 11:
        p[0] = ('funcion', p[2], p[4], p[7], p[9])
    elif len(p) == 10 and p[2] != 'main':
        p[0] = ('funcion', p[2], p[4], None, p[7])
    else:
        p[0] = ('funcion', 'main', p[4], None, p[7])

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
    "asignacion : ID ASIGN expresion PUNTOCOMA"
    p[0] = ('asignar', p[1], p[3])

def p_sentencia_if(p):
    """sentencia_if : IF expresion LLAVEIZQ lista_sentencias LLAVEDER
                    | IF expresion LLAVEIZQ lista_sentencias LLAVEDER ELSE LLAVEIZQ lista_sentencias LLAVEDER
                    | IF expresion LLAVEIZQ lista_sentencias LLAVEDER ELSE sentencia_if"""
    if len(p) == 6:
        p[0] = ('if', p[2], p[4], None)
    elif len(p) == 10:
        p[0] = ('if', p[2], p[5], p[8])
    else:
        p[0] = ('if', p[2], p[5], p[7])

def p_sentencia_while(p):
    "sentencia_while : WHILE expresion LLAVEIZQ lista_sentencias LLAVEDER"
    p[0] = ('while', p[2], p[4])

def p_sentencia_loop(p):
    """sentencia_loop : LOOP LLAVEIZQ lista_sentencias LLAVEDER
                      | ID DOSPUNTOS LOOP LLAVEIZQ lista_sentencias LLAVEDER"""
    if len(p) == 5:
        p[0] = ('loop', None, p[3])
    else:
        p[0] = ('loop', p[1], p[5])

def p_sentencia_match(p):
    "sentencia_match : MATCH expresion LLAVEIZQ casos_match LLAVEDER"
    p[0] = ('match', p[2], p[4])

def p_casos_match(p):
    """casos_match : caso_match
                   | casos_match caso_match"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_caso_match(p):
    """caso_match : INTEGER FLECHA LLAVEIZQ lista_sentencias LLAVEDER COMA
                  | ID FLECHA LLAVEIZQ lista_sentencias LLAVEDER COMA
                  | NO ID FLECHA LLAVEIZQ lista_sentencias LLAVEDER COMA"""
    if len(p) == 7 and p[1] != 'NO':
        p[0] = ('caso', p[1], p[4])
    else:
        p[0] = ('caso', 'default', p[5])

def p_sentencia_return(p):
    """sentencia_return : RETURN expresion PUNTOCOMA
                        | RETURN PUNTOCOMA"""
    if len(p) == 4:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)

def p_sentencia_break(p):
    """sentencia_break : BREAK PUNTOCOMA
                       | BREAK ID PUNTOCOMA"""
    if len(p) == 3:
        p[0] = ('break', None)
    else:
        p[0] = ('break', p[2])

def p_sentencia_continue(p):
    """sentencia_continue : CONTINUE PUNTOCOMA
                          | CONTINUE ID PUNTOCOMA"""
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
    if p[1] in [True, False]:
        p[0] = ('bool', p[1])
    elif isinstance(p[1], str):
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
                 | PRINTLN PARENIZQ lista_argumentos PARENDER
                 | TYPEOF PARENIZQ lista_argumentos PARENDER
                 | RANDOM PARENIZQ lista_argumentos PARENDER
                 | LEN PARENIZQ lista_argumentos PARENDER
                 | CONTAINS PARENIZQ lista_argumentos PARENDER
                 | REPLACE PARENIZQ lista_argumentos PARENDER
                 | SPLIT PARENIZQ lista_argumentos PARENDER
                 | TO_UPPERCASE PARENIZQ lista_argumentos PARENDER
                 | TO_LOWERCASE PARENIZQ lista_argumentos PARENDER
                 | REVERSE PARENIZQ lista_argumentos PARENDER"""
    p[0] = ('llamada', p[1], p[3])

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

def p_campos_struct(p):
    """campos_struct : campo_struct
                     | campo_struct COMA campos_struct"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_campo_struct(p):
    """campo_struct : ID DOSPUNTOS tipo"""
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

def p_error(p):
    if p:
        errores_parseo.append({
            'linea': p.lineno,
            'mensaje': f'Token inesperado: {p.value}'
        })

parser = yacc.yacc()

def parsear(codigo):
    global errores_parseo
    errores_parseo = []
    resultado = parser.parse(codigo, lexer=lexer)
    return resultado, errores_parseo