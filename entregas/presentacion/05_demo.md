# Demo en vivo

La demo es una página web que corre en la computadora de quien presenta. Python hace todas las cuentas y el navegador solo las muestra.

**Pruébenla completa al menos un día antes, en la misma computadora que van a usar.** Y tengan capturas de pantalla de cada paso en las diapositivas, por si algo falla en vivo. Ya están hechas en la carpeta `capturas/`, una por paso (`1_help_hiat.png` a `5_ataque.png`).

## Preparación (una sola vez)

Se necesita Python 3.10 o más nuevo. En una terminal:

```bash
git clone https://github.com/krisspaz/proyecto_algebra.git
cd proyecto_algebra
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

En Windows, cambien `.venv/bin/` por `.venv\Scripts\`.

## Antes de presentar

```bash
cd proyecto_algebra
.venv/bin/python app.py
```

Abran **http://127.0.0.1:5050** en el navegador y dejen la terminal abierta: si la cierran, la página deja de funcionar. Suban el zoom del navegador para que se vea desde atrás.

## Los pasos de la demo (≈2 min)

Conviene usar el mismo ejemplo de las diapositivas, para que el público lo reconozca.

### 1. El ejemplo de la clase: HELP → HIAT

1. En **Alfabeto**, elijan «Solo letras».
2. En **Clave K**, elijan 2×2 y llenen la matriz con `3  3` en la primera fila y `2  5` en la segunda.
3. En el mensaje escriban `HELP`.
4. Aparece **HIAT**, igual que en la pizarra. Muestren la sección «Paso a paso».

Qué decir:
> El programa hace exactamente la multiplicación que hicimos a mano.

### 2. Descifrar

Pulsen **«Descifrar este resultado»**: vuelve HELP. Señalen que la página muestra `K⁻¹ = [[15, 17], [20, 9]]`, la misma inversa que calculamos. Ojo: el botón deja la página en modo «Descifrar».

### 3. Una clave que no sirve

Cambien la clave a `[[2, 4], [6, 8]]` (primera fila `2  4`, segunda `6  8`). La matriz se pone en rojo, desaparece `K⁻¹` y la página avisa que `mcd(18, 26) = 2`: la clave no tiene inversa y no sirve.

Qué decir:
> El determinante es −8, que no es cero, y en los reales esta matriz tendría inversa. Módulo 26 no la tiene.

Después regresen la clave a `[[3, 3], [2, 5]]`.

### 4. Mensajes reales con «Todo el teclado»

Vuelvan a **«Cifrar»** (junto a «Mensaje»), cambien el alfabeto a «Todo el teclado» y escriban algo con signos y tildes, por ejemplo `¿Nos vemos mañana? Aula #204, a las 9:30 (¡no faltes!)`. Se cifra tal cual, con mayúsculas, ñ y signos. Pulsen «Descifrar este resultado» para mostrar que regresa igual.

Qué decir:
> Aquí el módulo es 113, que es primo, así que casi cualquier clave sirve.

### 5. El ataque

1. Bajen a **«Ataque: recuperar la clave»**.
2. Pulsen **«Usar el mensaje y el cifrado de arriba»**.
3. Pulsen **«Recuperar la clave»**.
4. Aparece la misma clave `K` que está arriba.

Qué decir:
> El atacante no conocía la clave, solo el mensaje y su cifrado. Resolvió `K = C · P⁻¹` y la sacó al instante.

### 6. Imágenes

1. Bajen a **«Imágenes (módulo 256)»**, al final de la página. Usa la misma clave de arriba.
2. Pulsen **«Usar la imagen de ejemplo»**. Aparecen cuatro imágenes: original, cifrada (se ven las figuras), encadenada (ruido) y descifrada (idéntica).
3. Hagan clic en el **círculo rojo** de la original. Abajo aparece «Un bloque de cerca»: los píxeles originales con su `(R, G, B)`, la cuenta `K · p ≡ c (mod 256)` de cada canal y los píxeles cifrados.

Qué decir:
> Una imagen ya son números: cada píxel es cuánto rojo, verde y azul tiene, de 0 a 255. No usamos ASCII. Multiplicamos los píxeles de 3 en 3 por la clave, módulo 256. Los píxeles no se mueven: cambia su color. Y como el bloque de al lado es igual, sale igual; por eso se sigue viendo el círculo.

También se puede pulsar **«Subir una imagen»** y usar una foto propia. Si la clave tiene determinante par, la sección avisa que no sirve para imágenes (256 = 2⁸). Captura de respaldo: `capturas/6_imagenes.png`. Las figuras del informe están en `figuras/` (`pixeles.png`, `imagen_sin_encadenar.png`, `imagen_encadenada.png`).

## Si algo falla

| Problema | Qué hacer |
|---|---|
| `python3` no existe | En Windows prueben `py` o `python`. |
| Error al instalar | Revisen que haya internet y que Python sea 3.10 o más nuevo (`python3 --version`). |
| «Address already in use» | Ya hay otra copia corriendo: ciérrenla o reinicien la terminal. |
| La página no carga | Revisen que la terminal con `app.py` siga abierta. |
| El ataque dice que no encontró combinación | El mensaje es muy corto o muy repetitivo. Usen uno más largo, o la clave 2×2 con HELP. |
| Cualquier otra cosa | No se pongan a arreglarlo en vivo: pasen a las capturas de pantalla y sigan. |
