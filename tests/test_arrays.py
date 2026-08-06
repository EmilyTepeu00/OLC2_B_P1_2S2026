from backend.parser import parsear
from backend.semantic import AnalizadorSemantico
from backend.interpreter import Interprete

codigo = """
fn main() {
    let numeros: [i32; 5] = [10, 20, 30, 40, 50];
    let edades = [18, 20, 22];
    let repetidos = [0; 3];
    
    println(numeros[0]);
    println(edades[2]);
    println(repetidos[1]);
    
    // Slice
    let parte = &numeros[1..4];
    println(parte);
}
"""

ast, errores_parseo = parsear(codigo)

if errores_parseo:
    print("Errores de parseo:")
    for e in errores_parseo:
        print(f"  {e['mensaje']}")
else:
    analizador = AnalizadorSemantico()
    errores = analizador.analizar(ast)
    
    if errores:
        print("Errores semanticos:")
        for e in errores:
            print(f"  {e['mensaje']}")
    else:
        interprete = Interprete()
        salida, errores_ejecucion = interprete.ejecutar(ast)
        
        print("=== EJECUCION ===\n")
        if errores_ejecucion:
            print("Errores de ejecucion:")
            for e in errores_ejecucion:
                print(f"  {e}")
        else:
            print("Salida:")
            for linea in salida:
                print(f"  {linea}")