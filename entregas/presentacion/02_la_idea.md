# La idea del cifrado de Hill

## El problema

Dos personas quieren mandarse mensajes que nadie más pueda leer. Se ponen de acuerdo antes en una **clave secreta**, y la misma clave sirve para cifrar y para descifrar. Esto se llama criptografía de **clave privada** (o simétrica). En la de **clave pública** (como RSA) cada persona tiene dos claves distintas, una para cifrar y otra para descifrar. Nuestro proyecto es de clave privada.

Lester S. Hill publicó este método en 1929. Fue de los primeros cifrados basados en álgebra lineal: **la clave es una matriz**.

## Paso 1: de letras a números

Cada letra se cambia por su posición, empezando en cero:

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T | U | V | W | X | Y | Z |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |

## Paso 2: cortar en bloques

Con una clave de 2×2, el mensaje se corta en bloques de 2 letras, y cada bloque se ve como un **vector columna**:

```
HELP  →  HE | LP  →  (7, 4) | (11, 15)
```

Si sobra una letra al final, se completa con X.

## Paso 3: multiplicar por la clave, módulo 26

```
c = K · p   (mod 26)
```

**Módulo 26** quiere decir que, después de multiplicar, nos quedamos con el **residuo de dividir entre 26**. Es como un reloj de 26 horas: después del 25 viene otra vez el 0. Así cada número vuelve a quedar entre 0 y 25, que es otra letra.

Ejemplos: `33 mod 26 = 7` · `78 mod 26 = 0` · `97 mod 26 = 19` (porque `97 = 3·26 + 19`).

## Ejemplo completo: HELP → HIAT

Clave:

```
K = | 3  3 |
    | 2  5 |
```

**Bloque HE = (7, 4):**

```
| 3  3 | · | 7 |  =  | 3·7 + 3·4 |  =  | 33 |  ≡  | 7 |  → H
| 2  5 |   | 4 |     | 2·7 + 5·4 |     | 34 |     | 8 |  → I
```

**Bloque LP = (11, 15):**

```
| 3  3 | · | 11 |  =  | 3·11 + 3·15 |  =  | 78 |  ≡  |  0 |  → A
| 2  5 |   | 15 |     | 2·11 + 5·15 |     | 97 |     | 19 |  → T
```

**Resultado: HELP se cifra como HIAT.**

Detalles para comentar:

- La misma letra no siempre se cifra igual. En HELP no hay letras repetidas, pero en otros mensajes una misma letra cambia según la letra con la que comparte bloque. Eso hace a Hill más difícil de romper que un cifrado de sustitución simple (como el de César), donde se pueden contar letras.
- Cada letra cifrada depende de **las dos** letras del bloque, porque cada fila de la matriz las mezcla.

## Paso 4: descifrar

Para volver al mensaje original se multiplica por la **inversa** de la clave:

```
p = K⁻¹ · c   (mod 26)
```

Para esta clave, `K⁻¹ = [[15, 17], [20, 9]]` (en `03_la_matematica.md` está cómo se calcula).

```
HI = (7, 8):   K⁻¹ · (7, 8)  = (15·7 + 17·8, 20·7 + 9·8)  = (241, 212) ≡ (7, 4)   → HE ✓
AT = (0, 19):  K⁻¹ · (0, 19) = (17·19, 9·19)               = (323, 171) ≡ (11, 15) → LP ✓
```

## Claves más grandes y otros alfabetos

- La clave puede ser 3×3, 4×4, etc. Con 3×3 los bloques son de 3 letras. Mientras más grande, más mezcla, pero la idea es la misma.
- No hace falta usar solo 26 letras. Con un alfabeto de `m` símbolos todo se hace módulo `m`. Nuestro programa tiene tres alfabetos:
  - **Solo letras:** 26 símbolos, módulo 26.
  - **Letras, números y espacio:** 37 símbolos, módulo 37.
  - **Todo el teclado:** 113 símbolos, con signos, minúsculas, tildes, ñ, ¿ ¡ € °, módulo 113.
- 37 y 113 son números **primos**, y eso se eligió a propósito: con un módulo primo casi cualquier matriz sirve como clave (ver `03_la_matematica.md`).
