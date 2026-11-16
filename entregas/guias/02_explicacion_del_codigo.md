---
title: "Guía 2 · Explicación del código"
subtitle: "Proyecto final de Álgebra Lineal · Cifrado de Hill · Grupo 15"
---

## Para qué sirve esta guía

Explica cómo está hecho el programa: qué hace cada archivo y cada función importante, qué viene de librerías y qué programamos nosotros, y cómo correrlo. Es para quien defienda la parte de Python en la presentación, que es el 40 % de la nota de mañana: «Presentación Python», «Resuelve varios tamaños o casos», «Uso de librerías y funciones propias» y «Organización del código».

## 1. Cómo correr el programa

### Preparación (una sola vez por computadora)

Hace falta Python 3.10 o más nuevo y conexión a internet para instalar las librerías.

```bash
git clone https://github.com/krisspaz/proyecto_algebra.git
cd proyecto_algebra
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

En **Windows**, cambiar `python3` por `py` y `.venv/bin/` por `.venv\Scripts\` (por ejemplo, `.venv\Scripts\pip install -r requirements.txt`).

### Comandos

| Para… | Comando | Qué pasa |
|---|---|---|
| Abrir la página web | `.venv/bin/python app.py` | Abrir **http://127.0.0.1:5050** en el navegador. La terminal tiene que quedar abierta; se detiene con `Ctrl+C` |
| Correr las pruebas | `.venv/bin/python -m unittest -v` | Corre las 35 pruebas; al final debe decir `OK` |
| Demo de texto en consola | `.venv/bin/python demo.py` | Cifra, descifra, rechaza una clave inválida y hace el ataque |
| Demo de imágenes | `.venv/bin/python demo_imagen.py` | Imprime la cuenta de un bloque de píxeles y guarda las imágenes en `salida/` |
| Demo con una foto propia | `.venv/bin/python demo_imagen.py foto.png` | Lo mismo con la foto |
| Tablas y figuras del reporte | `.venv/bin/python resultados.py` | Calcula las tablas de Resultados y guarda las figuras en `figuras/` |
| Comprobar la inversa propia | `.venv/bin/python inversa.py` | Compara nuestra inversa con la de sympy en 3 claves y 4 módulos |
| Ver el notebook | Abrir `cifrado_hill.ipynb` en VS Code (extensión Jupyter) y elegir el kernel de `.venv` | O leer el PDF ya ejecutado: `entregas/programa/cifrado_hill.pdf` |

**Si el puerto 5050 está ocupado:** `PORT=5051 .venv/bin/python app.py` y abrir http://127.0.0.1:5051.

## 2. Organización

El código está separado por tema: cada archivo hace una cosa y la parte matemática no depende de la página web.

```
proyecto_algebra/
├── inversa.py           ← álgebra a mano: mcd, determinante, adjunta, K⁻¹
├── hill.py              ← alfabetos, validar la clave, cifrar, descifrar
├── ataque.py            ← recuperar la clave: K = C · P⁻¹
├── imagen.py            ← bloques de píxeles mod 256, con y sin encadenar
├── app.py               ← servidor web (Flask)
├── templates/, static/  ← la página que se ve (HTML, CSS, JavaScript)
├── demo.py              ← demo de texto en consola
├── demo_imagen.py       ← demo de imágenes en consola
├── resultados.py        ← tablas y figuras de Resultados del reporte
├── cifrado_hill.ipynb   ← notebook con las cuentas explicadas
├── tests/test_hill.py   ← 35 pruebas automáticas
└── requirements.txt     ← librerías que hay que instalar
```

Las dependencias van en una sola dirección:

```
inversa.py ──→ hill.py ──→ ataque.py ──┐
     │                                 ├──→ app.py ──→ página web
     └───────→ imagen.py ──────────────┘
```

(`hill.py` también lo usa `app.py` directamente.)

`inversa.py` no usa ninguna librería: es álgebra pura con listas de Python. Todo lo demás se apoya en él.

## 3. Funciones propias y librerías

| Lo hicimos nosotros | Lo usamos de una librería |
|---|---|
| Inverso modular con Euclides extendido (`inverso_modular`) | **sympy** `Matrix`: guardar matrices y multiplicarlas en el cifrado de texto |
| Determinante por cofactores (`determinante`) | **numpy**: multiplicar cientos de miles de bloques de píxeles de una vez |
| Adjunta (`adjunta`) e inversa módulo m (`inversa_mod`) | **Pillow**: abrir y guardar archivos de imagen (PNG, JPG) |
| Validación de la clave con `mcd(det K, m) = 1` | **Flask**: el servidor de la página web |
| Cifrado y descifrado por bloques, con relleno | **matplotlib**: las figuras del notebook y del informe |
| Los tres alfabetos (26, 37 y 113 símbolos) | `math.gcd`, `unicodedata`, `itertools`, `secrets` (vienen con Python) |
| El ataque que busca bloques invertibles | |
| Cifrado de imágenes, encadenamiento y `explicar_bloque` | |

Idea para decir en la presentación:

> Las librerías hacen el trabajo pesado (guardar matrices, procesar imágenes, mostrar la página), pero el álgebra del curso (determinante, adjunta, inverso modular e inversa) la programamos nosotros, con la misma fórmula del pizarrón. Y para estar seguros, `inversa.py` compara nuestro resultado con el de sympy.

## 4. Los archivos, uno por uno

### 4.1 `inversa.py`: el álgebra a mano

Es el corazón matemático. Trabaja con matrices como listas de listas, por ejemplo `[[3, 3], [2, 5]]`.

| Función | Qué hace | Teoría del curso |
|---|---|---|
| `inverso_modular(a, m)` | Busca `x` con `a·x ≡ 1 (mod m)` con Euclides extendido. Si `mcd(a, m) ≠ 1`, avisa que no existe | Identidad de Bézout |
| `menor(A, i, j)` | Devuelve `A` sin la fila `i` ni la columna `j` | Menores |
| `determinante(A)` | Desarrollo por cofactores en la primera fila, recursivo | Determinante por cofactores |
| `adjunta(A)` | Traspuesta de la matriz de cofactores | Adjunta |
| `inversa_mod(A, m)` | `K⁻¹ = det(K)⁻¹ · adj(K) (mod m)` | Inversa con la adjunta |
| `multiplicar_mod(A, B, m)` | Producto de matrices reduciendo módulo `m` | Producto de matrices |

Es la función crítica del proyecto:

```python
def inversa_mod(A, m):
    det = determinante(A) % m
    det_inv = inverso_modular(det, m)  # aquí falla si mcd(det, m) != 1
    adj = adjunta(A)
    inv = []
    for fila in adj:
        inv.append([(det_inv * x) % m for x in fila])
    return inv
```

Son cuatro líneas que siguen la fórmula `K⁻¹ = det(K)⁻¹ · adj(K)`. La única diferencia con los reales es que, en vez de dividir entre el determinante, se multiplica por su inverso modular.

### 4.2 `hill.py`: el cifrado

**Alfabetos.** Hay tres, y el módulo `m` es la cantidad de símbolos:

| Nombre | Símbolos | m | Relleno |
|---|---|---|---|
| `LETRAS` | A–Z | 26 | X |
| `ALFANUMERICO` | A–Z, 0–9 y espacio | 37 (primo) | espacio |
| `COMPLETO` | Todo el teclado, más ¡ ¿ tildes ñ ü € ° | 113 (primo) | espacio |

**Funciones principales:**

| Función | Qué hace |
|---|---|
| `limpiar(texto, alfabeto)` | Adapta el texto al alfabeto: con «Solo letras», `á → A` y quita lo que no se puede cifrar |
| `texto_a_numeros` / `numeros_a_texto` | Cada símbolo es su posición en el alfabeto: A = 0, B = 1… |
| `validar_clave(K, m)` | Rechaza la clave si no es cuadrada o si `mcd(det K, m) ≠ 1`, y dice por qué |
| `analizar_clave(K, m)` | Devuelve el determinante, el mcd y la inversa (la usa la página para mostrarlos) |
| `preparar_mensaje` | Limpia el texto y lo completa con el relleno hasta un múltiplo de `n` |
| `multiplicar_bloques(M, texto)` | Pone cada bloque como **columna** de una matriz `P` y calcula `M · P` y `M · P mod m`. Así se cifran todos los bloques con una sola multiplicación |
| `cifrar(mensaje, K)` | Valida la clave, prepara el mensaje y multiplica por `K` |
| `descifrar(cifrado, K)` | Valida la clave, calcula `K⁻¹` con `inversa_mod` y multiplica por ella |

Como `n` sale del tamaño de la clave, el mismo código sirve para 2×2, 3×3, 4×4 o cualquier tamaño.

### 4.3 `ataque.py`: romper el cifrado

`recuperar_clave(texto_plano, texto_cifrado, n, alfabeto)`:

1. Convierte el texto conocido y su cifrado en números y los corta en bloques.
2. Prueba grupos de `n` bloques hasta encontrar uno cuya matriz `P` sea invertible módulo `m`, con la misma condición `mcd(det P, m) = 1` que la clave.
3. Calcula `K = C · P⁻¹ (mod m)` con nuestra `inversa_mod`.

Si ningún grupo sirve, `_motivo_del_fallo` explica por qué: por ejemplo, «det P ≡ 10 y mcd(10, 26) = 2». También sugiere qué probar. Prueba como máximo 20 000 combinaciones, para no quedarse colgado con textos muy repetitivos.

### 4.4 `imagen.py`: imágenes módulo 256

Una imagen se lee como una tabla de `alto × ancho × 3` números de 0 a 255 (rojo, verde y azul de cada píxel). **No se usa ASCII.**

| Función | Qué hace |
|---|---|
| `validar_clave_imagen(K)` | Como `256 = 2⁸`, la clave sirve si y solo si `det K` es impar |
| `rellenar(img, n)` | Agrega columnas negras para que el ancho sea múltiplo de `n` |
| `cifrar_imagen` / `descifrar_imagen` | Corta cada canal en bloques de `n` píxeles horizontales y calcula `K · p mod 256`. Con numpy se hacen todos los bloques en una sola multiplicación |
| `cifrar_imagen_encadenado` | `cᵢ = K · (pᵢ + cᵢ₋₁) mod 256`: cada bloque arrastra el anterior y las figuras dejan de verse |
| `descifrar_imagen_encadenado` | `pᵢ = K⁻¹ · cᵢ − cᵢ₋₁ mod 256` |
| `explicar_bloque(img, K, fila, columna)` | Devuelve la cuenta de un bloque, canal por canal (la usan el informe, el notebook y la página) |
| `imagen_de_prueba()` | La imagen de ejemplo: un círculo rojo, un rectángulo azul y un degradado gris |

### 4.5 `app.py`: la página web

Es el puente entre la página y el código de arriba. No hace cuentas propias: recibe lo que la persona escribe, llama a `hill.py`, `ataque.py` o `imagen.py` y devuelve el resultado.

| Ruta | Qué hace |
|---|---|
| `GET /` | Muestra la página |
| `POST /api/procesar` | Cifra o descifra. Devuelve el resultado, el determinante, el mcd, `K⁻¹` y el paso a paso de los primeros 8 bloques |
| `GET /api/clave-aleatoria` | Genera una clave al azar que sirva para el alfabeto elegido |
| `POST /api/atacar` | Ejecuta el ataque |
| `POST /api/imagen` | Cifra la imagen de ejemplo o una subida (que se achica a 320 px por lado) y devuelve las cuatro imágenes y la cuenta del bloque elegido |

También revisa todo lo que llega: tamaño de clave 2, 3 o 4, textos de hasta 5000 caracteres y archivos de hasta 10 MB. Si algo está mal, responde con un mensaje claro en vez de fallar.

### 4.6 La página (`templates/`, `static/`)

`index.html` es la estructura, `estilos.css` el aspecto (pensado para proyectar: fondo blanco, letra grande, la clave en azul y el resultado resaltado) y `app.js` reacciona a lo que escribes. Cada vez que cambias el mensaje o la clave, le pide a Python el resultado y lo dibuja. **Toda la matemática la hace Python**; el navegador solo muestra.

## 5. El recorrido de un mensaje

Así viaja un mensaje desde que se escribe hasta que sale cifrado:

1. La persona escribe el mensaje y la clave en la página.
2. `app.js` manda el texto, la clave, el alfabeto y el modo a `POST /api/procesar`.
3. `app.py` revisa los datos y llama a `analizar_clave`, que usa `determinante` y `mcd`.
4. **¿La clave sirve?** Si `mcd(det K, m) ≠ 1`, responde «Esta clave no tiene inversa» y la página pone la matriz en rojo.
5. Si sirve, `preparar_mensaje` limpia el texto y lo rellena hasta un múltiplo de `n`.
6. `multiplicar_bloques` arma `P` con un bloque por columna y calcula `K · P mod m`. Para descifrar usa `K⁻¹`, calculada con `inversa_mod`.
7. `numeros_a_texto` convierte los números en símbolos.
8. La página muestra el resultado, `K⁻¹` y el paso a paso (vector, producto y residuo).

## 6. Varios tamaños y casos

Este criterio vale 10 puntos mañana. Lo que el programa resuelve:

| Caso | Cómo se prueba |
|---|---|
| Claves 2×2, 3×3 y 4×4 | Botones de tamaño en la página; `test_ida_y_vuelta_*` |
| Tres alfabetos: m = 26, 37 y 113 | Selector de alfabeto; `test_modulos`, `test_ida_y_vuelta_otros_alfabetos` |
| Imágenes, m = 256, de cualquier tamaño, en color o en gris | «Subir una imagen»; `test_ida_y_vuelta_gris`, `test_imagen_subida_y_bloque_elegido` |
| Mensajes que no son múltiplo de `n` | Relleno automático con X o espacio |
| Claves que no sirven | Se detectan y se explica el mcd; `test_clave_invalida`, `test_clave_sin_inversa` |
| Clave aleatoria válida | Botón «Clave aleatoria»; `test_clave_aleatoria` |
| Ataque con texto suficiente o insuficiente | `test_recupera_la_clave`, `test_error_explica_por_que_no_se_puede` |
| Textos muy repetitivos (el ataque no se cuelga) | `test_texto_repetitivo_no_se_cuelga` |

## 7. Pruebas automáticas

`tests/test_hill.py` tiene 35 pruebas en seis grupos:

| Grupo | Pruebas | Qué revisa |
|---|---|---|
| `TestAlfabetos` | 6 | Que los módulos sean 26, 37 y 113, que no haya símbolos repetidos y que las tildes se adapten bien |
| `TestCifrado` | 5 | HELP → HIAT, que cifrar y descifrar devuelva el original en los tres alfabetos y que se rechacen las claves inválidas |
| `TestAtaque` | 3 | Que se recupere la clave exacta, que se explique cuándo no se puede y que no se cuelgue |
| `TestImagenEncadenada` | 5 | Ida y vuelta en color y en gris, que bloques iguales den cifrados distintos al encadenar y el ejemplo de píxeles del informe |
| `TestResultados` | 2 | Que la fórmula de claves válidas coincida con contarlas una por una y que encadenar borre el parecido entre bloques vecinos (los números de la sección Resultados del reporte) |
| `TestAPI` | 14 | Cada ruta de la página web, con entradas válidas e inválidas |

Si alguien pregunta «¿cómo saben que funciona?», la respuesta es esta: el ejemplo a mano coincide, la inversa propia coincide con la de sympy y las 35 pruebas pasan.

## 8. Preguntas probables sobre el código

**¿Por qué programaron la inversa a mano si sympy ya la tiene?**
Para que el álgebra del curso esté en el código y no sea una caja negra. Usamos la misma fórmula de la adjunta y el resultado de sympy solo sirve para comprobar.

**¿Por qué sympy para el texto y numpy para las imágenes?**
sympy maneja enteros exactos de cualquier tamaño, ideal para pocas matrices. numpy es mucho más rápido para multiplicar millones de números, que es lo que hace falta con una foto.

**¿El determinante por cofactores no es lento?**
Para matrices grandes sí (crece como `n!`), pero las claves son de 2×2 a 4×4, así que es instantáneo. Lo elegimos porque es el método del curso.

**¿Por qué una página web y no solo el notebook?**
Para que la demo sea en vivo e interactiva: se cambia un número de la clave y se ve al instante si sirve, el resultado y el paso a paso. El notebook queda como documento con todas las cuentas.

**¿Qué pasa si el mensaje tiene emojis o saltos de línea?**
No están en ningún alfabeto: la página avisa cuáles se ignoran y cifra el resto.
