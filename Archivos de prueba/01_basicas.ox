// =====================================================================
//  OxigenScript - Archivo de entrada 01
//  Hoja de calificacion, Seccion 1: Funcionalidades Basicas (17 pts)
//
//  Cada bloque esta rotulado con el numero de criterio de la hoja.
//  Si el estudiante declara que NO implemento un criterio, se borra el
//  bloque completo antes de iniciar la evaluacion: ningun bloque depende
//  de otro.
//
//  La salida esperada completa esta al final del archivo.
// =====================================================================

// Funcion auxiliar usada solo por el criterio 1.13 (cortocircuito).
// Se declara antes de main para que este archivo no dependa del hoisting
// (el hoisting se evalua en el archivo 03).
fn marca(etiqueta: String) -> bool {
    println!("{}", etiqueta);
    return true;
}

fn main() {

    // ===== 1.1 Formato de identificadores (0.1 c/u = 0.6) =====
    // Seis identificadores validos distintos:
    // inicia con letra, inicia con guion bajo, letras + digito,
    // letras + guion bajo + digito, y sensibilidad a mayusculas.
    let edad = 20;
    let Edad = 25;
    let EDAD = 30;
    let _oculto = 1;
    let contador_1 = 2;
    let n2 = 3;

    println!("{}", edad);
    println!("{}", Edad);
    println!("{}", EDAD);
    println!("{}", _oculto);
    println!("{}", contador_1);
    println!("{}", n2);
    // Esperado: 20 / 25 / 30 / 1 / 2 / 3


    // ===== 1.2 Comentarios (0.2 c/u = 0.4) =====
    // 1) Comentario de linea: todo esto se ignora -> let roto = ;
    /*
       2) Comentario de bloque, varias lineas.
          Tambien se ignora codigo aqui adentro: fn ( ) { } ; let
    */
    println!("comentarios ignorados");
    // Esperado: comentarios ignorados


    // ===== 1.3 Declaracion inmutable larga sin inicializar (0.2 por tipo = 1) =====
    // Forma larga = con anotacion explicita de tipo. Usan valor por defecto.
    let vacio_i: i32;
    let vacio_f: f64;
    let vacio_b: bool;
    let vacio_c: char;
    let vacio_s: String;

    println!("{}", vacio_i);
    println!("{}", vacio_f);
    println!("{}", vacio_b);
    println!("{}", vacio_s);
    // vacio_c NO se imprime: el enunciado deja el valor por defecto de
    // char como "-" (sin definir). Ver README, ambiguedad #2.
    // Esperado: 0 / 0.0 / false / (linea vacia)


    // ===== 1.4 Declaracion inmutable larga inicializada (0.2 por tipo = 1) =====
    let larga_i: i32 = 10;
    let larga_f: f64 = 3.14;
    let larga_b: bool = true;
    let larga_c: char = 'A';
    let larga_s: String = String::from("Hola");

    println!("{}", larga_i);
    println!("{}", larga_f);
    println!("{}", larga_b);
    println!("{}", larga_c);
    println!("{}", larga_s);
    // Esperado: 10 / 3.14 / true / A / Hola


    // ===== 1.5 Declaracion inmutable inferida inicializada (0.2 por tipo = 1) =====
    // Sin anotacion de tipo: el interprete lo infiere del valor.
    let inf_i = 7;
    let inf_f = 2.5;
    let inf_b = false;
    let inf_c = 'Z';
    let inf_s = String::from("Mundo");

    println!("{}", inf_i);
    println!("{}", inf_f);
    println!("{}", inf_b);
    println!("{}", inf_c);
    println!("{}", inf_s);
    // Esperado: 7 / 2.5 / false / Z / Mundo


    // ===== 1.6 Declaracion mutable sin inicializar (0.2 por tipo = 1) =====
    let mut mvacio_i: i32;
    let mut mvacio_f: f64;
    let mut mvacio_b: bool;
    let mut mvacio_c: char;
    let mut mvacio_s: String;

    println!("{}", mvacio_i);
    println!("{}", mvacio_f);
    println!("{}", mvacio_b);
    println!("{}", mvacio_s);
    // mvacio_c no se imprime, misma razon que en 1.3.
    // Esperado: 0 / 0.0 / false / (linea vacia)


    // ===== 1.7 Declaracion mutable inicializada (0.2 por tipo = 1) =====
    let mut minit_i: i32 = 100;
    let mut minit_f: f64 = 1.5;
    let mut minit_b: bool = true;
    let mut minit_c: char = 'B';
    let mut minit_s: String = String::from("Rust");

    println!("{}", minit_i);
    println!("{}", minit_f);
    println!("{}", minit_b);
    println!("{}", minit_c);
    println!("{}", minit_s);
    // Esperado: 100 / 1.5 / true / B / Rust


    // ===== 1.8 Asignacion de variables mutables (0.2 por tipo = 1) =====
    let mut asig_i: i32 = 0;
    let mut asig_f: f64 = 0.0;
    let mut asig_b: bool = false;
    let mut asig_c: char = 'X';
    let mut asig_s: String = String::new();

    asig_i = 42;
    asig_f = 9.5;
    asig_b = true;
    asig_c = 'C';
    asig_s = String::from("Compiladores");

    println!("{}", asig_i);
    println!("{}", asig_f);
    println!("{}", asig_b);
    println!("{}", asig_c);
    println!("{}", asig_s);
    // Esperado: 42 / 9.5 / true / C / Compiladores


    // ===== 1.9 Operadores de asignacion (0.25 c/u = 1.5) =====
    // Seis operadores: =  +=  -=  *=  /=  %=
    let mut acc: i32 = 0;

    acc = 5;
    println!("{}", acc);
    acc += 5;
    println!("{}", acc);
    acc -= 3;
    println!("{}", acc);
    acc *= 4;
    println!("{}", acc);
    acc /= 2;
    println!("{}", acc);
    acc %= 5;
    println!("{}", acc);
    // Esperado: 5 / 10 / 7 / 28 / 14 / 4


    // ===== 1.10 Operadores aritmeticos (0.2 c/u = 1) =====
    // Las divisiones son exactas a proposito: el enunciado no define si
    // i32 / i32 trunca o promociona. Ver README, ambiguedad #9.
    let op_a: i32 = 10;
    let op_b: i32 = 4;

    println!("{}", op_a + op_b);
    println!("{}", op_a - op_b);
    println!("{}", op_a * op_b);
    println!("{}", op_a % op_b);
    println!("{}", 20 / 5);
    println!("{}", -op_a);
    println!("{}", op_a + 2.5);
    // Esperado: 14 / 6 / 40 / 2 / 4 / -10 / 12.5
    // (la ultima linea es promocion de tipos: i32 + f64 -> f64)


    // ===== 1.11 Operadores relacionales (0.25 c/u = 1.5) =====
    let rel_a: i32 = 10;
    let rel_b: i32 = 4;

    println!("{}", rel_a == rel_b);
    println!("{}", rel_a != rel_b);
    println!("{}", rel_a > rel_b);
    println!("{}", rel_a >= rel_b);
    println!("{}", rel_a < rel_b);
    println!("{}", rel_a <= rel_b);
    // Esperado: false / true / true / true / false / false


    // ===== 1.12 Operadores logicos (0.5 c/u = 1.5) =====
    let log_t: bool = true;
    let log_f: bool = false;

    println!("{}", !log_t);
    println!("{}", log_t && log_f);
    println!("{}", log_t || log_f);
    // Esperado: false / false / true


    // ===== 1.13 Restriccion de cortocircuito (0.5 c/u = 1.5) =====
    // marca() imprime su argumento y devuelve true. Si se imprime, la
    // funcion SI se evaluo.
    let cc_t: bool = true;
    let cc_f: bool = false;

    // Caso 1: false && f()  -> f() NO se evalua
    let cc1 = cc_f && marca(String::from("ERROR: no debia imprimirse (caso 1)"));

    // Caso 2: true || f()   -> f() NO se evalua
    let cc2 = cc_t || marca(String::from("ERROR: no debia imprimirse (caso 2)"));

    // Caso 3 (control): true && f() -> f() SI se evalua
    let cc3 = cc_t && marca(String::from("caso 3: si se evalua"));

    println!("{}", cc1);
    println!("{}", cc2);
    println!("{}", cc3);
    // Esperado: caso 3: si se evalua / false / true / true
    // NINGUNA de las dos lineas que empiezan con ERROR debe aparecer.


    // ===== 1.14 Manejo de None (1) =====
    // i32 + String no es una combinacion valida: el resultado es None,
    // se registra un error semantico y la ejecucion CONTINUA.
    let none_nombre = String::from("Ana");
    let none_res = 10 + none_nombre;
    println!("{}", none_res);
    println!("continua despues de None");
    // Esperado: un error semantico registrado en la tabla de errores,
    // apuntando a la linea del "10 + none_nombre", y luego la linea
    // "continua despues de None".
    // Lo que imprime println! para un valor None no lo define el
    // enunciado. Ver README, ambiguedad #19.


    // ===== 1.15 Literales y secuencia de escape (1 c/u = 2) =====
    // (a) Literales de cada tipo, escritos directamente
    println!("{}", 42);
    println!("{}", 3.1416);
    println!("{}", true);
    println!("{}", 'Q');
    println!("Cadena literal");
    // Esperado: 42 / 3.1416 / true / Q / Cadena literal

    // (b) Secuencias de escape y raw strings
    let esc_mensaje = String::from("Hola\nRust");
    let esc_comillas = String::from("El dijo: \"Hola\"");
    let esc_ruta = String::from("C:\\Users\\Diego");

    println!("{}", esc_mensaje);
    println!("{}", esc_comillas);
    println!("{}", esc_ruta);

    let raw_ruta = String::from(r"C:\Users\Diego");
    let raw_texto = String::from(r#"El dijo: "Hola Rust""#);

    println!("{}", raw_ruta);
    println!("{}", raw_texto);
    // Esperado: Hola / Rust / El dijo: "Hola" / C:\Users\Diego
    //           C:\Users\Diego / El dijo: "Hola Rust"
}

/* =====================================================================
   SALIDA ESPERADA COMPLETA (en orden)

   20
   25
   30
   1
   2
   3
   comentarios ignorados
   0
   0.0
   false

   10
   3.14
   true
   A
   Hola
   7
   2.5
   false
   Z
   Mundo
   0
   0.0
   false

   100
   1.5
   true
   B
   Rust
   42
   9.5
   true
   C
   Compiladores
   5
   10
   7
   28
   14
   4
   14
   6
   40
   2
   4
   -10
   12.5
   false
   true
   true
   true
   false
   false
   false
   false
   true
   caso 3: si se evalua
   false
   true
   true
   continua despues de None
   42
   3.1416
   true
   Q
   Cadena literal
   Hola
   Rust
   El dijo: "Hola"
   C:\Users\Diego
   C:\Users\Diego
   El dijo: "Hola Rust"

   Notas:
   - Las dos lineas en blanco corresponden a los String sin inicializar
     de 1.3 y 1.6 (cadena vacia).
   - El criterio 1.14 ademas debe registrar UN error semantico en la
     tabla de errores; si el interprete imprime algo para el valor None,
     esa linea va antes de "continua despues de None".
   ===================================================================== */
