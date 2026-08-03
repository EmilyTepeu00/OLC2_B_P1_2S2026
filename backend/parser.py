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
    """function : FN ID PARENIZQ param_list PARENDER FLECHA type LLAVEIZQ statement_list LLAVEDER
                | FN ID PARENIZQ param_list PARENDER LLAVEIZQ statement_list LLAVEDER
                | FN MAIN PARENIZQ param_list PARENDER LLAVEIZQ statement_list LLAVEDER"""
    if len(p) == 11:
        p[0] = ('function', p[2], p[4], p[7], p[9])
    elif len(p) == 10 and p[2] != 'main':
        p[0] = ('function', p[2], p[4], None, p[7])
    else:
        p[0] = ('function', 'main', p[4], None, p[7])

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
            | STRING_TYPE
            | CHAR
            | ID"""
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
                 | assignment
                 | if_statement
                 | while_statement
                 | loop_statement
                 | match_statement
                 | return_statement
                 | break_statement
                 | continue_statement
                 | expression PUNTOCOMA"""
    p[0] = p[1]

def p_let_declaration(p):
    """let_declaration : LET ID DOSPUNTOS type ASIGN expression PUNTOCOMA
                       | LET ID ASIGN expression PUNTOCOMA
                       | LET MUT ID DOSPUNTOS type ASIGN expression PUNTOCOMA
                       | LET MUT ID ASIGN expression PUNTOCOMA
                       | LET ID DOSPUNTOS type PUNTOCOMA
                       | LET MUT ID DOSPUNTOS type PUNTOCOMA"""
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

def p_assignment(p):
    "assignment : ID ASIGN expression PUNTOCOMA"
    p[0] = ('assign', p[1], p[3])

def p_if_statement(p):
    """if_statement : IF expression LLAVEIZQ statement_list LLAVEDER
                    | IF expression LLAVEIZQ statement_list LLAVEDER ELSE LLAVEIZQ statement_list LLAVEDER
                    | IF expression LLAVEIZQ statement_list LLAVEDER ELSE if_statement"""
    if len(p) == 6:
        p[0] = ('if', p[2], p[4], None)
    elif len(p) == 10:
        p[0] = ('if', p[2], p[5], p[8])
    else:
        p[0] = ('if', p[2], p[5], p[7])

def p_while_statement(p):
    "while_statement : WHILE expression LLAVEIZQ statement_list LLAVEDER"
    p[0] = ('while', p[2], p[4])

def p_loop_statement(p):
    """loop_statement : LOOP LLAVEIZQ statement_list LLAVEDER
                      | ID DOSPUNTOS LOOP LLAVEIZQ statement_list LLAVEDER"""
    if len(p) == 5:
        p[0] = ('loop', None, p[3])
    else:
        p[0] = ('loop', p[1], p[5])

def p_match_statement(p):
    "match_statement : MATCH expression LLAVEIZQ match_cases LLAVEDER"
    p[0] = ('match', p[2], p[4])

def p_match_cases(p):
    """match_cases : match_case
                   | match_cases match_case"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_match_case(p):
    """match_case : INTEGER FLECHA LLAVEIZQ statement_list LLAVEDER COMA
                  | ID FLECHA LLAVEIZQ statement_list LLAVEDER COMA
                  | NO ID FLECHA LLAVEIZQ statement_list LLAVEDER COMA"""
    if len(p) == 7:
        p[0] = ('case', p[1], p[4])
    else:
        p[0] = ('case', 'default', p[5])

def p_return_statement(p):
    """return_statement : RETURN expression PUNTOCOMA
                        | RETURN PUNTOCOMA"""
    if len(p) == 4:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)

def p_break_statement(p):
    """break_statement : BREAK PUNTOCOMA
                       | BREAK ID PUNTOCOMA"""
    if len(p) == 3:
        p[0] = ('break', None)
    else:
        p[0] = ('break', p[2])

def p_continue_statement(p):
    """continue_statement : CONTINUE PUNTOCOMA
                          | CONTINUE ID PUNTOCOMA"""
    if len(p) == 3:
        p[0] = ('continue', None)
    else:
        p[0] = ('continue', p[2])

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
    """expression : NO expression
                  | RESTA expression %prec NO"""
    p[0] = ('unop', p[1], p[2])

def p_expression_literal(p):
    """expression : INTEGER
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

def p_expression_variable(p):
    "expression : ID"
    p[0] = ('var', p[1])

def p_expression_call(p):
    """expression : ID PARENIZQ arg_list PARENDER
                  | PRINTLN PARENIZQ arg_list PARENDER
                  | TYPEOF PARENIZQ arg_list PARENDER
                  | RANDOM PARENIZQ arg_list PARENDER
                  | LEN PARENIZQ arg_list PARENDER
                  | CONTAINS PARENIZQ arg_list PARENDER
                  | REPLACE PARENIZQ arg_list PARENDER
                  | SPLIT PARENIZQ arg_list PARENDER
                  | TO_UPPERCASE PARENIZQ arg_list PARENDER
                  | TO_LOWERCASE PARENIZQ arg_list PARENDER
                  | REVERSE PARENIZQ arg_list PARENDER"""
    p[0] = ('call', p[1], p[3])

def p_arg_list(p):
    """arg_list : 
                | expression
                | arg_list COMA expression"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

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