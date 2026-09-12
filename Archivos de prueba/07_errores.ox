// =====================================================================
//  OxigenScript - Archivo de entrada 07
//  Hoja de calificacion, criterio 8.1: Reporte de errores + tabla
//  (0.1 c/u = 1 pt)
//
//  ESTE ARCHIVO ESTA ROTO A PROPOSITO.
//
//  Contiene los tipos de error del enunciado (3.4.1) que permiten que
//  el interprete se recupere y siga ejecutando. Entre error y error hay
//  un println! de control: si esas lineas aparecen en la consola, la
//  resiliencia funciona. Si el interprete se detiene en el primer
//  error, el criterio no se cumple.
//
//  El caso "llave o parentesis sin cerrar" NO esta aqui porque rompe el
//  parseo del archivo completo. Se prueba aparte, borrando la ultima
//  llave del archivo 09 al momento de calificar. Ver README.
//
//  Las lineas y columnas esperadas estan en la tabla del final.
// =====================================================================

// Se declara antes de main para que el error 8 sea de numero de
// argumentos y no de funcion no declarada.
fn suma(a: i32, b: i32) {
    println!("{}", a + b);
}

fn main() {
    println!("inicio");

    // --- Error 1: caracter no reconocido (LEXICO) ---
    let total = @100;
    println!("control 1");

    // --- Error 2: variable no declarada (SEMANTICO) ---
    println!(no_declarada);
    println!("control 2");

    // --- Error 3: tipos incompatibles en la declaracion (SEMANTICO) ---
    let edad: i32 = "veinte";
    println!("control 3");

    // --- Error 4: tipos incompatibles en la operacion (SEMANTICO) ---
    let x: i32 = 10;
    let y = x + "5";
    println!("control 4");

    // --- Error 5: modificacion de variable inmutable (SEMANTICO) ---
    let contador = 10;
    contador = 20;
    println!("control 5");

    // --- Error 6: indice fuera de los limites del arreglo (SEMANTICO) ---
    let numeros = [10, 20, 30];
    println!(numeros[5]);
    println!("control 6");

    // --- Error 7: funcion no declarada (SEMANTICO) ---
    saludar();
    println!("control 7");

    // --- Error 8: numero incorrecto de argumentos (SEMANTICO) ---
    suma(10);
    println!("control 8");

    // --- Error 9: falta punto y coma (SINTACTICO) ---
    // Va de ultimo a proposito: si el parser no se recupera de esto,
    // al menos los ocho errores anteriores ya se reportaron.
    let z = 10
    println!("{}", z);

    println!("fin");
}

/* =====================================================================
   ERRORES ESPERADOS

   El interprete debe reportar los NUEVE errores y ademas llenar la
   tabla de analisis de errores (No / Tipo / Descripcion / Linea /
   Columna) del reporte HTML.

   No  Tipo         Linea  Col  Descripcion
   --  -----------  -----  ---  ---------------------------------------
   1   Lexico         31    17  Caracter no reconocido '@'.
   2   Semantico      35    14  La variable 'no_declarada' no ha sido
                                declarada.
   3   Semantico      39    21  No es posible asignar un valor de tipo
                                String a una variable de tipo i32.
   4   Semantico      44    17  Tipos incompatibles. No es posible
                                utilizar un valor de tipo String donde
                                se esperaba un valor de tipo i32.
   5   Semantico      49     5  No es posible modificar la variable
                                'contador' porque fue declarada como
                                inmutable.
   6   Semantico      54    14  Indice fuera de los limites del arreglo.
   7   Semantico      58     5  La funcion 'saludar' no ha sido
                                declarada.
   8   Semantico      62     5  La funcion 'suma' esperaba 2 argumentos,
                                pero recibio 1.
   9   Sintactico     68    15  Se esperaba ';'.

   Sobre las columnas: el enunciado no es consistente consigo mismo. En
   su ejemplo de "variable no declarada" (println!(total);) reporta la
   columna 9, que es el parentesis, mientras que en el de "variable
   inmutable" reporta la columna del identificador. Las columnas de esta
   tabla apuntan al inicio del token que causa el error. Una diferencia
   de una o dos posiciones no deberia costar puntos; lo que se califica
   es que la linea sea correcta y que el error este bien clasificado.


   SALIDA ESPERADA EN CONSOLA

   Ademas de los errores, deben aparecer TODAS estas lineas de control,
   que demuestran que el interprete se recupera y sigue ejecutando:

   inicio
   control 1
   control 2
   control 3
   control 4
   control 5
   control 6
   control 7
   control 8
   fin

   La linea "fin" solo aparece si el parser tambien se recupero del
   error 9 (falta de punto y coma). Si falta unicamente "fin", los ocho
   errores anteriores igual cuentan.
   ===================================================================== */
