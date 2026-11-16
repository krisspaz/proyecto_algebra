---
title: "Guía 3 · El programa sin tecnicismos"
subtitle: "Qué hace, qué álgebra hay detrás y cómo explicarlo · Grupo 15"
---

## Para qué sirve esta guía

Para entender y explicar el programa **sin leer código**. No aparece Python, pero sí toda el álgebra, porque es lo que evalúa el curso. La idea es que cualquiera del grupo pueda pararse frente a la página web y decir qué está pasando y por qué.

Si te preguntan algo del código en sí, la respuesta corta está en la sección 7. La explicación completa está en la Guía 2.

## 1. El problema

Ana quiere mandarle a Beto un mensaje que nadie más pueda leer. Antes, en persona, acordaron un **secreto**: una matriz de números, la **clave** `K`. Con esa misma matriz Ana cifra y Beto descifra. Por eso se llama criptografía de **clave privada** (o simétrica): los dos tienen la misma clave.

Lester Hill propuso esto en 1929. Lo interesante para nosotros es que cifrar es literalmente lo que hicimos en el curso: **multiplicar una matriz por un vector**.

## 2. El programa de un vistazo

El programa es una página web con cinco partes, de arriba hacia abajo:

| Parte | Qué haces ahí | Qué álgebra hay |
|---|---|---|
| **Alfabeto** | Eliges qué símbolos se pueden cifrar | Define el módulo `m` |
| **Clave** | Escribes la matriz `K` (2×2, 3×3 o 4×4) | Determinante, mcd, inversa |
| **Mensaje** | Escribes el texto y ves el resultado al instante | `c = K · p (mod m)` |
| **Paso a paso** | Ves la cuenta de cada bloque | Producto matriz-vector y residuo |
| **Ataque** | Sacas la clave a partir de un trozo conocido | Sistema lineal `K = C · P⁻¹` |
| **Imágenes** | Cifras una foto y ves qué le pasa a cada píxel | Lo mismo, módulo 256 |

![La página con el ejemplo HELP → HIAT](entregas/presentacion/capturas/1_help_hiat.png)

## 3. Recorrido parte por parte

### 3.1 Alfabeto: convertir letras en números

Una matriz solo puede multiplicar números, así que primero cada símbolo se convierte en un número según su posición: **A = 0, B = 1, C = 2, …, Z = 25**.

El programa ofrece tres alfabetos:

| Alfabeto | Cuántos símbolos (m) | Para qué |
|---|---|---|
| Solo letras | 26 | El cifrado clásico, el de los libros |
| Letras, números y espacio | 37 | Mensajes con números, como «AULA 204» |
| Todo el teclado | 113 | Mensajes reales con mayúsculas, ñ, tildes y signos: `¿Nos vemos mañana?` |

El número de símbolos `m` es importante: todas las cuentas se hacen **módulo m**.

**¿Qué es «módulo»?** Es quedarse con el residuo de dividir entre `m`, como en un reloj. En un reloj de 12 horas, 15 horas después de las 12 son las 3, porque `15 = 12 + 3`. Módulo 26 pasa lo mismo: `33 ≡ 7` porque `33 = 26 + 7`. Así cualquier resultado vuelve a caer entre 0 y 25 y se puede convertir de nuevo en letra.

### 3.2 Clave: una matriz que se pueda «deshacer»

La clave es una matriz cuadrada `K`. Su tamaño `n` dice de cuántas letras es cada bloque: con 2×2 el mensaje se corta de 2 en 2, con 3×3 de 3 en 3.

Debajo de la matriz, el programa dice si **sirve o no**. Para descifrar hace falta la inversa `K⁻¹`. En los reales basta con `det K ≠ 0`, pero módulo 26 no se puede dividir entre cualquier número. La regla es:

> **La clave sirve si y solo si `mcd(det K, m) = 1`**, es decir, si el determinante y `m` no comparten ningún factor.

Con la clave del ejemplo:

- `K = [[3, 3], [2, 5]]`
- `det K = 3·5 − 3·2 = 9`
- `mcd(9, 26) = 1`, así que **sirve**.

Cuando la clave sirve, aparece su inversa `K⁻¹` debajo. Se calcula con la fórmula de la **adjunta** que vimos en clase, cambiando «dividir entre el determinante» por «multiplicar por el inverso modular del determinante»:

```
K⁻¹ = det(K)⁻¹ · adj(K)   (mod 26)
```

- El inverso de 9 módulo 26 es 3, porque `9 · 3 = 27 ≡ 1`.
- `adj(K) = [[5, −3], [−2, 3]]`.
- `K⁻¹ = 3 · [[5, −3], [−2, 3]] = [[15, −9], [−6, 9]] ≡ [[15, 17], [20, 9]]`.

**¿Cómo se encuentra el inverso de 9?** Con el algoritmo de Euclides, el mismo del mcd: `26 = 2·9 + 8`, `9 = 1·8 + 1`. Despejando hacia atrás, `1 = 9 − 8 = 9 − (26 − 2·9) = 3·9 − 26`. Entonces `3·9 ≡ 1 (mod 26)`.

#### Una clave que no sirve

![Clave inválida: la matriz se pone en rojo](entregas/presentacion/capturas/3_clave_invalida.png)

Con `K = [[2, 4], [6, 8]]`, la matriz se pone en rojo. El determinante es `−8`, que **no es cero**: en los reales esta matriz tendría inversa. Pero `−8 ≡ 18 (mod 26)` y `mcd(18, 26) = 2`, así que no sirve.

¿Por qué es un problema? Porque dos mensajes distintos terminarían cifrados igual. El vector `(13, 0)`, que es «NA», da `K · (13, 0) = (26, 78) ≡ (0, 0)`, que es «AA». Y «AA» también da `(0, 0)`. Si recibes «AA», no hay forma de saber cuál de los dos te mandaron. En términos del curso, **la transformación no es inyectiva**: un vector distinto de cero va a parar al cero.

### 3.3 Mensaje: cifrar y descifrar

Escribes el mensaje y el resultado aparece al instante en el recuadro amarillo. Con «HELP» y la clave de arriba sale **HIAT**.

- **Cifrar** es multiplicar cada bloque por `K`: `c = K · p (mod m)`.
- **Descifrar** es multiplicar por la inversa: `p = K⁻¹ · c (mod m)`. Funciona porque `K⁻¹ · K = I`, la identidad.

El botón **«Descifrar este resultado»** toma lo cifrado y lo descifra: vuelve exactamente el mensaje original.

Si al último bloque le faltan letras, se completa con X (o con espacios en los otros alfabetos). Así todos los bloques tienen `n` símbolos.

### 3.4 Paso a paso: la cuenta que hicimos a mano

Esta parte muestra la misma cuenta del pizarrón, bloque por bloque:

```
HE → p = (7, 4)     K · p = (3·7 + 3·4, 2·7 + 5·4) = (33, 34) ≡ (7, 8)   → HI
LP → p = (11, 15)   K · p = (3·11 + 3·15, 2·11 + 5·15) = (78, 97) ≡ (0, 19) → AT
```

Cada fila del resultado es el producto punto de una fila de `K` con el vector `p`. Después se reduce módulo 26 y se vuelve a convertir en letras.

### 3.5 Ataque: por qué este cifrado no es seguro

![El ataque recupera la clave](entregas/presentacion/capturas/5_ataque.png)

Supón que un espía no conoce la clave, pero sabe que el mensaje empezaba con «HELP» y ve que el cifrado empieza con «HIAT». Con eso le basta:

1. Pone los bloques conocidos como columnas de una matriz: `P = [[7, 11], [4, 15]]` (HE y LP) y `C = [[7, 0], [8, 19]]` (HI y AT).
2. Como cada columna cumple `c = K · p`, entonces `C = K · P`.
3. Si `P` tiene inversa módulo 26, despeja: **`K = C · P⁻¹`**.

La cuenta:

- `det P = 7·15 − 11·4 = 61 ≡ 9`, y `mcd(9, 26) = 1`, así que `P` tiene inversa.
- `P⁻¹ = 3 · [[15, −11], [−4, 7]] ≡ [[19, 19], [14, 21]]`.
- `K = C · P⁻¹ ≡ [[3, 3], [2, 5]]`. **Es la clave secreta.**

Romper el cifrado fue **resolver un sistema lineal**. En la página se hace con dos botones: «Usar el mensaje y el cifrado de arriba» y «Recuperar la clave». Con una clave `n×n` bastan `n²` letras conocidas: 4 con 2×2 y 9 con 3×3, siempre que formen una `P` invertible.

Esta es la lección del proyecto: **lo mismo que permite descifrar (que todo es lineal y se puede invertir) es lo que permite al espía sacar la clave.**

### 3.6 Imágenes: el mismo cifrado con fotos

![La sección de imágenes](entregas/presentacion/capturas/6_imagenes.png)

**Una imagen ya está hecha de números.** Cada píxel es un trío `(R, G, B)`: cuánto rojo, verde y azul tiene, de 0 a 255. Por ejemplo, `(255, 0, 0)` es rojo puro, `(0, 0, 0)` es negro y `(255, 255, 255)` es blanco. **No se usa ASCII.** ASCII sirve para convertir letras en números, y aquí ya tenemos números.

Entonces se hace lo mismo que con el texto:

- Se toman 3 píxeles seguidos de una fila (con clave 3×3).
- Para cada color por separado, se arma el vector de 3 números y se multiplica por `K`.
- Se trabaja **módulo 256**, para que el resultado vuelva a ser un color entre 0 y 255.

Como `256 = 2 · 2 · 2 · 2 · 2 · 2 · 2 · 2`, la regla `mcd(det K, 256) = 1` queda así: **la clave sirve si su determinante es impar.**

**Ejemplo real.** Tres píxeles del círculo rojo valen `(200, 40, 40)`. Con la clave `[[6, 24, 1], [13, 16, 10], [20, 17, 15]]` (determinante 441, impar):

| | Píxel 1 | Píxel 2 | Píxel 3 |
|---|---|---|---|
| Antes | (200, 40, 40) | (200, 40, 40) | (200, 40, 40) |
| Después | (56, 216, 216) | (120, 24, 24) | (160, 32, 32) |

Por ejemplo, el rojo nuevo del píxel 2 es `13·200 + 16·200 + 10·200 = 7800`, y `7800 ≡ 120 (mod 256)`.

![Qué le pasa a cada píxel](figuras/pixeles.png)

**La matriz cambia el color, no el lugar del píxel.** Cada píxel se queda en su fila y columna con otros colores. Y el rojo solo se mezcla con rojos: los colores no se mezclan entre sí.

#### Lo que se sigue viendo

![Original, cifrada y descifrada](figuras/imagen_sin_encadenar.png)

En la imagen cifrada **se siguen viendo las figuras**. El bloque de al lado del círculo también es `(200, 40, 40)` tres veces, así que sale exactamente igual. Bloques iguales dan cifrados iguales, y una zona de un solo color se convierte en un patrón repetido con la misma forma.

#### Encadenar los bloques

La solución es que cada bloque se mezcle con el anterior antes de cifrarse: `cᵢ = K · (pᵢ + cᵢ₋₁)`. Ahora dos bloques iguales casi nunca salen iguales, y la imagen queda como ruido. Al descifrar vuelve idéntica, píxel por píxel.

![Sin encadenar, encadenada y descifrada](figuras/imagen_encadenada.png)

Pero **sigue siendo lineal**: el espía que conozca unos píxeles puede sacar la clave igual que antes. Encadenar esconde el dibujo, no la clave.

## 4. Aplicaciones relevantes

1. **Mensajes reales.** Con «Todo el teclado» se cifra cualquier frase con signos, tildes y ñ.
2. **Fotos y cualquier archivo.** Una foto son números de 0 a 255, y cualquier archivo (PDF, audio) también, así que la misma idea sirve para cifrar archivos.
3. **Los cifrados de hoy.** AES, el estándar que protege WhatsApp, las páginas `https` y los bancos, tiene un paso que es exactamente multiplicar bloques de 4 bytes por una matriz 4×4. La diferencia es que lo combina con pasos **no lineales**, para que no funcione nuestro ataque.

## 5. Las cuatro ideas que hay que poder decir sin leer

1. **Cifrar es multiplicar una matriz por un vector:** `c = K · p (mod m)`.
2. **Descifrar es multiplicar por la inversa:** `p = K⁻¹ · c (mod m)`, con `K⁻¹ = det(K)⁻¹ · adj(K)`.
3. **La clave sirve solo si `mcd(det K, m) = 1`.** No basta con `det ≠ 0`, como en los reales.
4. **Como es lineal, se rompe resolviendo un sistema:** `K = C · P⁻¹`.

## 6. Qué tema del curso aparece en cada parte

| Tema del curso | Dónde aparece |
|---|---|
| Producto de matrices y matriz por vector | Cifrar y descifrar; el paso a paso |
| Determinante por cofactores | Decidir si la clave sirve |
| Matriz adjunta e inversa | Calcular `K⁻¹` para descifrar |
| Sistemas de ecuaciones lineales | El ataque: `C = K · P` |
| Transformaciones lineales e inyectividad | Por qué una clave con `mcd ≠ 1` no sirve («NA» y «AA» chocan) |
| Matriz identidad | `K⁻¹ · K = I`, por eso vuelve el mensaje |

## 7. Si te preguntan por el código

No hace falta saber programar para responder esto:

- **¿Qué hace Python y qué hace la página?** Python hace todas las cuentas. La página solo muestra los resultados y deja escribir el mensaje y la clave.
- **¿Usaron una función ya hecha para la inversa?** No. La programamos con la fórmula de la adjunta y el algoritmo de Euclides, como en clase. Usamos una librería solo para comprobar que diera lo mismo.
- **¿Qué librerías usaron?** Para guardar y multiplicar matrices (sympy), para procesar imágenes rápido (numpy y Pillow), para la página (Flask) y para las gráficas (matplotlib).
- **¿Cómo saben que funciona?** El ejemplo a mano HELP → HIAT coincide con el programa, nuestra inversa coincide con la de la librería y hay 35 pruebas automáticas que revisan todo y pasan.
- **¿Funciona con otros tamaños?** Sí: claves 2×2, 3×3 y 4×4, alfabetos de 26, 37 y 113 símbolos, e imágenes de cualquier tamaño.

## 8. Glosario

| Palabra | Qué significa |
|---|---|
| Cifrar / descifrar | Convertir el mensaje en algo ilegible / regresarlo a como era |
| Clave privada (simétrica) | La misma clave sirve para cifrar y descifrar, y la comparten los dos |
| Bloque | Grupo de `n` símbolos (o píxeles) que se cifra junto |
| Módulo `m` | Quedarse con el residuo de dividir entre `m` |
| `a ≡ b (mod m)` | `a` y `b` dejan el mismo residuo al dividir entre `m` |
| Inverso modular | El número que multiplicado por `a` da 1 módulo `m` (el de 9 es 3) |
| mcd | Máximo común divisor |
| Adjunta | Traspuesta de la matriz de cofactores; sirve para la inversa |
| Texto plano conocido | Un trozo del mensaje original que el espía conoce |
| RGB | Rojo, verde y azul: los tres números de cada píxel |
| Encadenar | Mezclar cada bloque con el cifrado anterior para que bloques iguales no salgan iguales |
