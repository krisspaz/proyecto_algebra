"""Cifrado de Hill: cifrado por bloques con matrices módulo m.

Convención: cada bloque de n símbolos es un vector columna p y se cifra como
    c = K · p (mod m)
donde m es el tamaño del alfabeto y K es una matriz n×n invertible módulo m.

Alfabetos disponibles:
    LETRAS        A-Z                                  → m = 26
    ALFANUMERICO  A-Z, 0-9 y espacio                   → m = 37 (primo)
    COMPLETO      todo el teclado + letras del español → m = 113 (primo)
"""
import unicodedata
from dataclasses import dataclass
from math import gcd

from sympy import Matrix

from inversa import determinante, inversa_mod


@dataclass(frozen=True)
class Alfabeto:
    clave: str  # identificador corto, el que usa la interfaz web
    nombre: str
    simbolos: str
    relleno: str  # símbolo para completar el último bloque
    descripcion: str

    @property
    def mod(self) -> int:
        return len(self.simbolos)


_ASCII_IMPRIMIBLE = "".join(chr(i) for i in range(32, 127))  # espacio, signos, dígitos, A-Z, a-z
_ESPANOL = "¡¿ÁÉÍÓÚÜÑáéíóúüñ"

LETRAS = Alfabeto(
    "letras", "Solo letras", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "X",
    "Las minúsculas pasan a mayúsculas y se quitan las tildes (á→A, ñ→N). Números, espacios y signos no se cifran.",
)
ALFANUMERICO = Alfabeto(
    "alfanumerico", "Letras, números y espacio", LETRAS.simbolos + "0123456789 ", " ",
    "Las minúsculas pasan a mayúsculas y se quitan las tildes. Los signos (¿ ? , . : #…) no se cifran.",
)
COMPLETO = Alfabeto(
    "completo", "Todo el teclado", _ASCII_IMPRIMIBLE + _ESPANOL + "€°", " ",
    "Se cifra el texto tal cual: mayúsculas, minúsculas, números, espacio, signos, ñ, tildes, ¿ ¡ € °. Solo quedan fuera emojis y saltos de línea.",
)

ALFABETOS = {a.clave: a for a in (LETRAS, ALFANUMERICO, COMPLETO)}

# Compatibilidad con el código que usa el alfabeto clásico de 26 letras
ALFABETO = LETRAS
MOD = LETRAS.mod
RELLENO = LETRAS.relleno


# --- Texto ↔ números -------------------------------------------------------

def adaptar_simbolo(ch: str, alfabeto: Alfabeto = LETRAS) -> str | None:
    """Devuelve el símbolo del alfabeto que corresponde a `ch`, o None si no hay.
    Prueba tal cual, en mayúscula y sin tilde (á → A con LETRAS, á → á con COMPLETO)."""
    sin_tilde = unicodedata.normalize("NFD", ch)[0]
    for variante in (ch, ch.upper(), sin_tilde, sin_tilde.upper()):
        if variante in alfabeto.simbolos:
            return variante
    return None


def limpiar(texto: str, alfabeto: Alfabeto = LETRAS) -> str:
    """Deja solo símbolos del alfabeto, adaptando mayúsculas y tildes cuando hace falta."""
    adaptados = (adaptar_simbolo(ch, alfabeto) for ch in unicodedata.normalize("NFC", texto))
    return "".join(ch for ch in adaptados if ch is not None)


def simbolos_ignorados(texto: str, alfabeto: Alfabeto = LETRAS) -> list[str]:
    """Caracteres del texto que no se pueden cifrar con este alfabeto (sin repetir)."""
    vistos = dict.fromkeys(
        ch for ch in unicodedata.normalize("NFC", texto) if adaptar_simbolo(ch, alfabeto) is None
    )
    return list(vistos)


def texto_a_numeros(texto: str, alfabeto: Alfabeto = LETRAS) -> list[int]:
    return [alfabeto.simbolos.index(ch) for ch in texto]


def numeros_a_texto(numeros, alfabeto: Alfabeto = LETRAS) -> str:
    return "".join(alfabeto.simbolos[int(n) % alfabeto.mod] for n in numeros)


# --- Clave ------------------------------------------------------------------

def es_clave_valida(K: Matrix, mod: int = MOD) -> bool:
    """K sirve como clave si es cuadrada y det(K) es coprimo con el módulo."""
    return K.is_square and gcd(int(determinante(K.tolist())) % mod, mod) == 1


def validar_clave(K: Matrix, mod: int = MOD) -> None:
    if not K.is_square:
        raise ValueError("La clave debe ser una matriz cuadrada.")
    det = int(determinante(K.tolist())) % mod
    if gcd(det, mod) != 1:
        raise ValueError(
            f"Clave no invertible módulo {mod}: det(K) ≡ {det} y mcd({det}, {mod}) ≠ 1."
        )


def analizar_clave(K: Matrix, mod: int) -> dict:
    """Datos de la clave para mostrar: determinante, mcd con m y la inversa si existe."""
    det = int(determinante(K.tolist()))
    mcd = gcd(det % mod, mod)
    inversa = Matrix(inversa_mod(K.tolist(), mod)) if mcd == 1 else None
    return dict(det=det, det_mod=det % mod, mcd=mcd, valida=mcd == 1, inversa=inversa)


# --- Cifrado ----------------------------------------------------------------

def _bloques(numeros: list[int], n: int) -> Matrix:
    """Agrupa los números en una matriz n×m donde cada columna es un bloque."""
    m = len(numeros) // n
    return Matrix(n, m, lambda i, j: numeros[j * n + i])


def multiplicar_bloques(M: Matrix, texto: str, alfabeto: Alfabeto = LETRAS):
    """Aplica M a cada bloque del texto. Devuelve (P, M·P sin reducir, M·P mod m),
    con un bloque por columna. El texto ya debe tener longitud múltiplo de n."""
    P = _bloques(texto_a_numeros(texto, alfabeto), M.shape[0])
    producto = M * P
    return P, producto, producto.applyfunc(lambda x: x % alfabeto.mod)


def _aplicar(M: Matrix, texto: str, alfabeto: Alfabeto) -> str:
    _, _, C = multiplicar_bloques(M, texto, alfabeto)
    # Recorrer por columnas para reconstruir el texto en orden
    return numeros_a_texto((C[i, j] for j in range(C.cols) for i in range(C.rows)), alfabeto)


def preparar_mensaje(mensaje: str, n: int, alfabeto: Alfabeto = LETRAS) -> str:
    """Limpia el mensaje y lo completa con el símbolo de relleno hasta un múltiplo de n."""
    texto = limpiar(mensaje, alfabeto)
    if len(texto) % n:
        texto += alfabeto.relleno * (n - len(texto) % n)
    return texto


def preparar_cifrado(cifrado: str, n: int, alfabeto: Alfabeto = LETRAS) -> str:
    texto = limpiar(cifrado, alfabeto)
    if len(texto) % n:
        raise ValueError(
            f"El texto cifrado debe tener un múltiplo de {n} símbolos (tiene {len(texto)})."
        )
    return texto


def cifrar(mensaje: str, K: Matrix, alfabeto: Alfabeto = LETRAS) -> str:
    validar_clave(K, alfabeto.mod)
    return _aplicar(K, preparar_mensaje(mensaje, K.shape[0], alfabeto), alfabeto)


def descifrar(cifrado: str, K: Matrix, alfabeto: Alfabeto = LETRAS) -> str:
    validar_clave(K, alfabeto.mod)
    texto = preparar_cifrado(cifrado, K.shape[0], alfabeto)
    return _aplicar(Matrix(inversa_mod(K.tolist(), alfabeto.mod)), texto, alfabeto)
