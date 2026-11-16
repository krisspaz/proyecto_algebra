---
title: "Guía 1 · Objetivos y todo lo que hicimos"
subtitle: "Proyecto final de Álgebra Lineal · Cifrado de Hill · Grupo 15"
---

## 1. La idea del proyecto en un párrafo

Dos personas comparten una matriz secreta `K`. Para mandar un mensaje, lo convierten en números, lo cortan en bloques de `n` números y multiplican cada bloque por `K`, quedándose con el residuo de dividir entre `m` (el número de símbolos del alfabeto): `c = K · p (mod m)`. Para leerlo, el receptor multiplica por la inversa: `p = K⁻¹ · c (mod m)`. La matriz sirve como clave solo si `mcd(det K, m) = 1`, que es más exigente que el `det ≠ 0` de los reales. Como el cifrado es una transformación lineal, quien conozca un trozo del mensaje y su cifrado puede despejar la clave resolviendo un sistema: `K = C · P⁻¹`. Esa es la gran lección: **la linealidad que hace posible descifrar también hace posible romperlo.**

## 2. Objetivos

**General.** Aplicar matrices, determinantes e inversas al cifrado y descifrado de mensajes con el cifrado de Hill.

**Específicos.**

1. Explicar por qué una matriz sirve como clave módulo `m` solo si `mcd(det K, m) = 1` y calcular su inversa con la adjunta.
2. Programar el cifrado, el descifrado y la inversa módulo `m` en Python, y comprobarlos con ejemplos resueltos a mano.
3. Mostrar que, por ser lineal, la clave se recupera resolviendo un sistema a partir de texto conocido.
4. Extender el método a imágenes y ver qué información deja pasar.

## 3. Aplicaciones relevantes

La catedrática insiste en esto, así que conviene tenerlo claro y decirlo con seguridad:

1. **Mensajes reales.** El programa no solo cifra letras: con el alfabeto «Todo el teclado» (113 símbolos) cifra frases con mayúsculas, ñ, tildes, números y signos, como `¿Nos vemos mañana? Aula #204, a las 9:30 (¡no faltes!)`.
2. **Imágenes y fotos.** Una foto ya es una tabla de números de 0 a 255 (el rojo, verde y azul de cada píxel). El mismo cifrado, con módulo 256, cifra la foto. Como **cualquier archivo** de computadora (PDF, audio, documentos) son bytes de 0 a 255, la misma idea sirve para cifrar cualquier archivo.
3. **La idea vive en los cifrados modernos.** AES, el estándar con el que hoy se cifran WhatsApp, las páginas `https` y las tarjetas bancarias, tiene un paso llamado *MixColumns* que es exactamente multiplicar un bloque de 4 bytes por una matriz 4×4 fija. La diferencia es que AES lo combina con pasos **no lineales**, justamente para que no se pueda hacer el ataque que mostramos.
4. **Aprender por qué algo es inseguro.** El ataque `K = C · P⁻¹` muestra con álgebra lineal por qué un cifrado puramente lineal no protege. Es la razón de que existan los pasos no lineales.

## 4. Qué construimos

| Pieza | Qué es | Dónde |
|---|---|---|
| Programa en Python | Cifrar, descifrar, validar la clave, calcular la inversa módulo m a mano, atacar y cifrar imágenes | `hill.py`, `inversa.py`, `ataque.py`, `imagen.py` |
| Página web | Interfaz para hacer todo lo anterior con clics, mostrando el paso a paso de las cuentas | `app.py`, `templates/`, `static/` |
| Notebook | Las cuentas explicadas paso a paso, con figuras | `cifrado_hill.ipynb` (y su PDF en `entregas/programa/`) |
| Pruebas | 35 pruebas automáticas que verifican que todo funciona | `tests/test_hill.py` |
| Demos de consola | Ejemplos que se corren con un comando | `demo.py`, `demo_imagen.py` |
| Resultados | Tablas y gráficas del reporte (claves válidas, ataque, correlación de píxeles) | `resultados.py` |
| Reporte | El documento formal | `INFORME.md` → `entregas/reporte/INFORME.pdf` |
| Presentación | Guion, explicación de cada parte, demo y preguntas probables | `entregas/presentacion/` |
| Guías | Estas tres guías | `entregas/guias/` |

### Cómo fue evolucionando

1. **28 de octubre.** Kris arma la primera versión: cifrado y descifrado con sympy, el ataque, la página web y un primer informe.
2. **2 de noviembre.** Milton programa la inversa módulo `m` a mano (Euclides extendido y adjunta), para que el álgebra del curso se vea en el código y no dependa de una función de librería. Se agregan el notebook y el encadenamiento de bloques en imágenes, y se completa el informe con portada, objetivos, figuras y referencias.
3. **11 al 13 de noviembre.** La página web se rediseña para proyectarla: fondo blanco, la clave en azul, el resultado resaltado y el paso a paso con vectores. Cuando una clave no sirve, la matriz se pone en rojo y el ataque explica por qué falla. Se arma el material para la presentación.
4. **12 y 13 de noviembre.** La catedrática pregunta cómo se codifican las imágenes: ella suponía «un código ASCII por color y píxel». Se responde con un ejemplo de píxeles reales en el informe, el notebook y una nueva sección de imágenes en la web, donde se hace clic en un píxel y se ve la cuenta.
5. **15 de noviembre.** Llegan las rúbricas. El reporte se reorganiza en las secciones que piden, el guion se ajusta para que hablen los cuatro y se escriben estas guías.

## 5. Resultados principales

- **El ejemplo a mano coincide con el programa.** Con `K = [[3, 3], [2, 5]]`, "HELP" se cifra como **"HIAT"** y se descifra de vuelta con `K⁻¹ = [[15, 17], [20, 9]]`.
- **Varios tamaños y alfabetos.** Funciona con claves 2×2, 3×3 y 4×4, y con alfabetos de 26, 37 y 113 símbolos. Con un módulo primo casi cualquier matriz sirve; con 26 solo un tercio (157 248 de 456 976 matrices 2×2).
- **Las claves inválidas se detectan.** `[[2, 4], [6, 8]]` tiene `det = −8 ≠ 0`, pero `mcd(18, 26) = 2`: "NA" y "AA" se cifrarían igual, así que el programa la rechaza.
- **El ataque funciona.** Conociendo «ATAQUENALAMANECERPOR» (20 letras) y su cifrado, el programa recupera la clave 3×3 exacta.
- **Imágenes.** Cada píxel es `(R, G, B)` de 0 a 255; **no se usa ASCII**. La matriz cambia el color del píxel, no su lugar. Tres píxeles `(200, 40, 40)` salen `(56, 216, 216)`, `(120, 24, 24)` y `(160, 32, 32)`. Sin encadenar se siguen viendo las figuras; encadenando, la imagen queda como ruido, pero la clave sigue igual de expuesta al ataque.
- **35 pruebas automáticas pasan.**

## 6. Conclusiones

1. Cifrar con Hill es multiplicar por una matriz y descifrar es multiplicar por su inversa.
2. Módulo `m` no basta `det ≠ 0`: la clave sirve si y solo si `mcd(det K, m) = 1`.
3. La linealidad es a la vez su fortaleza matemática y su debilidad: el mismo álgebra que permite descifrar permite sacar la clave con `K = C · P⁻¹`.
4. Por eso los cifrados modernos como AES usan multiplicaciones por matrices, pero mezcladas con pasos no lineales.
