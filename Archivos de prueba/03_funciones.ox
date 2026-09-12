// =====================================================================
//  OxigenScript - Archivo de entrada 03
//  Hoja de calificacion, Seccion 3: Funciones (20 pts)
//
//  IMPORTANTE (criterio 3.6): main() esta declarada PRIMERO en el
//  archivo y llama funciones que se declaran despues. Si el interprete
//  no hace hoisting de declaraciones de funcion, este archivo falla
//  completo.
//
//  El lenguaje NO tiene sqrt() ni abs() embebidas, asi que la raiz
//  cuadrada se calcula dentro del propio OxigenScript (Newton-Raphson).
// =====================================================================

fn main() {

    // ===== Minimo obligatorio (viene de la seccion 1) =====
    let base_i: i32 = 6;
    let base_f: f64 = 1.5;
    let base_b: bool = false;
    let base_c: char = 'F';
    let base_s: String = String::from("Funciones");

    println!("{}", base_i * 2);
    println!("{}", !base_b);
    println!("{}", base_f);
    println!("{}", base_c);
    println!("{}", base_s);
    // Esperado: 12 / true / 1.5 / F / Funciones


    // ===== 3.6 Main (Hoisting) (2) =====
    // Esta llamada se resuelve contra una funcion declarada mas abajo.
    println!("hoisting: main se declaro primero");


    // ===== 3.1 Funciones sin parametro y sin retorno (1 c/u = 2) =====
    greet();
    gen_pascal();


    // ===== 3.2 Funciones con parametros sin retorno (1 c/u = 2) =====
    print_msg(String::from("hola desde print_msg"));
    show_factorial(5);


    // ===== 3.3 Funciones con parametros y con retorno (2 c/u = 4) =====
    println!("{}", fibonacci(10));
    println!("{}", fibonacci(1));
    println!("{}", euclidean_distance(0.0, 0.0, 3.0, 4.0));
    println!("{}", euclidean_distance(0.0, 0.0, 6.0, 8.0));


    // ===== 3.4 aprox_pi() + helper_leibniz() (5) =====
    let pi: f64 = aprox_pi();
    println!("{}", pi);
    // Comprobacion determinista: el valor exacto impreso depende de como
    // el interprete formatee los f64, pero el rango no.
    println!("{}", pi > 3.14 && pi < 3.15);


    // ===== 3.5 resolve_hanoi() (5) =====
    resolve_hanoi();
}


// ---------------------------------------------------------------------
//  3.1  Funciones sin parametro y sin retorno
// ---------------------------------------------------------------------

fn greet() {
    println!("Hola desde greet()");
}

// Triangulo de Pascal, 5 filas. Se imprime un valor por linea y "---"
// al cerrar cada fila, porque el lenguaje no tiene forma de convertir
// i32 a String para armar la fila completa en un solo println!.
// Usa la identidad C(n, k+1) = C(n, k) * (n - k) / (k + 1), que da
// siempre una division exacta.
fn gen_pascal() {
    let mut n: i32 = 0;

    while n <= 4 {
        let mut k: i32 = 0;
        let mut c: i32 = 1;

        while k <= n {
            println!("{}", c);
            c = c * (n - k) / (k + 1);
            k += 1;
        }

        println!("---");
        n += 1;
    }
}


// ---------------------------------------------------------------------
//  3.2  Funciones con parametros y sin retorno
// ---------------------------------------------------------------------

fn print_msg(msg: String) {
    println!("mensaje: {}", msg);
}

fn show_factorial(n: i32) {
    let mut i: i32 = 1;
    let mut acumulado: i32 = 1;

    while i <= n {
        acumulado *= i;
        i += 1;
    }

    println!("{}! = {}", n, acumulado);
}


// ---------------------------------------------------------------------
//  3.3  Funciones con parametros y con retorno
// ---------------------------------------------------------------------

fn fibonacci(n: i32) -> i32 {
    if n < 2 {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Raiz cuadrada por Newton-Raphson. Auxiliar de euclidean_distance,
// porque el lenguaje no trae sqrt() embebida.
fn sqrt_newton(valor: f64) -> f64 {
    if valor <= 0.0 {
        return 0.0;
    }

    let mut x: f64 = valor;
    let mut i: i32 = 0;

    while i < 30 {
        x = (x + valor / x) / 2.0;
        i += 1;
    }

    return x;
}

fn euclidean_distance(x1: f64, y1: f64, x2: f64, y2: f64) -> f64 {
    let dx: f64 = x2 - x1;
    let dy: f64 = y2 - y1;
    return sqrt_newton(dx * dx + dy * dy);
}


// ---------------------------------------------------------------------
//  3.4  aprox_pi() + helper_leibniz()
// ---------------------------------------------------------------------

// Termino k de la serie de Leibniz: (-1)^k / (2k + 1)
fn helper_leibniz(k: i32) -> f64 {
    let denominador: f64 = 2.0 * k + 1.0;

    if k % 2 == 0 {
        return 1.0 / denominador;
    }

    return -1.0 / denominador;
}

// pi = 4 * (1 - 1/3 + 1/5 - 1/7 + ...)
fn aprox_pi() -> f64 {
    let mut suma: f64 = 0.0;
    let mut k: i32 = 0;

    while k < 1000 {
        suma += helper_leibniz(k);
        k += 1;
    }

    return 4.0 * suma;
}


// ---------------------------------------------------------------------
//  3.5  resolve_hanoi()
// ---------------------------------------------------------------------

// No se usa "return;" sin valor porque la gramatica del enunciado define
// <return_stmt> ::= return <exp> ; (siempre con expresion). Por eso el
// caso base va con if/else.
fn hanoi_move(n: i32, origen: char, auxiliar: char, destino: char) {
    if n == 1 {
        println!("mover disco 1 de {} a {}", origen, destino);
    } else {
        hanoi_move(n - 1, origen, destino, auxiliar);
        println!("mover disco {} de {} a {}", n, origen, destino);
        hanoi_move(n - 1, auxiliar, origen, destino);
    }
}

fn resolve_hanoi() {
    hanoi_move(3, 'A', 'B', 'C');
}

/* =====================================================================
   SALIDA ESPERADA COMPLETA (en orden)

   12
   true
   1.5
   F
   Funciones
   hoisting: main se declaro primero
   Hola desde greet()
   1
   ---
   1
   1
   ---
   1
   2
   1
   ---
   1
   3
   3
   1
   ---
   1
   4
   6
   4
   1
   ---
   mensaje: hola desde print_msg
   5! = 120
   55
   1
   5
   10
   3.140592653839794
   true
   mover disco 1 de A a C
   mover disco 2 de A a B
   mover disco 1 de C a B
   mover disco 3 de A a C
   mover disco 1 de B a A
   mover disco 2 de B a C
   mover disco 1 de A a C

   Notas:
   - Las distancias euclidianas son 5.0 y 10.0. Segun como el interprete
     formatee los f64, pueden imprimirse como "5" y "10" o como "5.0" y
     "10.0". Las dos formas son validas: el enunciado no lo define.
     Ver README, ambiguedad #9.
   - El valor de pi depende de la cantidad de decimales que imprima el
     interprete. Lo que SI debe cumplirse es la linea "true" que sigue,
     que comprueba 3.14 < pi < 3.15.
   - Las 5 filas del triangulo de Pascal son 1 / 1 1 / 1 2 1 / 1 3 3 1 /
     1 4 6 4 1, impresas un valor por linea y separadas por "---".
   ===================================================================== */
