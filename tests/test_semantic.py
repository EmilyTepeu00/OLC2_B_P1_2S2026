from backend.parser import parsear
from backend.semantic import AnalizadorSemantico

codigo = """
fn main() {
    let x: i32 = 10;
    let mut y = 20;
    let suma = x + y;
    y = 30;
    println(suma);
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
    
    print("=== ANALISIS SEMANTICO ===\n")
    if errores:
        print("Errores semanticos:")
        for e in errores:
            print(f"  {e['mensaje']}")
    else:
        print("Analisis semantico exitoso")
        print("\nTabla de simbolos global:")
        for nombre, simbolo in analizador.tabla_global.simbolos.items():
            print(f"  {nombre}: {simbolo.tipo_simbolo} - {simbolo.tipo_dato}")