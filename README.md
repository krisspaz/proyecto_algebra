# Cifrado de Hill

Proyecto de álgebra lineal: cifrado de clave privada con matrices módulo 26 y un ataque de texto plano conocido que recupera la clave.

## Estructura

- `hill.py`: conversión de texto a números, validación de la clave, cifrado y descifrado con tres alfabetos: solo letras (mod 26), letras + números + espacio (mod 37) y todo el teclado (mod 113)
- `cifrado_hill.ipynb`: notebook explicativo con el ejemplo a mano, la inversa, el ataque y las imágenes
- `inversa.py`: inverso modular, determinante, adjunta e inversa módulo m hechos a mano
- `ataque.py`: recupera la clave K = C · P⁻¹ (mod 26) a partir de texto plano conocido
- `app.py` + `templates/` + `static/`: interfaz web para cifrar, descifrar, atacar y cifrar imágenes (con la cuenta de cada bloque de píxeles)
- `tests/`: pruebas automáticas
- `imagen.py` (extra): cifrado de imágenes por bloques de píxeles (mod 256, clave con det impar). Cada píxel es (R, G, B) de 0 a 255: la matriz cambia el color, no el lugar del píxel
- `demo.py`: demo de texto (cifrar, descifrar, clave inválida, ataque)
- `demo_imagen.py` (extra): demo de imagen; imprime la cuenta de un bloque de píxeles y guarda original, cifrada, encadenada y descifrada en `salida/`
- `resultados.py`: tablas y figuras de la sección Resultados del reporte
- `INFORME.md`: el reporte final (su PDF está en `entregas/reporte/INFORME.pdf`)
- `entregas/`: PDF del reporte, del notebook y de los preliminares; material de la presentación; y tres guías en PDF (`entregas/guias/`): contexto del proyecto, explicación del código y el programa sin tecnicismos

## Cómo correrlo

Hace falta Python 3.10 o más nuevo. La primera vez, desde la carpeta del proyecto:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py                    # interfaz web en http://127.0.0.1:5050
.venv/bin/python demo.py
.venv/bin/python -m unittest -v           # pruebas
.venv/bin/python demo_imagen.py            # imagen sintética
.venv/bin/python demo_imagen.py foto.png   # imagen propia
```

En Windows, cambiar `python3` por `py` y `.venv/bin/` por `.venv\Scripts\`. Para la interfaz web, dejar la terminal abierta y abrir http://127.0.0.1:5050; se detiene con `Ctrl+C`. Si el puerto está ocupado: `PORT=5051 .venv/bin/python app.py`.
