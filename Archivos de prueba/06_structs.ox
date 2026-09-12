// =====================================================================
//  OxigenScript - Archivo de entrada 06
//  Hoja de calificacion, Seccion 6: Structs (11 pts)
//
//  main() va al final: este archivo NO depende del hoisting.
//
//  El lenguaje no trae abs() embebida, asi que polygon_area() usa una
//  funcion auxiliar valor_absoluto() escrita en OxigenScript.
//
//  El ejemplo del enunciado usa "age: u8", pero u8 no esta en la lista
//  de tipos <type>. Aqui se usa i32. Ver README, ambiguedad #12.
// =====================================================================

// ===== 6.1 Declaracion de structs (1) =====

struct Persona {
    nombre: String,
    edad: i32,
    activo: bool,
}

struct Point {
    x: f64,
    y: f64,
}

// ===== 6.3 Structs anidados (1) =====
// Triangle y Rect usan Point como tipo de sus campos.

struct Triangle {
    a: Point,
    b: Point,
    c: Point,
}

struct Rect {
    position: Point,
    width: f64,
    height: f64,
}


// ---------------------------------------------------------------------
//  6.4  polygon_area()
// ---------------------------------------------------------------------

fn valor_absoluto(v: f64) -> f64 {
    if v < 0.0 {
        return -v;
    }
    return v;
}

// Formula del cordon (shoelace) para un triangulo:
// area = |x1(y2-y3) + x2(y3-y1) + x3(y1-y2)| / 2
fn polygon_area(t: Triangle) -> f64 {
    let doble: f64 = t.a.x * (t.b.y - t.c.y) + t.b.x * (t.c.y - t.a.y) + t.c.x * (t.a.y - t.b.y);
    return valor_absoluto(doble) / 2.0;
}


// ---------------------------------------------------------------------
//  6.5  detect_collision()  (cajas alineadas a los ejes, AABB)
// ---------------------------------------------------------------------

fn detect_collision(a: Rect, b: Rect) -> bool {
    if a.position.x + a.width <= b.position.x {
        return false;
    }
    if b.position.x + b.width <= a.position.x {
        return false;
    }
    if a.position.y + a.height <= b.position.y {
        return false;
    }
    if b.position.y + b.height <= a.position.y {
        return false;
    }
    return true;
}


fn main() {

    // ===== Minimo obligatorio (viene de la seccion 1) =====
    let base_i: i32 = 3;
    let base_f: f64 = 7.5;
    let base_b: bool = true;
    let base_c: char = 'S';
    let base_s: String = String::from("Structs");

    println!("{}", base_i * 3);
    println!("{}", !base_b);
    println!("{}", base_f);
    println!("{}", base_c);
    println!("{}", base_s);
    // Esperado: 9 / false / 7.5 / S / Structs


    // ===== 6.2 Asignacion de atributos (1) =====
    // Se asigna un valor a cada campo al construir la instancia y luego
    // se leen con el operador punto.
    let persona = Persona {
        nombre: String::from("Pedro"),
        edad: 27,
        activo: true,
    };

    println!("{}", persona.nombre);
    println!("{}", persona.edad);
    println!("{}", persona.activo);
    // Esperado: Pedro / 27 / true


    // ===== 6.3 Structs anidados (1) =====
    let esquina = Point {
        x: 10.5,
        y: 20.25,
    };

    let caja = Rect {
        position: Point {
            x: 1.5,
            y: 2.25,
        },
        width: 5.5,
        height: 3.25,
    };

    println!("({}, {})", esquina.x, esquina.y);
    println!("({}, {})", caja.position.x, caja.position.y);
    println!("{}", caja.width);
    println!("{}", caja.height);
    // Esperado: (10.5, 20.25) / (1.5, 2.25) / 5.5 / 3.25


    // ===== 6.4 polygon_area() (3) =====
    // Triangulo 1: (0,0) (5,0) (0,3)  -> area 7.5
    let t1 = Triangle {
        a: Point { x: 0.0, y: 0.0 },
        b: Point { x: 5.0, y: 0.0 },
        c: Point { x: 0.0, y: 3.0 },
    };

    // Triangulo 2: (0,0) (7,0) (0,3)  -> area 10.5
    let t2 = Triangle {
        a: Point { x: 0.0, y: 0.0 },
        b: Point { x: 7.0, y: 0.0 },
        c: Point { x: 0.0, y: 3.0 },
    };

    // Triangulo 3: los mismos vertices del 1 pero en orden inverso.
    // El determinante sale negativo, asi que comprueba el valor absoluto.
    let t3 = Triangle {
        a: Point { x: 0.0, y: 0.0 },
        b: Point { x: 0.0, y: 3.0 },
        c: Point { x: 5.0, y: 0.0 },
    };

    println!("{}", polygon_area(t1));
    println!("{}", polygon_area(t2));
    println!("{}", polygon_area(t3));
    // Esperado: 7.5 / 10.5 / 7.5


    // ===== 6.5 detect_collision() (5) =====
    let r1 = Rect {
        position: Point { x: 0.0, y: 0.0 },
        width: 4.0,
        height: 4.0,
    };

    // Se solapa con r1
    let r2 = Rect {
        position: Point { x: 2.0, y: 2.0 },
        width: 4.0,
        height: 4.0,
    };

    // Lejos de r1
    let r3 = Rect {
        position: Point { x: 10.0, y: 10.0 },
        width: 2.0,
        height: 2.0,
    };

    // Pegado a r1 pero sin solaparse: el borde derecho de r1 (x = 4)
    // coincide con el borde izquierdo de r4. Tocarse no es colisionar.
    let r4 = Rect {
        position: Point { x: 4.0, y: 0.0 },
        width: 2.0,
        height: 2.0,
    };

    println!("{}", detect_collision(r1, r2));
    println!("{}", detect_collision(r1, r3));
    println!("{}", detect_collision(r1, r4));
    // Esperado: true / false / false
}

/* =====================================================================
   SALIDA ESPERADA COMPLETA (en orden)

   9
   false
   7.5
   S
   Structs
   Pedro
   27
   true
   (10.5, 20.25)
   (1.5, 2.25)
   5.5
   3.25
   7.5
   10.5
   7.5
   true
   false
   false

   Nota: todos los f64 que se imprimen tienen parte decimal distinta de
   cero a proposito, para que la salida no dependa de si el interprete
   imprime 5 o 5.0. Ver README, ambiguedad #9.
   ===================================================================== */
