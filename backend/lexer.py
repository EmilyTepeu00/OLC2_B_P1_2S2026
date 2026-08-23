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
}

# LISTA DE TOKENS
tokens = [
    'ID', 'INTEGER', 'FLOAT', 'STRING', 'CHAR_LITERAL', 'LABEL',
    'ASIGN', 'MASIGUAL', 'MENOSIGUAL', 'MULTIGUAL', 'DIVIGUAL', 'RESTOIGUAL',
    'SUMA', 'RESTA', 'MULT', 'DIV', 'RESTO',
    'IGUAL', 'DIFERENTE', 'MAYOR', 'MAYORIGUAL', 'MENOR', 'MENORIGUAL',
    'Y', 'O', 'NO',
    'PARENIZQ', 'PARENDER', 'LLAVEIZQ', 'LLAVEDER', 'CORCHIZQ', 'CORCHDER',
    'PUNTOCOMA', 'DOSPUNTOS', 'DOSDOSPUNTOS', 'COMA', 'PUNTO', 'FLECHA', 'FLECHA_GORDA', 'RANGO',
    'AMPERSAND',
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
t_RESTOIGUAL = r'%='
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
t_DOSDOSPUNTOS = r'::'
t_DOSPUNTOS = r':'
t_COMA = r','
t_PUNTO = r'\.'
t_FLECHA = r'->'
t_FLECHA_GORDA = r'=>'
t_RANGO = r'\.\.'
t_AMPERSAND = r'&'

t_ignore = ' \t'

# IDENTIFICADORES Y LITERALES
def t_RAW_STRING_HASH(t):
    r'r\#"(.|\n)*?"\#'
    t.type = 'STRING'
    contenido = t.value[3:-2]
    t.lexer.lineno += contenido.count('\n')
    t.value = contenido
    return t

def t_RAW_STRING(t):
    r'r"[^"\n]*"'
    t.type = 'STRING'
    t.value = t.value[2:-1]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    # Convertir el literal true/false a un booleano real para no que no adivine el parser
    if t.type == 'TRUE':
        t.value = True
    elif t.type == 'FALSE':
        t.value = False
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    contenido = t.value[1:-1]
    mapa_escapes = {'n': '\n', 't': '\t', 'r': '\r', '"': '"', '\\': '\\', '0': '\0'}
    resultado = []
    i = 0
    while i < len(contenido):
        c = contenido[i]
        if c == '\\' and i + 1 < len(contenido):
            resultado.append(mapa_escapes.get(contenido[i + 1], contenido[i + 1]))
            i += 2
        else:
            resultado.append(c)
            i += 1
    t.value = ''.join(resultado)
    t.lexer.lineno += t.value.count('\n')
    return t

def t_LABEL(t):
    r"'[a-zA-Z_][a-zA-Z0-9_]*"
    # Etiqueta de loop estilo Rust: 'outer, 'inner
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
    t.lexer.lineno += t.value.count('\n')
    pass

def t_COMMENT_BLOCK_SIN_CERRAR(t):
    r'/\*(.|\n)*'
    print(f"[Error Lexico] Linea {t.lineno}, Columna {t.lexpos} "
          f"Comentario de bloque sin cerrar (falta '*/').")
    t.lexer.lineno += t.value.count('\n')

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