# Cómo se rompe el cifrado y qué pasa con imágenes

## 1. Ataque de texto plano conocido

**La situación:** un espía no tiene la clave, pero conoce un pedazo del mensaje original y su versión cifrada. Pasa en la vida real: muchos mensajes empiezan igual («Estimados…», la fecha, un saludo).

**La idea:** cada bloque cumple `c = K · p`. Si se ponen varios bloques conocidos como columnas de una matriz `P` y sus cifrados como columnas de `C`, todos juntos cumplen:

```
C = K · P   (mod 26)
```

Si `P` tiene inversa módulo 26, se despeja la clave:

```
K = C · P⁻¹   (mod 26)
```

**Romper el cifrado es resolver un sistema lineal.** No hace falta probar claves una por una.

### Ejemplo a mano: recuperar la clave de HELP → HIAT

El espía sabe que "HELP" se cifró como "HIAT", pero no conoce `K`.

1. **Matrices con los bloques como columnas:**
   ```
   P = | 7  11 |   (HE, LP)        C = | 7   0 |   (HI, AT)
       | 4  15 |                       | 8  19 |
   ```
2. **¿P tiene inversa?** `det P = 7·15 − 11·4 = 61 ≡ 9`, y `mcd(9, 26) = 1` → sí. `9⁻¹ ≡ 3`.
3. **Inversa de P:**
   ```
   P⁻¹ = 3 · | 15  −11 |  =  |  45  −33 |  ≡  | 19  19 |
             | −4    7 |     | −12   21 |     | 14  21 |
   ```
4. **La clave:**
   ```
   K = C · P⁻¹ = | 7   0 | · | 19  19 |  =  | 133  133 |  ≡  | 3  3 |
                 | 8  19 |   | 14  21 |     | 418  551 |     | 2  5 |
   ```

**Sale exactamente la clave original, `[[3, 3], [2, 5]]`, con solo 4 letras conocidas.**

### ¿Cuántas letras necesita el espía?

Con una clave `n×n` necesita `n` bloques, o sea `n²` letras: 4 para una clave 2×2 y **9 para una 3×3**. Además, esos bloques tienen que formar una matriz `P` invertible (con `mcd(det P, 26) = 1`). Si no, prueba con otra combinación de bloques.

En la demo del programa (`demo.py`) el espía conoce el inicio de «ATAQUEN AL AMANECER POR EL FLANCO NORTE». Con 5 bloques no le alcanza, porque ninguna combinación da una `P` invertible. Con 6 bloques («ATAQUENALAMANECERPOR») sí, y recupera la clave 3×3 exacta.

### La conclusión importante

> La misma propiedad que permite descifrar (que todo es lineal e invertible) es la que permite romper el cifrado. **La linealidad es su fortaleza matemática y su debilidad criptográfica.**

## 2. Cifrar imágenes (módulo 256)

Una imagen digital es una **matriz de píxeles**. Cada píxel tiene tres canales (rojo, verde, azul) con valores de 0 a 255. Por eso se puede usar el mismo método **módulo 256**: se agrupan píxeles vecinos de 3 en 3, cada grupo es un vector y se multiplica por la clave.

### Cómo se codifica una imagen (la catedrática lo preguntó)

- **No se usa ASCII.** ASCII convierte letras en números, pero una imagen *ya son números*: cada píxel es un trío `(R, G, B)` que dice cuánto rojo, verde y azul tiene, de 0 a 255. `(255, 0, 0)` es rojo puro, `(0, 0, 0)` negro, `(255, 255, 255)` blanco.
- **Cada canal se cifra por separado.** Se toman 3 píxeles seguidos de una fila y se arma el vector de sus rojos, el de sus verdes y el de sus azules. Cada vector se multiplica por `K` y se reduce módulo 256 (para que el resultado vuelva a ser un color de 0 a 255).
- **La matriz cambia el color, no el lugar del píxel.** Cada píxel cifrado sigue en la misma fila y columna, pero con otro color. Cada valor nuevo mezcla los 3 píxeles del bloque en ese canal; el rojo solo se mezcla con rojos.

**Ejemplo con la clave del programa** `K = [[6, 24, 1], [13, 16, 10], [20, 17, 15]]` (det = 441, impar). Tres píxeles del círculo rojo, los tres `(200, 40, 40)`:

```
Rojos:            K · (200, 200, 200) = (6200, 7800, 10400) ≡ (56, 120, 160)   (mod 256)
Verdes y azules:  K · (40, 40, 40)    = (1240, 1560, 2080)  ≡ (216, 24, 32)
```

| | píxel 1 | píxel 2 | píxel 3 |
|---|---|---|---|
| Original | (200, 40, 40) | (200, 40, 40) | (200, 40, 40) |
| Cifrado | (56, 216, 216) | (120, 24, 24) | (160, 32, 32) |

Tres píxeles iguales salen de tres colores distintos. Pero el bloque de al lado también es `(200, 40, 40)` tres veces, así que sale **otra vez igual**. Eso es lo que se ve abajo. Figura: `figuras/pixeles.png`.

**Regla de la clave:** `256 = 2⁸`, así que el único factor es 2. Por el teorema de `03_la_matematica.md`, la clave sirve si y solo si **`det K` es impar**.

### Lo que se observa (figura `figuras/imagen_sin_encadenar.png`)

La imagen cifrada cambia los colores, pero **las figuras se siguen viendo**. ¿Por qué? Una zona de un solo color tiene todos los bloques iguales, y bloques iguales dan cifrados iguales. El cifrado esconde los colores, pero no la forma.

### La solución: encadenar bloques (figura `figuras/imagen_encadenada.png`)

Antes de multiplicar, a cada bloque se le suma el cifrado del bloque anterior:

```
c_i = K · (p_i + c_{i−1})   (mod 256)
```

Así dos bloques iguales casi nunca dan el mismo cifrado, porque cada uno arrastra lo que pasó antes. La imagen cifrada se ve como ruido. Para descifrar se despeja, usando la misma inversa de siempre:

```
p_i = K⁻¹ · c_i − c_{i−1}   (mod 256)
```

Es la misma idea que el modo **CBC** de los cifrados modernos.

### Pero ojo: sigue siendo débil

Encadenar esconde las figuras, pero **no protege la clave**. El cifrado sigue siendo lineal: si el espía conoce unos píxeles originales, conoce también los cifrados anteriores (los puede ver), y despeja `K` igual que antes. En el notebook (sección 7) se recupera la clave exacta con unos pocos píxeles.

Para que un cifrado sea seguro de verdad hacen falta **pasos no lineales**. Por eso AES, el estándar actual, combina multiplicaciones de matrices con tablas de sustitución no lineales (S-boxes).
