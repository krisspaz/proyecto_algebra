"""Demo: cifrar y descifrar una imagen con Hill módulo 256.

Uso:
    python demo_imagen.py              # usa una imagen sintética
    python demo_imagen.py foto.png     # usa una imagen propia

Guarda original, cifrada, cifrada_encadenada y descifrada en la carpeta salida/.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from sympy import Matrix

from imagen import (
    cifrar_imagen,
    cifrar_imagen_encadenado,
    descifrar_imagen,
    descifrar_imagen_encadenado,
    es_clave_valida_imagen,
    explicar_bloque,
)

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


def tupla(v) -> str:
    return "(" + ", ".join(str(x) for x in v) + ")"


def mostrar_bloque(img: np.ndarray, fila: int, columna: int) -> None:
    """Imprime qué le pasa a un bloque de píxeles: cambia el color, no el lugar."""
    b = explicar_bloque(img, K, fila, columna)
    print(f"\nEjemplo: píxeles de la fila {fila}, columnas {b['columnas'][0]} a {b['columnas'][-1]}")
    print("  originales (R, G, B):", "  ".join(tupla(px) for px in b["original"]))
    for nombre, c in zip(("rojo ", "verde", "azul "), b["canales"]):
        print(f"  {nombre}: K·{tupla(c['p'])} = {tupla(c['Kp'])} ≡ {tupla(c['c'])} (mod 256)")
    print("  cifrados   (R, G, B):", "  ".join(tupla(px) for px in b["cifrado"]))
    print("  Los píxeles siguen en el mismo lugar; lo que cambia es su color.\n")


if len(sys.argv) > 1:
    original = np.array(Image.open(sys.argv[1]).convert("RGB"))
    fila_ejemplo, columna_ejemplo = original.shape[0] // 2, original.shape[1] // 2
else:
    original = imagen_sintetica()
    fila_ejemplo, columna_ejemplo = 60, 90  # dentro del círculo rojo

print("Clave:", K.tolist(), "| det mod 256 =", int(K.det()) % 256,
      "| válida:", es_clave_valida_imagen(K))
mostrar_bloque(original, fila_ejemplo, columna_ejemplo)

cifrada = cifrar_imagen(original, K)
descifrada = descifrar_imagen(cifrada, K, ancho=original.shape[1])
encadenada = cifrar_imagen_encadenado(original, K)
descifrada_enc = descifrar_imagen_encadenado(encadenada, K, ancho=original.shape[1])

SALIDA.mkdir(exist_ok=True)
Image.fromarray(original).save(SALIDA / "original.png")
Image.fromarray(cifrada).save(SALIDA / "cifrada.png")
Image.fromarray(descifrada).save(SALIDA / "descifrada.png")
Image.fromarray(encadenada).save(SALIDA / "cifrada_encadenada.png")

print("Tamaño original:", original.shape, "| cifrada:", cifrada.shape)
print("¿Descifrada idéntica a la original?", np.array_equal(original, descifrada))
print("¿Descifrada (encadenada) idéntica a la original?", np.array_equal(original, descifrada_enc))
print("Imágenes guardadas en", SALIDA)

try:
    cifrar_imagen(original, Matrix([[2, 1], [1, 1]]) * 2)
except ValueError as e:
    print("Clave par rechazada:", e)
