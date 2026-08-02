from backend.parser import parse_code

code = """
fn main() {
    let x: i32 = 10;
    let y = 20;
    let suma = x + y;
}
"""

ast, errors = parse_code(code)

print("=== PRUEBA DEL PARSER ===\n")

if errors:
    print("Errores:")
    for e in errors:
        print(f"  Linea {e['line']}: {e['message']}")
else:
    print("Parseo exitoso!")
    print(f"AST: {ast}")