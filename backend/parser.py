# --- ANALIZADOR SINTACTICO ---

import ply.yacc as yacc
from backend.lexer import tokens, lexer

parse_errors = []

start = 'program'

precedence = (
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULT', 'DIV', 'RESTO'),
    ('right', 'NO'),
)

def p_program(p):
    "program : function_list"
    p[0] = ('program', p[1])

def p_function_list(p):
    """function_list : function
                     | function_list function"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_function(p):
    """function : FN ID PARENIZQ param_list PARENDER LLAVEIZQ statement_list LLAVEDER
                | FN MAIN PARENIZQ param_list PARENDER LLAVEIZQ statement_list LLAVEDER"""
    if len(p) == 9:
        name = p[2] if p[2] != 'main' else 'main'
        p[0] = ('function', name, p[4], p[7])

def p_param_list(p):
    """param_list : 
                  | param
                  | param_list COMA param"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_param(p):
    "param : ID DOSPUNTOS type"
    p[0] = (p[1], p[3])

def p_type(p):
    """type : I32
            | F64
            | BOOL
            | STRING_TYPE"""
    p[0] = p[1]

def p_statement_list(p):
    """statement_list : 
                      | statement
                      | statement_list statement"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    """statement : let_declaration
                 | expression PUNTOCOMA"""
    p[0] = p[1]

def p_let_declaration(p):
    """let_declaration : LET ID DOSPUNTOS type ASIGN expression PUNTOCOMA
                       | LET ID ASIGN expression PUNTOCOMA"""
    if len(p) == 8:
        p[0] = ('let', p[2], p[4], p[6], False)
    else:
        p[0] = ('let', p[2], None, p[4], False)

def p_expression_binary(p):
    """expression : expression SUMA expression
                  | expression RESTA expression
                  | expression MULT expression
                  | expression DIV expression
                  | expression RESTO expression
                  | expression IGUAL expression
                  | expression DIFERENTE expression
                  | expression MAYOR expression
                  | expression MAYORIGUAL expression
                  | expression MENOR expression
                  | expression MENORIGUAL expression
                  | expression Y expression
                  | expression O expression"""
    p[0] = ('binop', p[2], p[1], p[3])

def p_expression_unary(p):
    """expression : NO expression"""
    p[0] = ('unop', p[1], p[2])

def p_expression_literal(p):
    """expression : INTEGER
                  | FLOAT
                  | STRING"""
    p[0] = ('literal', p[1])

def p_expression_variable(p):
    "expression : ID"
    p[0] = ('var', p[1])

def p_expression_group(p):
    "expression : PARENIZQ expression PARENDER"
    p[0] = p[2]

def p_error(p):
    if p:
        parse_errors.append({
            'line': p.lineno,
            'message': f'Token inesperado: {p.value}'
        })

parser = yacc.yacc()

def parse_code(code):
    global parse_errors
    parse_errors = []
    result = parser.parse(code, lexer=lexer)
    return result, parse_errors