from backend.parser import parsear

codigo = """
fn main() {
    let x: i32 = 10;
    let mut y = 20;
    let suma = x + y;
    
    if suma > 10 {
        println!("Mayor que 10");
    } else {
        println!("Menor o igual a 10");
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

ast, errores, errores_lexicos, lineas = parsear(codigo)

print("=== PRUEBA DEL PARSER ===\n")

if errores:
    print("Errores:")
    for e in errores:
        print(f"  Linea {e['linea']}: {e['mensaje']}")
else:
    print("Parseo exitoso")
    print(f"AST: {ast}")