from backend.parser import parsear
from backend.semantic import AnalizadorSemantico
from backend.interpreter import Interprete

codigo = """
struct Person {
    name: String,
    age: i32
}

fn main() {
    let persona = Person {
        name: "Ana",
        age: 25
    };
    
    println(persona.name);
    println(persona.age);
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