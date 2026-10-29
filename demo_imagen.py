"""Demo: cifrar y descifrar una imagen con Hill módulo 256.

Uso:
    python demo_imagen.py              # usa una imagen sintética
    python demo_imagen.py foto.png     # usa una imagen propia

Guarda original, cifrada y descifrada en la carpeta salida/.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from sympy import Matrix

from imagen import cifrar_imagen, descifrar_imagen, es_clave_valida_imagen

K = Matrix([[6, 24, 1], [13, 16, 10], [20, 17, 15]])  # det = 441, impar
SALIDA = Path(__file__).parent / "salida"


def imagen_sintetica(alto: int = 200, ancho: int = 301) -> np.ndarray:
    """Fondo uniforme con figuras: deja ver qué pasa con zonas de color plano.
    El ancho 301 no es múltiplo de 3 a propósito, para probar el relleno."""
    img = np.full((alto, ancho, 3), (235, 235, 220), dtype=np.uint8)
    y, x = np.ogrid[:alto, :ancho]
    img[(y - 100) ** 2 + (x - 90) ** 2 < 60**2] = (200, 40, 40)  # círculo
    img[40:160, 170:270] = (30, 80, 180)  # rectángulo
    img[90:110, :] = np.linspace(0, 255, ancho, dtype=np.uint8)[:, None]  # degradado
    return img


if len(sys.argv) > 1:
    original = np.array(Image.open(sys.argv[1]).convert("RGB"))
else:
    original = imagen_sintetica()

print("Clave:", K.tolist(), "| det mod 256 =", int(K.det()) % 256,
      "| válida:", es_clave_valida_imagen(K))

cifrada = cifrar_imagen(original, K)
descifrada = descifrar_imagen(cifrada, K, ancho=original.shape[1])

SALIDA.mkdir(exist_ok=True)
Image.fromarray(original).save(SALIDA / "original.png")
Image.fromarray(cifrada).save(SALIDA / "cifrada.png")
Image.fromarray(descifrada).save(SALIDA / "descifrada.png")

print("Tamaño original:", original.shape, "| cifrada:", cifrada.shape)
print("¿Descifrada idéntica a la original?", np.array_equal(original, descifrada))
print("Imágenes guardadas en", SALIDA)

try:
    cifrar_imagen(original, Matrix([[2, 1], [1, 1]]) * 2)
except ValueError as e:
    print("Clave par rechazada:", e)
