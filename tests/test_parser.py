from backend.parser import parse_code

code = """
fn main() {
    let x: i32 = 10;
    let mut y = 20;
    let suma = x + y;
    
    if suma > 10 {
        println("Mayor que 10");
    } else {
        println("Menor o igual a 10");
    }
    
    while y > 0 {
        y = y - 1;
    }
    
    loop {
        break;
    }
    
    return 0;
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