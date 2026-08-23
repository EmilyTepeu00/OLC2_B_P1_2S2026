from backend.parser import parsear
from backend.semantic import AnalizadorSemantico

# CODIGO CORRECTO
codigo1 = """
fn main() {
    let x: i32 = 10;
    let mut y = 20;
    let suma = x + y;
    y = 30;
    println!(suma);
}
"""

# ERROR DE TIPOS
codigo2 = """
fn main() {
    let x: i32 = 10;
    let nombre = "Ana";
    let error = x + nombre;
}
"""

# VARIABLE INMUTABLE
codigo3 = """
fn main() {
    let x: i32 = 10;
    x = 20;
}
"""

def probar(codigo, descripcion):
    print(f"\n{'='*50}")
    print(f"PRUEBA: {descripcion}")
    print('='*50)
    
    ast, errores_parseo, errores_lexicos, lineas = parsear(codigo)
    
    if errores_parseo:
        print("Errores de parseo:")
        for e in errores_parseo:
            print(f"  {e['mensaje']}")
        return
    
    analizador = AnalizadorSemantico()
    errores = analizador.analizar(ast, lineas=lineas)
    
    if errores:
        print("Errores semanticos:")
        for e in errores:
            print(f"  {e['mensaje']}")
    else:
        print("Analisis semantico exitoso")

if __name__ == "__main__":
    probar(codigo1, "Codigo correcto")
    probar(codigo2, "Error de tipos (i32 + String)")
    probar(codigo3, "Variable inmutable")