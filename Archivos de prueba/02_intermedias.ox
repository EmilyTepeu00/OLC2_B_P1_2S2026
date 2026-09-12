// =====================================================================
//  OxigenScript - Archivo de entrada 02
//  Hoja de calificacion, Seccion 2: Funcionalidades Intermedias (18 pts)
//
//  El bloque inicial repite el minimo obligatorio del enunciado (3.5):
//  declaracion de los cinco tipos, una operacion aritmetica, una logica
//  e impresion en consola. Los bloques 2.1 a 2.7 son independientes
//  entre si y se pueden borrar uno por uno.
//
//  SALVAGUARDAS: los ciclos que dependen de break o continue con
//  etiqueta llevan un contador de seguridad con un break normal. Si el
//  interprete no implementa las etiquetas, el programa igual termina e
//  imprime una linea que empieza con "ERROR", en vez de colgarse. En
//  una ejecucion correcta esas lineas NUNCA aparecen.
// =====================================================================

fn main() {

    // ===== Minimo obligatorio (viene de la seccion 1) =====
    let base_i: i32 = 8;
    let base_f: f64 = 2.5;
    let base_b: bool = true;
    let base_c: char = 'K';
    let base_s: String = String::from("OxigenScript");

    println!("{}", base_i + 2);
    println!("{}", base_b && false);
    println!("{}", base_f);
    println!("{}", base_c);
    println!("{}", base_s);
    // Esperado: 10 / false / 2.5 / K / OxigenScript


    // ===== 2.1 If (2) =====
    // La condicion es de tipo bool y NO lleva parentesis.
    let nota: i32 = 75;

    if nota >= 90 {
        println!("excelente");
    } else if nota >= 60 {
        println!("aprobado");
    } else {
        println!("reprobado");
    }

    // if sin else
    if nota != 100 {
        println!("no es perfecto");
    }
    // Esperado: aprobado / no es perfecto


    // ===== 2.2 Match (3) =====
    let dia: i32 = 3;

    match dia {
        1 => println!("lunes"),
        2 => println!("martes"),
        3 => println!("miercoles"),
        _ => println!("otro dia"),
    }

    // Caso que cae en el comodin
    let fuera: i32 = 9;

    match fuera {
        1 => println!("lunes"),
        2 => println!("martes"),
        _ => println!("comodin"),
    }
    // Esperado: miercoles / comodin


    // ===== 2.3 Loop (2) =====
    // Ciclo infinito acotado con break.
    let mut lc: i32 = 0;

    loop {
        lc += 1;
        println!("{}", lc);
        if lc == 3 {
            break;
        }
    }
    // Esperado: 1 / 2 / 3


    // ===== 2.4 Loop + Tag (3) =====
    // Dos loops anidados, cada uno con su etiqueta.
    let mut fila: i32 = 0;

    'externo: loop {
        fila += 1;
        let mut col: i32 = 0;

        'interno: loop {
            col += 1;
            println!("({}, {})", fila, col);

            if col == 2 {
                break 'interno;
            }

            if col > 5 {
                println!("ERROR: break con etiqueta no funciono");
                break;
            }
        }

        if fila == 2 {
            break 'externo;
        }

        if fila > 5 {
            println!("ERROR: break con etiqueta no funciono");
            break;
        }
    }
    // Esperado: (1, 1) / (1, 2) / (2, 1) / (2, 2)


    // ===== 2.5 While (2) =====
    let mut w: i32 = 3;

    while w > 0 {
        println!("{}", w);
        w -= 1;
    }
    println!("fin del while");
    // Esperado: 3 / 2 / 1 / fin del while


    // ===== 2.6 Break (3) =====
    // (a) break simple dentro de un while.
    // El while esta acotado a proposito: si break no funciona, b1 llega
    // a 10 en vez de quedarse en 2, y el programa no se cuelga.
    let mut b1: i32 = 0;

    while b1 < 10 {
        b1 += 1;
        if b1 == 2 {
            break;
        }
    }
    println!("{}", b1);

    // (b) break con etiqueta: sale del loop externo desde el interno
    let mut bi: i32 = 0;

    'salida: loop {
        bi += 1;

        if bi > 5 {
            println!("ERROR: break con etiqueta no funciono");
            break;
        }

        let mut bj: i32 = 0;

        'dentro: loop {
            bj += 1;

            if bj == 2 {
                break 'salida;
            }

            if bj > 5 {
                println!("ERROR: break con etiqueta no funciono");
                break;
            }
        }

        // Esta linea nunca se alcanza en una ejecucion correcta
        println!("ERROR: no debia llegar aqui");
    }
    println!("{}", bi);
    // Esperado: 2 / 1


    // ===== 2.7 Continue (3) =====
    // (a) continue simple: se salta el valor 3
    let mut c1: i32 = 0;

    while c1 < 5 {
        c1 += 1;
        if c1 == 3 {
            continue;
        }
        println!("{}", c1);
    }

    // (b) continue con etiqueta: reinicia el ciclo externo.
    // El ciclo externo termina con un break normal (el break con
    // etiqueta ya se evaluo en 2.6), asi que aqui lo unico que se
    // prueba es el continue con etiqueta.
    let mut ci: i32 = 0;

    'ext: loop {
        ci += 1;

        if ci > 3 {
            break;
        }

        let mut cj: i32 = 0;

        'int: loop {
            cj += 1;

            if cj == 2 {
                continue 'ext;
            }

            if cj > 5 {
                println!("ERROR: continue con etiqueta no funciono");
                break;
            }

            println!("{}-{}", ci, cj);
        }
    }
    // Esperado: 1 / 2 / 4 / 5 / 1-1 / 2-1 / 3-1
}

/* =====================================================================
   SALIDA ESPERADA COMPLETA (en orden)

   10
   false
   2.5
   K
   OxigenScript
   aprobado
   no es perfecto
   miercoles
   comodin
   1
   2
   3
   (1, 1)
   (1, 2)
   (2, 1)
   (2, 2)
   3
   2
   1
   fin del while
   2
   1
   1
   2
   4
   5
   1-1
   2-1
   3-1

   Nota: ninguna linea que empiece con "ERROR" debe aparecer. Si aparece
   alguna, el break o el continue con etiqueta no estan saliendo del
   ciclo correcto, y ademas 2.4, 2.6 o 2.7 no se cumplen.
   ===================================================================== */
