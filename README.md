# OxigenScript

Intérprete de **OxigenScript**, un lenguaje de programación académico con sintaxis inspirada en Rust. Es el **Proyecto 1** del curso **Organización de Lenguajes y Compiladores 2**.

El proyecto consiste en construir desde cero un intérprete: un programa capaz de leer código escrito en OxigenScript, revisar que esté bien escrito y ejecutarlo. Para lograrlo, el código pasa por varias etapas: primero se separa en piezas básicas, luego se verifica que su estructura sea correcta, después se comprueba que tenga sentido y finalmente se ejecuta.

Todo se usa desde una página web con un editor de código donde se puede escribir un programa o abrir uno existente, guardarlo y ejecutarlo. El resultado aparece en una consola de salida, y junto a ella hay un panel con tres reportes:

- **Errores**: los problemas encontrados en el código, indicando el tipo (léxico, sintáctico o semántico), la descripción, la línea y la columna. El intérprete sigue analizando después de un error, así que puede mostrar varios en una sola ejecución.
- **Tabla de símbolos**: todas las variables, funciones y structs declarados, con su tipo, su ámbito y su valor.
- **AST**: una imagen del árbol que representa la estructura del programa.

## Cómo correrlo

Primera vez, desde la raíz del repositorio:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd frontend
npm install
```

Para ejecutarlo se usan dos terminales.

Backend:

```bash
source venv/bin/activate
python -m backend.app
```

Frontend:

```bash
cd frontend
npm run dev
```

Después se abre en el navegador `http://localhost:5173`.

> Para el reporte del AST también debe estar instalado Graphviz en el sistema.
