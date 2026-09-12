// =====================================================================
//  OxigenScript - Archivo de entrada 05
//  Hoja de calificacion, Seccion 5: Arreglos (16 pts)
//
//  main() va al final: este archivo NO depende del hoisting (eso se
//  evalua aparte, en el archivo 03).
//
//  Nota sobre 5.6: la gramatica del enunciado define
//  <param> ::= <id> : <type>, sin "mut", asi que un parametro no se
//  puede modificar. Por eso sort_array() no recibe el arreglo: lo
//  declara adentro como "let mut" y lo ordena. Ver README.
// =====================================================================

// ---------------------------------------------------------------------
//  5.5  find_max()
// ---------------------------------------------------------------------
fn find_max(datos: [i32; 6]) -> i32 {
    let mut maximo: i32 = datos[0];
    let mut i: i32 = 1;

    while i < datos.len() {
        if datos[i] > maximo {
            maximo = datos[i];
        }
        i += 1;
    }

    return maximo;
}

// ---------------------------------------------------------------------
//  5.6  sort_array()  (ordenamiento burbuja, ascendente)
// ---------------------------------------------------------------------
fn sort_array() {
    let mut datos: [i32; 6] = [45, 12, 89, 7, 56, 23];
    let n: i32 = datos.len();
    let mut i: i32 = 0;

    while i < n - 1 {
        let mut j: i32 = 0;

        while j < n - 1 - i {
            if datos[j] > datos[j + 1] {
                let temporal: i32 = datos[j];
                datos[j] = datos[j + 1];
                datos[j + 1] = temporal;
            }
            j += 1;
        }

        i += 1;
    }

    println!(datos);
}

// ---------------------------------------------------------------------
//  5.7  compare_arrays()
// ---------------------------------------------------------------------
fn compare_arrays(a: [i32; 5], b: [i32; 5]) -> bool {
    if a.len() != b.len() {
        return false;
    }

    let mut i: i32 = 0;

    while i < a.len() {
        if a[i] != b[i] {
            return false;
        }
        i += 1;
    }

    return true;
}


fn main() {

    // ===== Minimo obligatorio (viene de la seccion 1) =====
    let base_i: i32 = 5;
    let base_f: f64 = 4.5;
    let base_b: bool = false;
    let base_c: char = 'A';
    let base_s: String = String::from("Arreglos");

    println!("{}", base_i + 5);
    println!("{}", base_b || true);
    println!("{}", base_f);
    println!("{}", base_c);
    println!("{}", base_s);
    // Esperado: 10 / true / 4.5 / A / Arreglos


    // ===== 5.1 Declaracion inmutable explicita e inferida (0.5 c/u = 1) =====
    let arr_explicito: [i32; 5] = [10, 20, 30, 40, 50];
    let arr_inferido = [18, 20, 22];
    // Tercera forma de la gramatica: [ <exp> ; <num> ]
    let arr_repetido = [7; 4];

    println!(arr_explicito);
    println!(arr_inferido);
    println!(arr_repetido);
    // Esperado: [10, 20, 30, 40, 50] / [18, 20, 22] / [7, 7, 7, 7]


    // ===== 5.2 Declaracion mutable explicita e inferida (0.5 c/u = 1) =====
    let mut marr_explicito: [i32; 3] = [1, 2, 3];
    let mut marr_inferido = [4, 5, 6];

    println!(marr_explicito);
    println!(marr_inferido);
    // Esperado: [1, 2, 3] / [4, 5, 6]


    // ===== 5.3 Asignacion y acceso a elemento (0.5 c/u = 1) =====
    let mut datos: [i32; 4] = [10, 20, 30, 40];

    println!("{}", datos[0]);
    println!("{}", datos[3]);

    datos[1] = 99;

    println!("{}", datos[1]);
    println!(datos);
    // Esperado: 10 / 40 / 99 / [10, 99, 30, 40]


    // ===== 5.4 Declaracion de slices (1) =====
    // El indice inicial se incluye y el final no: [1..4] son las
    // posiciones 1, 2 y 3. El arreglo original no se modifica.
    let numeros: [i32; 5] = [10, 20, 30, 40, 50];
    let parte = &numeros[1..4];

    println!(parte);
    println!(numeros);
    // Esperado: [20, 30, 40] / [10, 20, 30, 40, 50]


    // ===== 5.5 find_max() (3) =====
    let fm_positivos: [i32; 6] = [12, 45, 7, 89, 23, 56];
    let fm_negativos: [i32; 6] = [-5, -20, -3, -40, -1, -9];

    println!("{}", find_max(fm_positivos));
    println!("{}", find_max(fm_negativos));
    // Esperado: 89 / -1


    // ===== 5.6 sort_array() (4) =====
    sort_array();
    // Esperado: [7, 12, 23, 45, 56, 89]


    // ===== 5.7 compare_arrays() (5) =====
    let ca_uno: [i32; 5] = [1, 2, 3, 4, 5];
    let ca_igual: [i32; 5] = [1, 2, 3, 4, 5];
    let ca_distinto: [i32; 5] = [1, 2, 9, 4, 5];

    println!("{}", compare_arrays(ca_uno, ca_igual));
    println!("{}", compare_arrays(ca_uno, ca_distinto));
    // Esperado: true / false
}

/* =====================================================================
   SALIDA ESPERADA COMPLETA (en orden)

   10
   true
   4.5
   A
   Arreglos
   [10, 20, 30, 40, 50]
   [18, 20, 22]
   [7, 7, 7, 7]
   [1, 2, 3]
   [4, 5, 6]
   10
   40
   99
   [10, 99, 30, 40]
   [20, 30, 40]
   [10, 20, 30, 40, 50]
   89
   -1
   [7, 12, 23, 45, 56, 89]
   true
   false

   Nota: el unico ejemplo de slice del enunciado lo imprime con
   println!("\nSlice: {:?}", parte), usando el marcador {:?}, que no
   aparece documentado en ningun otro lado. Aqui se usa println!(parte),
   que es la forma que el propio enunciado emplea para arreglos en
   3.3.14. Ver README, ambiguedad #20.
   ===================================================================== */
