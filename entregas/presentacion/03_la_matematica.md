# La matemática detrás del cifrado

Esta es la parte que más pesa en un curso de Álgebra Lineal. Todo sale de tres ideas: el **inverso modular**, la **adjunta** y el **determinante**.

## 1. Aritmética módulo 26

Trabajamos con los números `{0, 1, …, 25}` y después de cada suma o producto nos quedamos con el residuo de dividir entre 26. Ahí se puede sumar, restar y multiplicar sin problema. **Dividir no siempre se puede.**

En los reales, «dividir entre 9» es multiplicar por `1/9`. Módulo 26 no hay fracciones, así que necesitamos un número entero que haga el papel de `1/9`: el que multiplicado por 9 dé 1. Ese número se llama **inverso modular**:

```
a · a⁻¹ ≡ 1   (mod 26)
```

Ejemplo: `9 · 3 = 27 = 26 + 1 ≡ 1`, así que **`9⁻¹ ≡ 3`** módulo 26.

## 2. ¿Cuándo existe el inverso modular?

**Regla:** `a` tiene inverso módulo `m` si y solo si `mcd(a, m) = 1`, es decir, si `a` y `m` no comparten factores.

- **Por qué sí cuando el mcd es 1:** se pueden encontrar enteros `x`, `y` con `a·x + m·y = 1` (identidad de Bézout). Al reducir módulo `m`, el término `m·y` desaparece y queda `a·x ≡ 1`. Ese `x` es el inverso.
- **Por qué no cuando el mcd es `d > 1`:** `a·x` es múltiplo de `d` y `m` también, así que `a·x mod m` sigue siendo múltiplo de `d` y nunca puede valer 1.

Como `26 = 2 · 13`, tienen inverso los números que **no son pares ni múltiplos de 13**. Son 12:

| a   | 1 | 3 | 5  | 7  | 9 | 11 | 15 | 17 | 19 | 21 | 23 | 25 |
|-----|---|---|----|----|---|----|----|----|----|----|----|----|
| a⁻¹ | 1 | 9 | 21 | 15 | 3 | 19 | 7  | 23 | 11 | 5  | 17 | 25 |

### Cómo se calcula: algoritmo de Euclides extendido

Ejemplo con `9` módulo `26`. Se divide hasta llegar a residuo 1:

```
26 = 2 · 9 + 8
 9 = 1 · 8 + 1
```

Y luego se despeja el 1 hacia atrás:

```
1 = 9 − 8
  = 9 − (26 − 2·9)
  = 3·9 − 26
```

Módulo 26 el `−26` desaparece y queda `1 ≡ 3·9`, así que `9⁻¹ = 3`. Esto es lo que hace la función `inverso_modular` de nuestro programa (`inversa.py`).

## 3. La inversa de la clave

Para cualquier matriz cuadrada se cumple:

```
K · adj(K) = det(K) · I
```

donde `adj(K)` es la **adjunta** (la traspuesta de la matriz de cofactores). Esa igualdad solo usa sumas y productos, así que también vale módulo 26. Si `det(K)` tiene inverso modular, multiplicamos los dos lados por él:

```
K⁻¹ = det(K)⁻¹ · adj(K)   (mod 26)
```

Es la misma fórmula del curso, `K⁻¹ = (1/det K) · adj(K)`, cambiando «dividir entre el determinante» por «multiplicar por el inverso modular del determinante».

### Ejemplo: K = [[3, 3], [2, 5]]

1. **Determinante:** `det K = 3·5 − 3·2 = 9`.
2. **¿Tiene inverso?** `mcd(9, 26) = 1` → sí, y `9⁻¹ ≡ 3`.
3. **Adjunta de una 2×2:** se intercambia la diagonal y se cambia el signo de la otra:
   ```
   adj | a  b |  =  |  d  −b |      adj | 3  3 |  =  |  5  −3 |
       | c  d |     | −c   a |          | 2  5 |     | −2   3 |
   ```
4. **Inversa:**
   ```
   K⁻¹ = 3 · |  5  −3 |  =  | 15  −9 |  ≡  | 15  17 |   (mod 26)
             | −2   3 |     | −6   9 |     | 20   9 |
   ```
   (Los negativos se pasan a positivo sumando 26: `−9 + 26 = 17`, `−6 + 26 = 20`.)
5. **Comprobación:** `K · K⁻¹ = [[105, 78], [130, 79]] ≡ [[1, 0], [0, 1]]` ✓

Con claves 3×3 o 4×4 es igual, solo que la adjunta se calcula con cofactores. Nuestro programa lo hace **a mano** en `inversa.py` (determinante por cofactores, adjunta e inverso modular), sin usar funciones ya hechas. Solo usa la librería SymPy para comprobar que el resultado coincide.

## 4. ¿Cuándo sirve una matriz como clave?

**Teorema:** `K` tiene inversa módulo 26 si y solo si `mcd(det K, 26) = 1`.

- **Si el mcd es 1:** `det(K)⁻¹` existe y la fórmula de arriba da la inversa.
- **Si `K` tiene inversa:** `K · K⁻¹ = I`, y tomando determinantes `det(K) · det(K⁻¹) ≡ 1`. O sea, `det(K)` tiene inverso modular, y por la regla de la sección 2 su mcd con 26 es 1.

### La diferencia con los reales

En los reales basta con `det ≠ 0`. **Módulo 26 no basta.**

Contraejemplo: `K = [[2, 4], [6, 8]]`

- `det K = 2·8 − 4·6 = −8`, que no es cero.
- Pero `−8 ≡ 18 (mod 26)` y `mcd(18, 26) = 2`, así que no tiene inverso.
- Qué pasa en la práctica: `K · (13, 0) = (26, 78) ≡ (0, 0)`. Es decir, **"NA" se cifra igual que "AA"** (las dos dan "AA"). Si dos mensajes distintos dan el mismo cifrado, nadie puede saber cuál era el original. La clave no sirve.

Nuestro programa revisa esto antes de cifrar y rechaza las claves que no cumplen.

### ¿Cuántas claves sirven?

Con matrices 2×2 hay `26⁴ = 456 976` matrices posibles, pero solo **157 248** sirven como clave (alrededor de un tercio).

### Por qué usamos módulos primos (37 y 113)

Si `m` es primo, el único factor que podría compartir con el determinante es el mismo `m`. Entonces la regla queda casi igual que en los reales: la clave sirve si `det K` no es múltiplo de `m`. Por eso, con 37 o 113 símbolos casi cualquier matriz al azar es una buena clave.

Una clave puede servir en un alfabeto y no en otro. Por ejemplo, `det K = 52` sirve módulo 37 (`52 ≡ 15`), pero no módulo 26 (`52 ≡ 0`).

## Resumen para una diapositiva

| En los reales | Módulo 26 |
|---|---|
| Dividir entre `a` = multiplicar por `1/a` | Multiplicar por `a⁻¹`, el inverso modular |
| `a` tiene inverso si `a ≠ 0` | `a` tiene inverso si `mcd(a, 26) = 1` |
| `K⁻¹ = (1/det K) · adj(K)` | `K⁻¹ = det(K)⁻¹ · adj(K) mod 26` |
| `K` invertible si `det K ≠ 0` | `K` invertible si `mcd(det K, 26) = 1` |
