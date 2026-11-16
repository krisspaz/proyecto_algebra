# Guion de la presentación (≈12 minutos)

La presentación es el **lunes 16 de noviembre**. La catedrática mandó la rúbrica el 15/11: **60 % presentación y 40 % Python**, con diez criterios de 10 puntos cada uno. Este guion los cubre todos, y al lado de cada parte dice qué criterio cubre.

| Presentación (60 %) | Python (40 %) |
|---|---|
| Aplicación relevante · Tiempo · Participación de integrantes · Teoría · Resultados · Conclusiones relevantes | Presentación del Python · Resuelve varios tamaños o casos · Uso de librerías y funciones propias · Organización del código |

**Participación:** se califica la participación de los integrantes, así que **hablan los cuatro**. El reparto de abajo es una sugerencia: cada quien presenta lo que mejor conoce. Lo importante es que cada uno pueda responder preguntas de su parte.

**Tiempo:** no dieron la duración. El guion dura unos 12 minutos. Si piden 10, recorten la parte 5 a la mitad (solo imágenes, sin encadenar). Si piden menos, recorten también la demo a los pasos 1, 3 y 5.

| Parte | Quién | Min | Criterio de la rúbrica |
|---|---|---|---|
| 1. El problema y para qué sirve | Rosemary | 1.5 | Aplicación relevante |
| 2. La idea de Hill | Rosemary | 1.5 | Teoría |
| 3. La matemática | Luis | 3 | Teoría |
| 4. El programa en Python y la demo | Kris | 3 | Los cuatro criterios de Python |
| 5. Resultados: el ataque y las imágenes | Milton | 2 | Resultados |
| 6. Conclusiones | Luis | 1 | Conclusiones relevantes |

---

## Parte 1 · El problema y para qué sirve (1.5 min) · Rosemary

**Diapositiva 1. Portada:** «Cifrado de Hill. Matrices aplicadas a la criptografía de clave privada». Grupo 15, los cuatro nombres.

**Diapositiva 2. Criptografía de clave privada:** el emisor y el receptor comparten la misma **clave secreta** para cifrar y descifrar. En el cifrado de Hill (Lester S. Hill, 1929) la clave es una matriz.

**Diapositiva 3. Aplicaciones.** La rúbrica evalúa «aplicación relevante» y la catedrática dijo que a varios grupos les falta:

1. **Mensajes reales** con mayúsculas, ñ, tildes y signos: `¿Nos vemos mañana? Aula #204, a las 9:30 (¡no faltes!)`.
2. **Fotos y cualquier archivo:** una foto son números de 0 a 255, y cualquier archivo (PDF, audio) también. Con el mismo método se cifran.
3. **Los cifrados de hoy:** AES, que protege WhatsApp, las páginas `https` y los bancos, tiene un paso (*MixColumns*) que es multiplicar bloques de 4 bytes por una matriz 4×4: la idea de Hill. AES lo combina con pasos no lineales, y en la parte 5 veremos por qué.

Qué decir:
> El programa cifra texto e imágenes. AES se menciona como ejemplo de un cifrado actual que también multiplica por matrices.

## Parte 2 · La idea de Hill (1.5 min) · Rosemary

Detalle completo en `02_la_idea.md`.

**Diapositiva 4. Conversión de letras a números:** A=0, B=1, …, Z=25. El mensaje se corta en bloques de 2 letras y cada bloque es un vector. Cifrar es multiplicar:

```
c = K · p   (mod 26)
```

**Diapositiva 5. Ejemplo: cifrado de HELP:** hacerlo paso a paso (en la pizarra si se puede):

- Clave `K = [[3, 3], [2, 5]]`
- `HE = (7, 4)` → `K · (7, 4) = (33, 34) ≡ (7, 8)` → **HI**
- `LP = (11, 15)` → `K · (11, 15) = (78, 97) ≡ (0, 19)` → **AT**

Qué decir:
> Módulo 26 significa tomar el residuo de dividir entre 26. Así cada resultado queda entre 0 y 25 y corresponde a una letra.

## Parte 3 · La matemática (3 min) · Luis

Detalle completo en `03_la_matematica.md`. Es la parte central de la nota de teoría.

**Diapositiva 6. Descifrado con la matriz inversa:**

```
p = K⁻¹ · c   (mod 26)
K⁻¹ = det(K)⁻¹ · adj(K)   (mod 26)
```

Para nuestra clave: `det K = 9`, `9⁻¹ ≡ 3` (porque `9 · 3 = 27 ≡ 1`), y queda `K⁻¹ = [[15, 17], [20, 9]]`. Comprobar: `K⁻¹ · (7, 8) ≡ (7, 4)` → HE.

**Diapositiva 7. Condición para que una clave sea válida:**

> En los reales una matriz tiene inversa si `det ≠ 0`. Módulo 26 no basta: hace falta `mcd(det K, 26) = 1`.

**Diapositiva 8. Ejemplo de clave inválida:** `K = [[2, 4], [6, 8]]` tiene `det = −8 ≠ 0`, pero `−8 ≡ 18` y `mcd(18, 26) = 2`. Con esa clave, "NA" y "AA" se cifran igual, así que nadie podría descifrar. La transformación no es inyectiva.

**Diapositiva 9. Alfabetos y módulos:** con 37 símbolos (letras, números y espacio) o 113 (todo el teclado) todo se hace módulo 37 o 113. Son primos, así que basta con que `det K` no sea múltiplo de `m` y casi cualquier matriz sirve. Módulo 26 solo sirve un tercio: 157 248 de las 456 976 matrices 2×2.

## Parte 4 · El programa en Python y la demo (3 min) · Kris

Es el 40 % de la nota. Detalle en `../guias/02_explicacion_del_codigo.pdf` y pasos de la demo en `05_demo.md`.

**Diapositiva 10. Estructura del código:**

| Archivo | Qué hace |
|---|---|
| `inversa.py` | Álgebra a mano: inverso modular, determinante, adjunta, inversa mod m |
| `hill.py` | Alfabetos, validar la clave, cifrar y descifrar |
| `ataque.py` | Recuperar la clave: `K = C · P⁻¹` |
| `imagen.py` | Imágenes módulo 256 |
| `app.py` + página | La interfaz web |
| `tests/` | 35 pruebas automáticas, todas pasan |

**Diapositiva 11. Funciones propias y librerías:**

- **Hechas por nosotros:** inverso modular (Euclides extendido), determinante por cofactores, adjunta, inversa módulo m, cifrado por bloques, ataque y cifrado de imágenes.
- **Librerías:** sympy (matrices), numpy (imágenes rápidas), Pillow (abrir fotos), Flask (página web), matplotlib (figuras).

Qué decir:
> La inversa la programamos con la fórmula de la adjunta. El resultado se compara con el de sympy para verificarlo.

**Diapositiva 12. Tamaños y casos que resuelve el programa:** claves 2×2, 3×3 y 4×4; alfabetos de 26, 37 y 113 símbolos; imágenes de cualquier tamaño (módulo 256); claves que no sirven, que se detectan y se explican.

**Diapositiva 13. Demostración** (los pasos están en `05_demo.md`; la diapositiva tiene la captura de respaldo):

1. HELP → HIAT con «Solo letras» y clave 2×2. Mostrar el paso a paso.
2. «Descifrar este resultado»: vuelve HELP y se ve `K⁻¹`.
3. Cambiar la clave a `[[2, 4], [6, 8]]`: se pone en rojo y explica `mcd(18, 26) = 2`.
4. Cambiar a 3×3 o 4×4 y «Todo el teclado» con el mensaje con tildes y signos (**varios tamaños y casos**).

## Parte 5 · Resultados: el ataque y las imágenes (2 min) · Milton

Detalle completo en `04_ataque_e_imagenes.md`.

**Diapositiva 14. Ataque de texto plano conocido:** si alguien conoce unos bloques del mensaje (`P`) y su cifrado (`C`), entonces `C = K · P`, y despejando:

```
K = C · P⁻¹   (mod 26)
```

Romper el cifrado es **resolver un sistema lineal**. Mostrarlo en la demo: «Usar el mensaje y el cifrado de arriba» y luego «Recuperar la clave». Aparece la misma `K`.

**Diapositiva 15. Cifrado de imágenes:** con `figuras/pixeles.png`. Cada píxel es `(R, G, B)` de 0 a 255 (no se usa ASCII). Se multiplican 3 píxeles seguidos por `K` módulo 256 y **cambia el color, no el lugar del píxel**: tres píxeles `(200, 40, 40)` salen `(56, 216, 216)`, `(120, 24, 24)` y `(160, 32, 32)`.

**Diapositiva 16. Cifrado por bloques y cifrado encadenado:** mostrar `figuras/imagen_sin_encadenar.png`. Las figuras se siguen viendo, porque bloques iguales dan cifrados iguales. Después mostrar `figuras/imagen_encadenada.png`: si cada bloque se mezcla con el cifrado anterior, queda como ruido. Pero sigue siendo lineal y la clave se saca igual. (En vivo: sección «Imágenes», «Usar la imagen de ejemplo» y clic en el círculo rojo.)

## Parte 6 · Conclusiones (1 min) · Luis

**Diapositiva 17. Conclusiones:**

1. El cifrado de Hill cifra multiplicando por una matriz y descifra multiplicando por su inversa.
2. Módulo `m` no basta con `det ≠ 0`: la clave es válida si y solo si `mcd(det K, m) = 1`.
3. Por ser lineal, la clave se recupera resolviendo `K = C · P⁻¹` con `n²` símbolos conocidos. Encadenar bloques oculta las figuras de una imagen, pero no evita este ataque.
4. Los cifrados actuales, como AES, también multiplican por matrices, pero agregan pasos no lineales para evitar este tipo de ataque.

**Diapositiva 18. Preguntas.** Antes de presentar, repasen `06_preguntas.md`. Cada uno responde las de su parte.
