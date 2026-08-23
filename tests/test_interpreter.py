from backend.parser import parsear
from backend.semantic import AnalizadorSemantico
from backend.interpreter import Interprete

codigo = """
fn main() {
    let texto = "Hola Mundo desde Rust";
    
    // contains
    let contiene = contains(texto, "Mundo");
    println!(contiene);
    
    // replace
    let nuevo = replace(texto, "Rust", "Compiladores");
    println!(nuevo);
    
    // split
    let partes = split(texto, " ");
    println!(partes);
    
    // to_uppercase
    let mayus = to_uppercase(texto);
    println!(mayus);
    
    // to_lowercase
    let minus = to_lowercase(texto);
    println!(minus);
    
    // reverse (string)
    let invertido = reverse(texto);
    println!(invertido);
}
"""

ast, errores_parseo, errores_lexicos, lineas = parsear(codigo)

if errores_parseo:
    print("Errores de parseo:")
    for e in errores_parseo:
        print(f"  {e['mensaje']}")
else:
    analizador = AnalizadorSemantico()
    errores = analizador.analizar(ast, lineas=lineas)
    
    if errores:
        print("Errores semanticos:")
        for e in errores:
            print(f"  {e['mensaje']}")
    else:
        interprete = Interprete()
        salida, errores_ejecucion = interprete.ejecutar(ast, lineas=lineas)
        
        print("=== EJECUCION ===\n")
        if errores_ejecucion:
            print("Errores de ejecucion:")
            for e in errores_ejecucion:
                print(f"  {e}")
        else:
            print("Salida:")
            for linea in salida:
                print(f"  {linea}")