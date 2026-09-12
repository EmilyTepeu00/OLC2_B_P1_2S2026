// =====================================================================
//  OxigenScript - Archivo de entrada 04
//  Hoja de calificacion, Seccion 4: Funciones embebidas (10 pts)
//
//  Las embebidas globales son println!, typeof y random.
//  len y contains aplican a String y a arreglo.
//  replace, split, to_uppercase y to_lowercase aplican a String.
//  reverse aplica a arreglo.
// =====================================================================

fn main() {

    // ===== Minimo obligatorio (viene de la seccion 1) =====
    let base_i: i32 = 4;
    let base_f: f64 = 0.5;
    let base_b: bool = true;
    let base_c: char = 'E';
    let base_s: String = String::from("Embebidas");

    println!("{}", base_i - 1);
    println!("{}", base_b || false);
    println!("{}", base_f);
    println!("{}", base_c);
    println!("{}", base_s);
    // Esperado: 3 / true / 0.5 / E / Embebidas


    // ===== 4.1 println!() (1) =====
    // Las seis formas que aparecen en el enunciado.
    let texto: String = String::from("Hola Mundo");

    println!("Hola Mundo");
    println!(texto);
    println!("Texto: {}", texto);
    println!("{}", texto.len());
    println!("({}, {})", 3, 7);
    println!(typeof(texto));
    // Esperado: Hola Mundo / Hola Mundo / Texto: Hola Mundo / 10
    //           (3, 7) / String


    // ===== 4.2 typeof() (1) =====
    let t_i: i32 = 1;
    let t_f: f64 = 1.0;
    let t_b: bool = true;
    let t_c: char = 'a';
    let t_s: String = String::from("x");

    println!(typeof(t_i));
    println!(typeof(t_f));
    println!(typeof(t_b));
    println!(typeof(t_c));
    println!(typeof(t_s));
    // Esperado: i32 / f64 / bool / char / String


    // ===== 4.3 random() (1) =====
    // random() no es determinista: la primera linea cambia en cada
    // ejecucion. La segunda linea SI es verificable.
    let aleatorio: i32 = random(1, 10);

    println!(aleatorio);
    println!("{}", aleatorio >= 1 && aleatorio <= 10);
    // Esperado: un entero entre 1 y 10 / true


    // ===== 4.4 len() (1) =====
    let l_s: String = String::from("Compiladores");
    let l_a = [10, 20, 30];

    println!("{}", l_s.len());
    println!("{}", l_a.len());
    // Esperado: 12 / 3


    // ===== 4.5 contains() (1) =====
    let c_s: String = String::from("Hola Mundo");
    let c_a = [10, 20, 30];

    println!("{}", c_s.contains("Mundo"));
    println!("{}", c_s.contains("Rust"));
    println!("{}", c_a.contains(20));
    println!("{}", c_a.contains(99));
    // Esperado: true / false / true / false


    // ===== 4.6 replace() (1) =====
    let r_s: String = String::from("Hola Mundo");

    println!("{}", r_s.replace("Mundo", "Rust"));
    // Esperado: Hola Rust


    // ===== 4.7 split() (1) =====
    // Se usa split(separador), que es lo que pide la hoja de
    // calificacion. El ejemplo del enunciado usa split_whitespace() y
    // Vec<&str>, que no estan en la gramatica. Ver README, ambiguedad #6.
    let sp_s: String = String::from("Hola Mundo");

    println!(sp_s.split(" "));
    // Esperado: ["Hola", "Mundo"]


    // ===== 4.8 to_uppercase() (1) =====
    let up_s: String = String::from("Hola Mundo");

    println!(up_s.to_uppercase());
    // Esperado: HOLA MUNDO


    // ===== 4.9 to_lowercase() (1) =====
    let low_s: String = String::from("Hola Mundo");

    println!(low_s.to_lowercase());
    // Esperado: hola mundo


    // ===== 4.10 reverse() (1) =====
    // reverse() invierte el arreglo en el lugar, por eso necesita mut.
    let mut rev_a = [10, 20, 30];

    rev_a.reverse();
    println!(rev_a);
    // Esperado: [30, 20, 10]
}

/* =====================================================================
   SALIDA ESPERADA COMPLETA (en orden)

   3
   true
   0.5
   E
   Embebidas
   Hola Mundo
   Hola Mundo
   Texto: Hola Mundo
   10
   (3, 7)
   String
   i32
   f64
   bool
   char
   String
   <entero aleatorio entre 1 y 10>
   true
   12
   3
   true
   false
   true
   false
   Hola Rust
   ["Hola", "Mundo"]
   HOLA MUNDO
   hola mundo
   [30, 20, 10]

   Notas:
   - La linea marcada como <entero aleatorio> es la unica que cambia
     entre ejecuciones. Lo que se califica es que el valor caiga en el
     rango, cosa que confirma el "true" de la linea siguiente.
   - El formato con el que se imprime un arreglo ("[30, 20, 10]") y un
     arreglo de cadenas ('["Hola", "Mundo"]') es el que muestra el
     enunciado en 3.3.14.
   ===================================================================== */
