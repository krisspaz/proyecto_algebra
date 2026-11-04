"""Cifrado de Hill aplicado a imágenes: bloques de píxeles módulo 256.

Cada canal de la imagen se recorre por filas y se agrupa en bloques de n
píxeles horizontales consecutivos. Cada bloque p (valores 0-255) se cifra como
    c = K · p (mod 256)
K es invertible módulo 256 si y solo si det(K) es impar (mcd(det, 256) = 1).
"""
from math import gcd

import numpy as np
from sympy import Matrix

from inversa import determinante, inversa_mod

MOD_IMG = 256


def es_clave_valida_imagen(K: Matrix) -> bool:
    return K.is_square and gcd(int(determinante(K.tolist())) % MOD_IMG, MOD_IMG) == 1


def validar_clave_imagen(K: Matrix) -> None:
    if not K.is_square:
        raise ValueError("La clave debe ser una matriz cuadrada.")
    det = int(determinante(K.tolist())) % MOD_IMG
    if gcd(det, MOD_IMG) != 1:
        raise ValueError(
            f"Clave no invertible módulo 256: det(K) ≡ {det} es par."
        )


def _a_numpy(K: Matrix) -> np.ndarray:
    return np.array(K.tolist(), dtype=np.int64)


def _aplicar(K: np.ndarray, img: np.ndarray) -> np.ndarray:
    """Aplica K a cada bloque de n píxeles horizontales de cada canal."""
    n = K.shape[0]
    alto, ancho = img.shape[:2]
    canales = img.reshape(alto, ancho, -1).transpose(2, 0, 1)  # (c, alto, ancho)
    bloques = canales.reshape(-1, n).astype(np.int64)  # una fila por bloque
    resultado = (bloques @ K.T) % MOD_IMG  # equivale a K · p para cada bloque p
    salida = resultado.reshape(canales.shape).transpose(1, 2, 0)
    return salida.reshape(img.shape).astype(np.uint8)


def rellenar(img: np.ndarray, n: int) -> np.ndarray:
    """Añade columnas negras a la derecha para que el ancho sea múltiplo de n."""
    sobra = img.shape[1] % n
    if not sobra:
        return img
    relleno = [(0, 0), (0, n - sobra)] + [(0, 0)] * (img.ndim - 2)
    return np.pad(img, relleno)


def cifrar_imagen(img: np.ndarray, K: Matrix) -> np.ndarray:
    """Cifra una imagen uint8 (escala de grises o RGB). Si el ancho no es
    múltiplo de n, la imagen cifrada tendrá columnas extra de relleno."""
    validar_clave_imagen(K)
    return _aplicar(_a_numpy(K), rellenar(img, K.shape[0]))


def descifrar_imagen(cifrada: np.ndarray, K: Matrix, ancho: int | None = None) -> np.ndarray:
    """Descifra la imagen. Si se indica `ancho`, recorta el relleno."""
    validar_clave_imagen(K)
    if cifrada.shape[1] % K.shape[0]:
        raise ValueError("El ancho de la imagen cifrada no es múltiplo del tamaño de la clave.")
    plana = _aplicar(_a_numpy(Matrix(inversa_mod(K.tolist(), MOD_IMG))), cifrada)
    return plana[:, :ancho] if ancho is not None else plana


# --- Encadenamiento de bloques ------------------------------------------------
# Sin encadenar, bloques iguales dan cifrados iguales y se ven las figuras.
# Encadenando, cada bloque se suma con el cifrado anterior antes de multiplicar:
#     c_i = K · (p_i + c_{i-1})   (mod 256),   con c_0 = 0
# y para descifrar se despeja:
#     p_i = K⁻¹ · c_i − c_{i-1}   (mod 256)


def _a_bloques(img: np.ndarray, n: int) -> np.ndarray:
    # cada canal recorrido por filas, una fila de la salida por bloque
    canales = img.reshape(img.shape[0], img.shape[1], -1).transpose(2, 0, 1)
    return canales.reshape(-1, n).astype(np.int64)


def _a_imagen(bloques: np.ndarray, forma) -> np.ndarray:
    # inverso de _a_bloques
    alto, ancho = forma[:2]
    canales = bloques.reshape(-1, alto, ancho)
    return canales.transpose(1, 2, 0).reshape(forma).astype(np.uint8)


def cifrar_imagen_encadenado(img: np.ndarray, K: Matrix) -> np.ndarray:
    validar_clave_imagen(K)
    n = K.shape[0]
    img = rellenar(img, n)
    Kn = _a_numpy(K)
    bloques = _a_bloques(img, n)
    cifrados = np.zeros_like(bloques)
    anterior = np.zeros(n, dtype=np.int64)
    for i in range(len(bloques)):
        anterior = (Kn @ (bloques[i] + anterior)) % MOD_IMG
        cifrados[i] = anterior
    return _a_imagen(cifrados, img.shape)


def descifrar_imagen_encadenado(cifrada: np.ndarray, K: Matrix, ancho: int | None = None) -> np.ndarray:
    validar_clave_imagen(K)
    n = K.shape[0]
    if cifrada.shape[1] % n:
        raise ValueError("El ancho de la imagen cifrada no es múltiplo del tamaño de la clave.")
    K_inv = _a_numpy(Matrix(inversa_mod(K.tolist(), MOD_IMG)))
    cifrados = _a_bloques(cifrada, n)
    planos = np.zeros_like(cifrados)
    anterior = np.zeros(n, dtype=np.int64)
    for i in range(len(cifrados)):
        planos[i] = (K_inv @ cifrados[i] - anterior) % MOD_IMG
        anterior = cifrados[i]
    plana = _a_imagen(planos, cifrada.shape)
    return plana[:, :ancho] if ancho is not None else plana
