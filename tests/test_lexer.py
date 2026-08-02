from backend.lexer import lexer

code = """
fn main() {
    let mut x: i32 = 10;
    let y = 20.5;
    let nombre = String::from("Ana");
    if x > y {
        println!("x es mayor");
    }
}
"""

lexer.input(code)
print("=== TOKENS GENERADOS ===\n")
for tok in lexer:
    print(f"{tok.type:15} | {str(tok.value):15} | Línea {tok.lineno}")