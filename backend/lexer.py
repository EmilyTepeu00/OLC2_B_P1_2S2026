# --- ANALIZADOR LEXICO ---

import ply.lex as lex

# PALABRAS RESERVADAS
reserved = {
    'let': 'LET',
    'mut': 'MUT',
    'fn': 'FN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'loop': 'LOOP',
    'match': 'MATCH',
    'struct': 'STRUCT',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'true': 'TRUE',
    'false': 'FALSE',
    'i32': 'I32',
    'f64': 'F64',
    'bool': 'BOOL',
    'char': 'CHAR',
    'String': 'STRING_TYPE',
    'println': 'PRINTLN',
    'typeof': 'TYPEOF',
    'random': 'RANDOM',
    'len': 'LEN',
    'contains': 'CONTAINS',
    'replace': 'REPLACE',
    'split': 'SPLIT',
    'to_uppercase': 'TO_UPPERCASE',
    'to_lowercase': 'TO_LOWERCASE',
    'reverse': 'REVERSE',
    'main': 'MAIN',
}

# LISTA DE TOKENS
tokens = [
    'ID', 'INTEGER', 'FLOAT', 'STRING', 'CHAR_LITERAL',
    'EQUALS', 'PLUS_EQUALS', 'MINUS_EQUALS', 'MULT_EQUALS', 'DIV_EQUALS',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO',
    'EQUAL_EQUAL', 'NOT_EQUAL', 'GREATER', 'GREATER_EQUAL', 'LESS', 'LESS_EQUAL',
    'AND', 'OR', 'NOT',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'COLON', 'COMMA', 'DOT', 'ARROW', 'RANGE',
] + list(reserved.values())

# TOKENS SIMPLES
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_EQUALS = r'='
t_PLUS_EQUALS = r'\+='
t_MINUS_EQUALS = r'-='
t_MULT_EQUALS = r'\*='
t_DIV_EQUALS = r'/='
t_EQUAL_EQUAL = r'=='
t_NOT_EQUAL = r'!='
t_GREATER = r'>'
t_GREATER_EQUAL = r'>='
t_LESS = r'<'
t_LESS_EQUAL = r'<='
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_ARROW = r'->'
t_RANGE = r'\.\.'

t_ignore = ' \t'

# IDENTIFICADORES Y LITERALES
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t

def t_CHAR_LITERAL(t):
    r"'([^'\\]|\\.)'"
    t.value = t.value[1:-1]
    return t

# Comentarios
def t_COMMENT_LINE(t):
    r'//[^\n]*'
    pass

def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    pass

# CONTADOR DE LINEAS
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# MANEJO DE ERRORES
def t_error(t):
    print(f"[Error Lexico] Linea {t.lineno}, Columna {t.lexpos} Caracter no reconocido: '{t.value[0]}'")
    t.lexer.skip(1)

# CREAR EL LEXER
lexer = lex.lex()

# PRUEBA
if __name__ == "__main__":
    test = """
    fn main() {
        let mut x: i32 = 10;
        let y = 20.5;
        if x > y {
            println!("x es mayor");
        }
    }
    """
    lexer.input(test)
    for tok in lexer:
        print(f"{tok.type:15} | {str(tok.value):15} | Línea {tok.lineno}")