# Cifrado de Hill: álgebra lineal aplicada a la criptografía

## 1. Idea general

El cifrado de Hill (Lester Hill, 1929) es un cifrado de clave privada por bloques. Cada letra se convierte en un número (A=0, B=1, …, Z=25), el mensaje se corta en bloques de `n` letras y cada bloque, visto como vector columna `p`, se transforma con una matriz clave `K` de tamaño `n×n`:

```
c = K · p   (mod 26)
```

Para descifrar se usa la inversa de la clave:

```
p = K⁻¹ · c   (mod 26)
```

Todo el cifrado es una transformación lineal sobre los enteros módulo 26. Eso lo hace elegante y también, como se verá, lo hace débil.

## 2. Fundamento teórico

### 2.1 Aritmética módulo 26

Trabajamos en `Z₂₆ = {0, 1, …, 25}`, donde sumas y productos se reducen módulo 26. Ahí se puede sumar, restar y multiplicar, pero **no siempre dividir**: dividir entre `a` significa multiplicar por su inverso modular `a⁻¹`, el número que cumple

```
a · a⁻¹ ≡ 1   (mod 26)
```

### 2.2 Cuándo existe el inverso modular

**Teorema.** `a` tiene inverso módulo `m` si y solo si `mcd(a, m) = 1`.

- *Si `mcd(a, m) = 1`*: por la identidad de Bézout existen enteros `x`, `y` con `a·x + m·y = 1`. Reduciendo módulo `m` queda `a·x ≡ 1`, así que `x` es el inverso. El algoritmo de Euclides extendido lo calcula.
- *Si `mcd(a, m) = d > 1`*: `a·x` siempre es múltiplo de `d`, y `m` también, así que `a·x mod m` es múltiplo de `d` y nunca puede valer 1.

Como `26 = 2 · 13`, los números invertibles módulo 26 son los que no son pares ni múltiplos de 13. Son 12 (`φ(26) = 12`):

| a   | 1 | 3 | 5  | 7  | 9 | 11 | 15 | 17 | 19 | 21 | 23 | 25 |
|-----|---|---|----|----|---|----|----|----|----|----|----|----|
| a⁻¹ | 1 | 9 | 21 | 15 | 3 | 19 | 7  | 23 | 11 | 5  | 17 | 25 |

### 2.3 Inversa de una matriz módulo 26

Sobre los enteros se cumple `K · adj(K) = det(K) · I`, donde `adj(K)` es la matriz adjunta (traspuesta de los cofactores). Como esa igualdad solo usa sumas y productos, sigue siendo cierta módulo 26. Si `det(K)` tiene inverso modular, multiplicamos ambos lados por él:

```
K⁻¹ = det(K)⁻¹ · adj(K)   (mod 26)
```

### 2.4 Por qué la clave debe cumplir mcd(det K, 26) = 1

**Teorema.** `K` es invertible módulo 26 si y solo si `mcd(det K, 26) = 1`.

- *Suficiente*: si el mcd es 1, `det(K)⁻¹` existe y la fórmula de 2.3 da la inversa.
- *Necesario*: si `K·K⁻¹ ≡ I`, tomando determinantes `det(K)·det(K⁻¹) ≡ 1`, así que `det(K)` tiene inverso y, por 2.2, `mcd(det K, 26) = 1`.

Ojo: en los reales basta con `det(K) ≠ 0`, pero aquí **no**. Ejemplo: `K = [[2, 4], [6, 8]]` tiene `det = -8 ≢ 0`, pero `-8 ≡ 18` y `mcd(18, 26) = 2`. Esa clave no es inyectiva: `K · (13, 0)ᵀ = (26, 78) ≡ (0, 0)`, así que "NA" y "AA" se cifran igual y es imposible saber cuál fue el mensaje. El programa rechaza esta clave (`hill.validar_clave`).

Para matrices 2×2 hay 26⁴ = 456 976 matrices posibles, de las cuales solo **157 248** son claves válidas.

### 2.5 Ejemplo resuelto (2×2)

Clave `K = [[3, 3], [2, 5]]`, mensaje "HELP".

1. `det(K) = 3·5 − 3·2 = 9`, `mcd(9, 26) = 1` → clave válida.
2. Bloques: `HE = (7, 4)`, `LP = (11, 15)`.
3. Cifrado:
   - `K·(7, 4) = (33, 34) ≡ (7, 8)` → "HI"
   - `K·(11, 15) = (78, 97) ≡ (0, 19)` → "AT"
   - Resultado: **"HIAT"**.
4. Inversa: `9⁻¹ ≡ 3` (porque `27 ≡ 1`), `adj(K) = [[5, −3], [−2, 3]]`, entonces `K⁻¹ = 3·adj(K) = [[15, −9], [−6, 9]] ≡ [[15, 17], [20, 9]]`.
5. Comprobación: `K⁻¹·(7, 8) = (241, 212) ≡ (7, 4)` → "HE". ✓

### 2.6 Otros alfabetos: módulos 37 y 113

El método no depende de usar 26 letras: con un alfabeto de `m` símbolos todo se hace módulo `m` y la clave sirve si `mcd(det K, m) = 1`. El programa ofrece tres:

| Alfabeto | Símbolos | m | Factores de m | La clave sirve si… |
|---|---|---|---|---|
| Solo letras | A–Z | 26 | 2 · 13 | det no es par ni múltiplo de 13 |
| Letras, números y espacio | A–Z, 0–9, espacio | 37 | primo | det no es múltiplo de 37 |
| Todo el teclado | los 95 caracteres imprimibles del teclado (espacio, signos, dígitos, mayúsculas, minúsculas), más ¡ ¿ Á É Í Ó Ú Ü Ñ á é í ó ú ü ñ € ° | 113 | primo | det no es múltiplo de 113 |

Los dos alfabetos grandes se eligieron con un número **primo** de símbolos a propósito. Si `m` es primo, `Z_m` es un cuerpo (todo número distinto de 0 tiene inverso) y la regla queda casi igual que en los reales: basta `det K ≢ 0 (mod m)`. Además, casi cualquier matriz al azar sirve como clave, mientras que módulo 26 solo lo hace un tercio de ellas (157 248 de 456 976 en el caso 2×2).

Con "Todo el teclado" el mensaje se cifra tal cual, con signos, mayúsculas y tildes, y el texto cifrado también puede contener cualquiera de esos símbolos. Solo quedan fuera los caracteres que no están en la lista (emojis, saltos de línea), y la interfaz avisa cuáles son.

Una clave válida en un alfabeto puede no serlo en otro. Por ejemplo, `det K = 52` sirve módulo 37 (`52 ≡ 15`) pero no módulo 26 (`52 ≡ 0`). Las claves de ejemplo de la interfaz se eligieron para que sirvan en los tres.

En los alfabetos que tienen espacio, el último bloque se completa con espacios en lugar de X, para que el texto descifrado se vea igual que el original.

## 3. Implementación

| Archivo | Contenido |
|---|---|
| `hill.py` | Conversión texto ↔ números, validación de la clave, cifrado y descifrado de texto. Tres alfabetos (mod 26, 37 y 113). Si el mensaje no es múltiplo de `n` se rellena con "X" o con espacios. |
| `inversa.py` | Inverso modular (Euclides extendido), determinante por cofactores, adjunta e inversa módulo m, hechos a mano. |
| `ataque.py` | Ataque de texto plano conocido, con un límite de intentos para textos muy repetitivos. |
| `imagen.py` | Cifrado de imágenes por bloques de píxeles (mod 256). |
| `app.py`, `templates/`, `static/` | Interfaz web: escribir el mensaje, editar la clave, ver el resultado y el paso a paso al instante, y lanzar el ataque. Python hace todos los cálculos; el navegador solo los muestra. |
| `tests/` | 23 pruebas automáticas del cifrado, el ataque y la API. |
| `demo.py`, `demo_imagen.py` | Demostraciones ejecutables. |

El determinante y la inversa módulo m están programados a mano en `inversa.py` con la fórmula de 2.3; `sympy` solo se usa para guardar las matrices y multiplicarlas, y como comprobación (`python inversa.py` compara ambos resultados). Para imágenes se usa `numpy`, porque hay que multiplicar cientos de miles de bloques.

## 4. Ataque de texto plano conocido

Si un atacante conoce `n` bloques de texto plano y sus cifrados, los coloca como columnas de matrices `P` y `C`. Como cada columna cumple `c = K·p`:

```
C = K · P   ⇒   K = C · P⁻¹   (mod 26)
```

siempre que `P` sea invertible módulo 26 (mismo criterio de 2.4). Recuperar la clave se reduce a **resolver un sistema lineal**: con una clave 3×3 bastan 9 letras conocidas en posiciones adecuadas.

En `demo.py` el atacante conoce el inicio del mensaje "ATAQUEN AL AMANECER POR…". Con los primeros 5 bloques no alcanza (ninguna terna de bloques da una `P` invertible módulo 26), pero con 6 bloques (`ATAQUENALAMANECERPOR`) sí, y recupera la clave exacta. `ataque.recuperar_clave` prueba combinaciones de bloques hasta encontrar una invertible.

## 5. Extensión: cifrado de imágenes (mod 256)

Una imagen digital es una matriz de píxeles con valores de 0 a 255 por canal. La misma idea funciona cambiando el módulo a 256: cada canal se recorre por filas, se agrupan `n` píxeles horizontales consecutivos en un vector y se aplica `c = K·p (mod 256)`.

Como `256 = 2⁸`, el único factor primo es 2, y por el teorema de 2.4 **la clave es válida si y solo si `det(K)` es impar**. La clave 3×3 del demo de texto tiene `det = 441`, así que sirve para ambos.

Si el ancho no es múltiplo de `n`, se añaden columnas negras a la derecha; al descifrar se recortan.

Ejecutar `python demo_imagen.py` genera `salida/original.png`, `salida/cifrada.png` y `salida/descifrada.png`. La imagen descifrada coincide píxel a píxel con la original.

**Resultado clave:** en la imagen cifrada **se siguen distinguiendo las figuras**. Una zona de color uniforme produce siempre el mismo bloque y, por tanto, el mismo bloque cifrado: el cifrado cambia los colores, pero no oculta la estructura. Es el mismo problema del modo ECB en cifrados modernos.

## 6. Conclusiones

1. El cifrado de Hill es una aplicación directa del álgebra lineal: cifrar es multiplicar por una matriz, descifrar es multiplicar por la inversa.
2. La condición de invertibilidad cambia respecto a los reales: no basta `det ≠ 0`, se necesita `mcd(det, m) = 1`.
3. Su linealidad lo hace vulnerable: con `n²` letras conocidas la clave se obtiene resolviendo un sistema.
4. Es determinista por bloques: bloques iguales dan cifrados iguales, lo que filtra patrones (muy visible en imágenes).
5. Por eso los cifrados modernos (AES) combinan pasos lineales con pasos **no lineales** (S-boxes) y usan modos de operación que encadenan bloques.

## 7. Guion de presentación (≈10 min)

1. **Problema** (1 min): enviar un mensaje que solo el receptor pueda leer; clave compartida.
2. **Idea de Hill** (2 min): letras → números → bloques → `c = K·p mod 26`. Ejemplo "HELP" → "HIAT" en la pizarra.
3. **La matemática** (3 min): inverso modular, `mcd(det, 26) = 1`, contraejemplo `[[2,4],[6,8]]` ("NA" y "AA" chocan).
4. **Demo en vivo** (2 min): abrir la interfaz (`python app.py`), cifrar un mensaje con signos y tildes en «Todo el teclado», pulsar «Descifrar este resultado», cambiar una casilla de la clave hasta que deje de servir. Al final, en la sección «Ataque», pulsar «Usar el mensaje y el cifrado de arriba» y «Recuperar la clave».
5. **Imágenes** (1 min): mostrar `salida/original.png` junto a `salida/cifrada.png`; se ven las figuras.
6. **Conclusión** (1 min): la linealidad es la fortaleza matemática y la debilidad criptográfica.
