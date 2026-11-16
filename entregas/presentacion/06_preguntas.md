# Preguntas probables y cómo responderlas

Respuestas cortas, para decirlas con sus palabras. Entre paréntesis está el archivo donde está la explicación completa.

## Sobre la matemática

**¿Por qué no basta con que el determinante sea distinto de cero?**
Porque módulo 26 no se puede dividir entre cualquier número. Para invertir `K` hay que «dividir» entre `det K`, o sea multiplicar por su inverso modular, y ese inverso solo existe si `mcd(det K, 26) = 1`. Ejemplo: `[[2, 4], [6, 8]]` tiene `det = −8 ≠ 0`, pero `−8 ≡ 18` y `mcd(18, 26) = 2`. (`03`)

**¿Qué pasa exactamente si se usa una clave que no sirve?**
Dos mensajes distintos dan el mismo cifrado, y entonces no se puede saber cuál era el original. Con `[[2, 4], [6, 8]]`, "NA" y "AA" se cifran igual. En términos del curso, la transformación no es inyectiva: hay un vector distinto de cero, `(13, 0)`, que va a parar al cero. (`03`)

**¿Cómo se calcula el inverso modular?**
Con el algoritmo de Euclides extendido. Por ejemplo, `26 = 2·9 + 8`, `9 = 1·8 + 1`, y despejando hacia atrás `1 = 3·9 − 26`, así que `9⁻¹ ≡ 3`. (`03`)

**¿Cómo se calcula la inversa de la clave?**
Con la fórmula de la adjunta que vimos en clase, `K⁻¹ = det(K)⁻¹ · adj(K)`, pero módulo 26: en vez de dividir entre el determinante se multiplica por su inverso modular. (`03`)

**¿Por qué A = 0 y no A = 1?**
Para que las 26 letras correspondan exactamente a los residuos 0 a 25. Si empezáramos en 1, la Z sería 26 ≡ 0 y chocaría con la A.

**¿Por qué usaron alfabetos de 37 y 113 símbolos?**
Porque son números primos. Con un módulo primo, la clave sirve si `det K` no es múltiplo de `m`, casi igual que en los reales, y casi cualquier matriz al azar funciona. Módulo 26 solo sirve alrededor de un tercio de las matrices. (`03`)

**¿Qué relación tiene esto con el curso?**
Multiplicación de matrices, determinantes por cofactores, adjunta, matriz inversa, sistemas lineales (en el ataque) y transformaciones lineales (inyectividad). Todo eso está en el libro de Poole. Lo nuevo es hacerlo con aritmética módulo `m` en lugar de con números reales.

## Sobre la seguridad

**¿Es seguro el cifrado de Hill hoy en día?**
No. Como es lineal, quien conozca un pedazo del mensaje y su cifrado saca la clave resolviendo `K = C · P⁻¹`. Con una clave 3×3 bastan 9 letras conocidas. (`04`)

**¿Y si el espía no conoce nada del mensaje?**
Es más difícil, pero con claves pequeñas se puede probar todas: con 2×2 solo hay 157 248 claves válidas, y una computadora las prueba en segundos. También se pueden estudiar las frecuencias de los pares de letras del idioma. (`03`)

**¿Qué pasa si los bloques conocidos no forman una matriz invertible?**
El atacante prueba con otra combinación de bloques hasta encontrar una con `mcd(det P, 26) = 1`. Nuestro programa hace eso automáticamente. (`04`)

**¿Por qué a veces el ataque no encuentra la clave?**
Porque los bloques conocidos tienen que formar una matriz `P` invertible módulo `m`. Con `m = 26 = 2 · 13` eso falla seguido. Ejemplo real: con «Solo letras» y una clave 4×4, el mensaje «¿Nos vemos mañana? Aula #204» da 4 bloques, y su `det P ≡ 10` con `mcd(10, 26) = 2`. Incluso con el mensaje completo ninguna combinación sirve: vistos como pares e impares, los bloques solo generan un espacio de dimensión 3, no 4. Con esos datos la clave no queda determinada. Ningún método la puede sacar sin más texto. Con un módulo primo, como 113, casi nunca pasa. (`04`)

**¿Cómo codifican las imágenes? ¿Usan un código ASCII para cada color?**
No hace falta ASCII: una imagen ya está hecha de números. Cada píxel es un trío `(R, G, B)` de 0 a 255 (cuánto rojo, verde y azul tiene). Se toman 3 píxeles seguidos, se arma el vector de sus rojos (y aparte el de verdes y el de azules), se multiplica por `K` y se reduce módulo 256 para que vuelva a ser un color válido. Ejemplo: tres píxeles `(200, 40, 40)` → `K·(200, 200, 200) = (6200, 7800, 10400) ≡ (56, 120, 160)` en el rojo. (`04`)

**¿La matriz cambia el color o el píxel?**
El color. Los píxeles se quedan en su lugar; lo que cambia son sus valores de R, G y B. Cada valor nuevo mezcla los 3 píxeles vecinos del bloque en ese canal, y los canales no se mezclan entre sí. En la demo se puede hacer clic en cualquier punto de la imagen y ver esa cuenta. (`04`, `05`)

**¿Por qué la clave para imágenes necesita det impar?**
Porque se trabaja módulo `256 = 2⁸`: la clave sirve si `mcd(det K, 256) = 1`, y eso pasa justo cuando `det K` es impar. Es el mismo teorema que con 26. (`03`)

**¿Por qué en la imagen cifrada se siguen viendo las figuras?**
Porque bloques iguales dan cifrados iguales. Una zona de un solo color se convierte en otra zona de un solo color, así que la forma se mantiene. Encadenar los bloques (sumar a cada uno el cifrado anterior) lo arregla. (`04`)

**¿Encadenar los bloques lo hace seguro?**
No. Esconde las figuras, pero el cifrado sigue siendo lineal y la clave se recupera igual con unos pocos píxeles conocidos. (`04`)

**¿Cómo lo hacen seguro los cifrados modernos?**
AES, el estándar actual, combina pasos lineales (como multiplicar matrices, igual que Hill) con pasos **no lineales** (tablas de sustitución llamadas S-boxes) y encadena los bloques. La parte no lineal es la que impide despejar la clave con un sistema.

**¿Qué diferencia hay con la criptografía de clave pública, como RSA?**
En Hill (clave privada) la misma clave cifra y descifra, así que las dos personas tienen que compartirla en secreto antes. En RSA (clave pública) cada persona tiene dos claves: una pública, que cualquiera usa para cifrarle mensajes, y una privada, que solo ella tiene para descifrarlos. RSA no usa matrices, sino potencias de números muy grandes módulo `n`.

**¿Qué tiene que ver con el cifrado César?**
Los dos cambian letras por letras usando aritmética módulo 26, pero César trabaja letra por letra y se rompe contando qué letra se repite más. Hill mezcla varias letras a la vez con la matriz, así que una misma letra puede cifrarse distinto según el bloque.

## Sobre el programa

**¿Qué hicieron ustedes y qué es de librerías?**
El inverso modular, el determinante por cofactores, la adjunta y la inversa módulo `m` están programados a mano, en `inversa.py`. La librería SymPy solo se usa para guardar matrices, multiplicarlas y comprobar que nuestra inversa da lo mismo que la suya. NumPy se usa en las imágenes, porque hay que multiplicar cientos de miles de bloques.

**¿Cómo saben que funciona?**
Con 35 pruebas automáticas (carpeta `tests/`), con la comparación contra SymPy en los módulos 26, 37, 113 y 256, y con el ejemplo HELP → HIAT hecho a mano, que el programa reproduce exactamente.

**¿Qué pasa si el mensaje no alcanza para el último bloque?**
Se completa con X (en «Solo letras») o con espacios (en los otros alfabetos). Al descifrar con espacios, el texto se ve igual que el original.

## Sobre las aplicaciones

**¿Para qué sirve esto en la vida real?**
Para cifrar mensajes reales (con «Todo el teclado» se cifra cualquier frase con tildes y signos), fotos y, en general, cualquier archivo, porque todo archivo son bytes de 0 a 255, como los píxeles. Y la idea sigue viva: AES, el cifrado de WhatsApp, `https` y los bancos, tiene un paso (*MixColumns*) que multiplica bloques de 4 bytes por una matriz 4×4. (`../guias/01_contexto_y_proyecto.pdf`, sección 3)

**Si AES multiplica por una matriz, ¿por qué no se rompe igual que Hill?**
Porque AES alterna esa multiplicación con pasos **no lineales** (las S-boxes) y repite todo 10 a 14 veces. El resultado ya no es una transformación lineal, así que no se puede despejar `K = C · P⁻¹`.

## Si no saben una respuesta

Está bien decir «no lo sabemos con certeza, pero lo podemos revisar». Es mucho mejor que inventar.
