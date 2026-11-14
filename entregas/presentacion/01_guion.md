# Guion de la presentación (≈10 minutos)

La catedrática no dio duración ni formato. Este guion está pensado para unos 10 minutos. Si les dan más tiempo, alarguen la parte 3 (la matemática) y la demo; si les dan menos, recorten las imágenes.

El reparto entre Rosemary y Luis es una sugerencia. Lo importante es que cada uno pueda responder preguntas de su parte.

---

## Parte 1 · El problema (1 min) — Rosemary

**Diapositiva 1. Portada:** Cifrado de Hill: álgebra lineal aplicada a la criptografía. Grupo 15, los cuatro nombres.

**Diapositiva 2. El problema:** dos personas quieren mandarse mensajes que nadie más pueda leer. Comparten una **clave secreta**: la misma clave sirve para cifrar y para descifrar. Eso se llama criptografía de **clave privada** (o simétrica).

Qué decir:
> Lester Hill propuso en 1929 un cifrado que usa directamente lo que vimos en el curso: matrices, determinantes e inversas.

## Parte 2 · La idea de Hill (2 min) — Rosemary

Detalle completo en `02_la_idea.md`.

**Diapositiva 3. De letras a números:** A=0, B=1, …, Z=25. El mensaje se corta en bloques de 2 letras y cada bloque es un vector.

**Diapositiva 4. Cifrar = multiplicar:**

```
c = K · p   (mod 26)
```

**Diapositiva 5. Ejemplo HELP → HIAT:** hacerlo paso a paso (en la pizarra si se puede):

- Clave `K = [[3, 3], [2, 5]]`
- `HE = (7, 4)` → `K · (7, 4) = (33, 34) ≡ (7, 8)` → **HI**
- `LP = (11, 15)` → `K · (11, 15) = (78, 97) ≡ (0, 19)` → **AT**

Qué decir:
> «Módulo 26» significa que nos quedamos con el residuo de dividir entre 26, como en un reloj de 26 horas. Así el resultado siempre vuelve a ser una letra.

## Parte 3 · La matemática (3 min) — Luis

Detalle completo en `03_la_matematica.md`. Es la parte más importante para la nota: aquí se ve el álgebra lineal.

**Diapositiva 6. Descifrar = multiplicar por la inversa:**

```
p = K⁻¹ · c   (mod 26)
K⁻¹ = det(K)⁻¹ · adj(K)   (mod 26)
```

Para nuestra clave: `det K = 9`, `9⁻¹ ≡ 3` (porque `9 · 3 = 27 ≡ 1`), y queda `K⁻¹ = [[15, 17], [20, 9]]`. Comprobar: `K⁻¹ · (7, 8) ≡ (7, 4)` → HE.

**Diapositiva 7. ¿Cuándo sirve una clave?**

> En los reales una matriz tiene inversa si `det ≠ 0`. Módulo 26 no basta: hace falta `mcd(det K, 26) = 1`.

**Diapositiva 8. Contraejemplo:** `K = [[2, 4], [6, 8]]` tiene `det = −8 ≠ 0`, pero `−8 ≡ 18` y `mcd(18, 26) = 2`. Con esa clave, "NA" y "AA" se cifran igual, así que nadie podría descifrar.

## Parte 4 · Demo en vivo (2 min) — Luis

Instrucciones completas en `05_demo.md`. Tengan capturas de respaldo por si algo falla.

1. Cifrar un mensaje con signos y tildes en «Todo el teclado».
2. Pulsar «Descifrar este resultado» y mostrar que vuelve el original.
3. Cambiar un número de la clave hasta que deje de servir y mostrar el aviso.
4. En «Ataque», pulsar «Usar el mensaje y el cifrado de arriba» y «Recuperar la clave».

## Parte 5 · Cómo se rompe y qué pasa con imágenes (1 min) — Rosemary

Detalle completo en `04_ataque_e_imagenes.md`.

**Diapositiva 9. El ataque:** si alguien conoce unos bloques del mensaje (`P`) y su cifrado (`C`), entonces `C = K · P`, y despejando:

```
K = C · P⁻¹   (mod 26)
```

Romper el cifrado es **resolver un sistema lineal**. Con una clave 3×3 bastan 9 letras conocidas, siempre que sus bloques formen una `P` invertible.

**Diapositiva 10. Imágenes:** mostrar `figuras/imagen_sin_encadenar.png`. Se cifran los píxeles módulo 256, pero **las figuras se siguen viendo**, porque bloques iguales dan cifrados iguales. Luego mostrar `figuras/imagen_encadenada.png`: si cada bloque se mezcla con el cifrado anterior, la imagen queda como ruido.

## Parte 6 · Conclusión (1 min) — Luis

**Diapositiva 11. Conclusiones:**

1. Cifrar y descifrar con Hill es multiplicar por una matriz y por su inversa.
2. Módulo 26 la regla cambia: la clave sirve si `mcd(det K, 26) = 1`.
3. **La linealidad es a la vez su fortaleza matemática y su debilidad:** el mismo álgebra que permite descifrar permite sacar la clave.
4. Por eso los cifrados modernos (como AES) mezclan pasos lineales con pasos no lineales.

**Diapositiva 12. Preguntas.** Antes de presentar, repasen `06_preguntas.md`.
