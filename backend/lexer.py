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
    'ASIGN', 'MASIGUAL', 'MENOSIGUAL', 'MULTIGUAL', 'DIVIGUAL',
    'SUMA', 'RESTA', 'MULT', 'DIV', 'RESTO',
    'IGUAL', 'DIFERENTE', 'MAYOR', 'MAYORIGUAL', 'MENOR', 'MENORIGUAL',
    'Y', 'O', 'NO',
    'PARENIZQ', 'PARENDER', 'LLAVEIZQ', 'LLAVEDER', 'CORCHIZQ', 'CORCHDER',
    'PUNTOCOMA', 'DOSPUNTOS', 'COMA', 'PUNTO', 'FLECHA', 'RANGO',
] + list(reserved.values())

# TOKENS SIMPLES
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_RESTO = r'%'
t_ASIGN = r'='
t_MASIGUAL = r'\+='
t_MENOSIGUAL = r'-='
t_MULTIGUAL = r'\*='
t_DIVIGUAL = r'/='
t_IGUAL = r'=='
t_DIFERENTE = r'!='
t_MAYOR = r'>'
t_MAYORIGUAL = r'>='
t_MENOR = r'<'
t_MENORIGUAL = r'<='
t_Y = r'&&'
t_O = r'\|\|'
t_NO = r'!'
t_PARENIZQ = r'\('
t_PARENDER = r'\)'
t_LLAVEIZQ = r'\{'
t_LLAVEDER = r'\}'
t_CORCHIZQ = r'\['
t_CORCHDER = r'\]'
t_PUNTOCOMA = r';'
t_DOSPUNTOS = r':'
t_COMA = r','
t_PUNTO = r'\.'
t_FLECHA = r'->'
t_RANGO = r'\.\.'

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

# COMENTARIOS
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
        print(f"{tok.type:15} | {str(tok.value):15} | Linea {tok.lineno}")