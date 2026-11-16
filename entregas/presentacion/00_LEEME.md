# Presentación del proyecto: Cifrado de Hill

**Para:** los cuatro integrantes. Presentamos el lunes 16 de noviembre (6 pts): 60 % presentación y 40 % Python. Según la rúbrica se califica la participación de los integrantes, así que hablan los cuatro.
**Grupo 15 · Álgebra Lineal, sección B.**

Estos archivos les dan todo lo necesario para preparar la presentación y defenderla en las preguntas. Lean primero el guion (01), que tiene la rúbrica, el reparto y el tiempo de cada parte. Los demás archivos explican cada parte a fondo. En `../guias/` hay tres guías en PDF: contexto del proyecto, explicación del código y el programa sin tecnicismos.

| Archivo | Qué tiene |
|---|---|
| `01_guion.md` | La rúbrica, qué decir, en qué orden, cuánto tiempo, quién habla y qué diapositivas hacer |
| `02_la_idea.md` | Qué es el cifrado de Hill y el ejemplo HELP → HIAT paso a paso |
| `03_la_matematica.md` | Módulo 26, inverso modular, inversa de la clave y cuándo una clave sirve |
| `04_ataque_e_imagenes.md` | Cómo se rompe el cifrado y qué pasa al cifrar imágenes |
| `05_demo.md` | Cómo correr la demo en vivo y qué hacer si falla |
| `06_preguntas.md` | Preguntas que probablemente haga la catedrática, con su respuesta |

## Lo que tienen que poder explicar sin leer

1. Cifrar es **multiplicar una matriz por un vector**: `c = K · p (mod 26)`.
2. Descifrar es **multiplicar por la inversa**: `p = K⁻¹ · c (mod 26)`.
3. Una matriz sirve como clave solo si **`mcd(det K, 26) = 1`**. No basta con `det ≠ 0`, como en los reales.
4. Como el cifrado es **lineal**, si alguien conoce un trozo del mensaje y su cifrado puede sacar la clave resolviendo un sistema: `K = C · P⁻¹`.

Si dominan esas cuatro ideas, el resto es detalle.

## Si usan IA para hacer las diapositivas

Péguenle a la IA el guion (`01_guion.md`) y el archivo de la parte que quieran convertir en diapositivas, con algo como:

> Haz diapositivas para una presentación universitaria de Álgebra Lineal a partir de este guion. Una idea por diapositiva, poco texto, fórmulas grandes. No inventes números ni ejemplos: usa exactamente los del texto.

Revisen siempre los números contra estos archivos. Las IA suelen equivocarse en las cuentas módulo 26.

## Material listo para usar

- **Figuras de imágenes cifradas:** `figuras/imagen_sin_encadenar.png` y `figuras/imagen_encadenada.png` (en el repo).
- **Capturas de la demo, paso por paso:** carpeta `capturas/` (aquí mismo).
- **Notebook con todo calculado:** `cifrado_hill.ipynb` (secciones 1 a 7, con las mismas cuentas que aquí).
- **Informe completo:** `INFORME.md`.
- **Repositorio:** https://github.com/krisspaz/proyecto_algebra

Cualquier duda, pregúntenle a Milton (inversa, ataque, imágenes) o a Kris (interfaz web). La guía 3 (`../guias/03_el_programa_sin_tecnicismos.pdf`) explica todo el programa sin código.
