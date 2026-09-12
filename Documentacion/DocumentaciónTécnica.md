# Documentación Técnica

## 1. Introducción

Este documento describe la implementación del intérprete de **OxigenScript**, un lenguaje con sintaxis inspirada en Rust. Cubre la gramática formal implementada, la arquitectura, el método de ejecución, y las decisiones de diseño y desafíos técnicos enfrentados durante el desarrollo.

El intérprete sigue una arquitectura monolítica cliente/servidor:

- **Cliente (frontend):** interfaz web en React, con editor de código, consola de salida y panel de reportes (Errores, Tabla de símbolos, AST).
- **Servidor (backend):** API REST en Python (Flask) que aloja el pipeline completo del intérprete.
- **Herramienta de análisis léxico/sintáctico:** PLY (Python Lex-Yacc).
- **Generación del reporte de AST:** Graphviz

---

## 2. Arquitectura del intérprete

El backend está organizado en fases secuenciales, cada una en su propio módulo:

| Módulo | Responsabilidad |
|---|---|
| `lexer.py` | **Análisis léxico:** convierte el código fuente en tokens y detecta errores léxicos (caracteres no reconocidos, comentarios de bloque sin cerrar) mediante una pasada completa e independiente del archivo. |
| `parser.py` | **Análisis sintáctico (LALR, vía PLY/yacc):** construye el Árbol de Sintaxis Abstracta (AST) a partir de los tokens e incluye recuperación de errores sintácticos para poder seguir detectando errores adicionales tras el primero. |
| `semantic.py` | **Análisis semántico:** tabla de símbolos, verificación de tipos, ámbitos (scopes), mutabilidad, sombreado (shadowing), validación de arreglos y structs. |
| `interpreter.py` | **Ejecución:** recorre el AST y evalúa el programa directamente (interpretación por recorrido de árbol), sin generar código intermedio ni bytecode. |
| `app.py` | Expone el pipeline anterior como un endpoint REST (`POST /execute`), unifica los reportes de errores de las tres fases, y genera la tabla de símbolos y el AST (con Graphviz) para el frontend. |
| `ast_generator.py` | Convierte la lista aplanada de nodos del AST (etiqueta + profundidad) en un grafo Graphviz y lo renderiza como imagen PNG codificada en base64. |

### 2.1. Método de "generación de código a bajo nivel"

OxigenScript no compila a un lenguaje intermedio ni a bytecode: es un **intérprete de recorrido de árbol (tree-walking interpreter)**. Una vez construido el AST y validado semánticamente, `interpreter.py` recorre cada nodo recursivamente y lo evalúa directamente en Python, usando las estructuras de datos nativas de Python como representación en tiempo de ejecución de los valores de OxigenScript:

| Tipo de OxigenScript | Representación en tiempo de ejecución (Python) |
|---|---|
| `i32` | `int` |
| `f64` | `float` |
| `bool` | `bool` |
| `char` | `str` de un solo carácter |
| `String` | `str` |
| `[T; N]` | `list` |
| `struct` | `dict` (nombre de campo → valor) |

Se eligió este enfoque por ser el más directo de implementar sobre un AST ya construido con PLY, evitando la complejidad adicional de diseñar una máquina virtual o un formato de bytecode propio, que no aporta valor añadido para los objetivos del proyecto.

### 2.2. Manejo de ámbitos (scopes)

Se usan dos estructuras de ámbito paralelas, una para cada fase:

- **`TablaSimbolos`** (en `semantic.py`): fue usada durante el análisis semántico. Cada ámbito (global, cada función, cada bloque `{}`, `if`, `while`, `loop`) crea una tabla hija enlazada a su padre. Además de resolver referencias (`obtener`), cada tabla mantiene un **historial completo** de declaraciones (no solo la última), para que el *shadowing* se refleje de manera correcta en el reporte de tabla de símbolos como declaraciones separadas en vez de que una sobrescriba a la otra.
- **`Entorno`** (en `interpreter.py`): fue usada durante la ejecución real. Sigue el mismo patrón de scopes anidados pero solo necesita la declaración **vigente** de cada variable (no su historial), ya que su propósito es resolver valores en tiempo de ejecución y no generar un reporte.

---

## 3. Gramática formal de OxigenScript

A continuación se presenta la gramática implementada, en notación BNF simplificada. Se anota junto a cada producción cuando difiere o amplia lo descrito de forma informal en el enunciado del proyecto.

```bnf
programa        ::= declaracion*
declaracion     ::= funcion | struct_decl

funcion         ::= "fn" ID "(" lista_parametros ")" ("->" tipo)? "{" sentencia* "}"
lista_parametros::= (parametro ("," parametro)*)?
parametro       ::= ID ":" tipo

struct_decl     ::= "struct" ID "{" campo_struct+ "}"
campo_struct    ::= ID ":" tipo ","?          (* la coma del ultimo campo es opcional *)

tipo            ::= "i32" | "f64" | "bool" | "char" | "String" | ID
                  | "[" tipo ";" INTEGER "]"

sentencia       ::= declaracion_let
                  | asignacion
                  | sentencia_if | sentencia_while | sentencia_loop | sentencia_match
                  | sentencia_return | sentencia_break | sentencia_continue
                  | sentencia_bloque
                  | expresion ";"

declaracion_let ::= "let" "mut"? ID (":" tipo)? ("=" expresion)? ";"

asignacion      ::= ID ("=" | "+=" | "-=" | "*=" | "/=" | "%=") expresion ";"
                  (* +=, -=, *=, /=, %= se desazucaran internamente a "x = x <op> expr" *)

sentencia_if    ::= "if" expresion "{" sentencia* "}" ("else" ("{" sentencia* "}" | sentencia_if))?
sentencia_while ::= "while" expresion "{" sentencia* "}"
sentencia_loop  ::= LABEL? "loop" "{" sentencia* "}"     (* LABEL: 'nombre, opcional *)
sentencia_bloque::= "{" sentencia* "}"                    (* bloque anonimo, crea su propio scope *)

sentencia_match ::= "match" expresion "{" caso_match+ "}"
caso_match      ::= (INTEGER | ID) "=>" (expresion | "{" sentencia* "}") ","
                  (* "_" (comodin) se reconoce como ID con valor especial *)

sentencia_return   ::= "return" expresion? ";"
sentencia_break    ::= "break" LABEL? ";"
sentencia_continue ::= "continue" LABEL? ";"

expresion       ::= expresion ("+"|"-"|"*"|"/"|"%"|"=="|"!="|">"|">="|"<"|"<="|"&&"|"||") expresion
                  | ("-" | "!") expresion
                  | expresion "." ID                                  (* acceso a campo *)
                  | expresion "." ID "(" lista_argumentos ")"          (* llamada a metodo, ej. arr.len() *)
                  | expresion "[" expresion "]"                       (* acceso a arreglo *)
                  | "&" expresion "[" expresion ".." expresion "]"     (* slice *)
                  | ID "(" lista_argumentos ")"                       (* llamada a funcion *)
                  | "println" "!" "(" lista_argumentos ")"            (* println! con "!" obligatorio *)
                  | "String" "::" ID "(" lista_argumentos ")"         (* String::from(..) / String::new() *)
                  | ID "{" (ID ":" expresion ","?)* "}"                (* instanciacion de struct *)
                  | "[" lista_expresiones "]" | "[" expresion ";" INTEGER "]"
                  | INTEGER | FLOAT | STRING | CHAR_LITERAL | "true" | "false" | ID
                  | "(" expresion ")"

lista_argumentos ::= (expresion ("," expresion)*)?
```

### 3.1. Diferencias respecto a la redacción informal del enunciado

Durante la implementación se indentificó y se resolvieron varias ambigüedades no explícitas en la gramática informal del enunciado:

1. **Token `=>` vs `->`.** El enunciado usa `=>` para los brazos de `match` y `->` para el tipo de retorno de función. Son símbolos léxicos distintos y ambos deben reconocerse por separado (`FLECHA` para `->`, `FLECHA_GORDA` para `=>`).
2. **`println!` requiere el símbolo `!`.** Se modeló como `PRINTLN` seguido del token de negación (`!`) y paréntesis, ya que `!` también se usa como operador de negación lógica en otros contextos.
3. **Ambigüedad LALR(1) entre `if`/`while`/`match` con una variable simple como condición y la sintaxis de instanciación de struct.** `if bandera { ... }` y `Persona { campo: valor }` comparten el prefijo `ID {` y con un solo token de lookahead (LALR(1)) el parser no puede decidir cuál de las dos construcciones está leyendo. Se resolvió agregando producciones específicas para el caso "condición = identificador simple" en `if`, `while` y `match`, evitando que el parser tenga que decidir prematuramente.
4. **Etiquetas de `loop` (`'outer`, `'inner`).** Se introdujo un token léxico dedicado (`LABEL`, con patrón `'[a-zA-Z_][a-zA-Z0-9_]*`) declarado en el lexer antes que el reconocimiento de literales de carácter (`'A'`), para que un carácter literal de una sola letra no sea interpretado incorrectamente como el inicio de una etiqueta.
5. **`::` como operador de espacio de nombres.** Fue necesario para `String::from(...)` / `String::new()`; no existe en la mayoría de gramáticas de expresiones simples y se agregó como token propio (`DOSDOSPUNTOS`).
6. **Coma final opcional** en la declaración de un `struct` y en su instanciación para aceptar el estilo "trailing comma" común en código real.

---

## 4. Decisiones de diseño

### 4.1. Manejo de errores y resiliencia

El intérprete no se detiene ante el primer error encontrado:

- **Léxico:** se hace una pasada completa e independiente del archivo (`escanear_errores_lexicos`) para recolectar todos los errores léxicos sin depender de hasta dónde llegue el parser.
- **Sintáctico:** se usó el mecanismo de recuperación de errores nativo de PLY/yacc (producciones `sentencia : error PUNTOCOMA | error LLAVEDER`) que descarta tokens hasta el siguiente punto de sincronización (`;` o `}`) y continúa parseando el resto del archivo en vez de terminar por completo.
- **Semántico y de ejecución:** ambas fases acumulan todos los errores que encuentran en una lista sin detener el análisis o la ejecución a menos que el error impida continuar de forma segura. Para evitar reportar el mismo problema dos veces (una vez como error semántico y otra como excepción cruda al intentar ejecutarlo), el intérprete omite la ejecución de cualquier sentencia donde la línea ya tiene un error semántico reportado.

Cada error se reporta con **tipo, línea, columna y descripción**, en el formato de dos líneas especificado en el enunciado:

```
[Error <Tipo>] Línea <línea>, Columna <columna>
<descripción>
```

La columna se calcula como la distancia desde el último salto de línea anterior a la posición del token y no como la posición absoluta en el archivo completo.

### 4.2. Shadowing en la tabla de símbolos

Dado que el enunciado pide el sombreado como parte del lenguaje, la tabla de símbolos conserva todas las declaraciones de un mismo nombre en un ámbito en el orden en que aparecen, en vez de que la última sobrescriba a las anteriores en el reporte. La resolución de referencias durante el análisis (`obtener`) sigue usando la declaración más reciente que es el comportamiento correcto en tiempo de ejecución.

### 4.3. Valores por defecto de variables no inicializadas

Cuando una variable se declara con tipo pero sin valor inicial (`let x: i32;`), se le asigna el valor por defecto de su tipo declarado en el momento de la ejecución (`0` para `i32`, `0.0` para `f64`, `false` para `bool`, cadena vacía para `String`/`char`).

### 4.4. Métodos sobre valores (`variable.metodo()`)

Las funciones embebidas que operan sobre `String` y arreglos (`len`, `contains`, `replace`, `split`, `to_uppercase`, `to_lowercase`, `reverse`) no se tratan como palabras reservadas del lenguaje. Se reconocen como identificadores normales, y la sintaxis `variable.metodo(args)` se traduce internamente a una llamada de función con el receptor como primer argumento (`metodo(variable, args...)`), reutilizando la misma lógica de despacho que las llamadas a función con paréntesis directos.

### 4.5. Reporte del AST

El AST se serializa como una lista plana de nodos `{etiqueta, profundidad}` en el orden de un recorrido en preorden (DFS), y `ast_generator.py` reconstruye la jerarquía a partir de la profundidad de cada nodo para generar el grafo con Graphviz y así se evita tener que definir clases de nodo específicas para cada construcción del lenguaje.

---

## 5. Desafíos técnicos enfrentados

Durante el desarrollo del proyecto se identificaron y corrigieron los siguientes problemas que son los siguientes:

- **Colisión de tokens entre etiquetas de `loop` y literales de carácter:** Los dos comienzan con `'` así que se resolvió con un orden de precedencia explícito entre las dos funciones del lexer y una regla que exige la comilla de cierre solo para el literal de carácter.

- **Confusión entre literales `0`/`1` y booleanos:** La comparación (`if valor in [True, False]`) fallaba porque en Python `1 == True` y `0 == False` así que se corrigió distinguiendo por el tipo de token gramatical y no por el valor.

- **División entera vs. división real:** `i32 / i32` debe producir `i32` (truncado hacia 0 como en Rust), no un `float` como hace la división `/` nativa de Python. Se corrigió truncando explícitamente el resultado cuando ambos operandos son enteros.

- **Evaluación de corto-circuito en `&&`/`||`:** La implementación inicial evaluaba ambos operandos antes de aplicar el operador. Se corrigió evaluando el operando izquierdo primero y evitando evaluar el derecho cuando el resultado ya está determinado.

- **Recursión de tablas de ámbito no enlazadas:** Las tablas de símbolos creadas para el cuerpo de un `if`/`while`/`loop` no se registraban como hijas de su tabla padre, por lo que las variables declaradas dentro de esos bloques nunca llegaban al reporte final de tabla de símbolos.

- **Ambigüedad de longitud de producción en la declaración `let`:** Las alternativas gramaticales distintas (`let x = expr;` y `let x: Tipo;`) tenían la misma longitud de producción y se manejaban con una única función basada en `len(p)` lo que hacia que una rama nunca se alcanzara. Se resolvió separando cada alternativa en su propia función de regla.

---