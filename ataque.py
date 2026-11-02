"""Ataque de texto plano conocido contra el cifrado de Hill.

Si el atacante conoce n bloques de texto plano P y sus cifrados C (como
matrices n×n con un bloque por columna), entonces C = K·P (mod m) y, si P es
invertible módulo m:
    K = C · P⁻¹ (mod m)
Es decir, recuperar la clave es resolver un sistema lineal. Esa linealidad es
la debilidad del cifrado.
"""
from itertools import combinations, islice

from sympy import Matrix

from hill import LETRAS, Alfabeto, _bloques, es_clave_valida, limpiar, texto_a_numeros
from inversa import inversa_mod

# Con muchos bloques las combinaciones crecen muy rápido (C(1000, 4) ≈ 4·10¹⁰).
# Si ninguna de las primeras sirve, es casi seguro que el texto es demasiado repetitivo.
MAX_INTENTOS = 20_000


def recuperar_clave(texto_plano: str, texto_cifrado: str, n: int,
                    alfabeto: Alfabeto = LETRAS, max_intentos: int = MAX_INTENTOS):
    """Busca n bloques del texto conocido que formen una matriz invertible mod m
    y devuelve la clave K. Lanza ValueError si no encuentra ninguna combinación."""
    mod = alfabeto.mod
    p = texto_a_numeros(limpiar(texto_plano, alfabeto), alfabeto)
    c = texto_a_numeros(limpiar(texto_cifrado, alfabeto), alfabeto)
    total = min(len(p), len(c)) // n
    if total < n:
        raise ValueError(f"Se necesitan al menos {n} bloques ({n * n} símbolos) conocidos.")

    P_todos = _bloques(p[: total * n], n)
    C_todos = _bloques(c[: total * n], n)

    for columnas in islice(combinations(range(total), n), max_intentos):
        P = P_todos.extract(list(range(n)), list(columnas))
        if es_clave_valida(P, mod):  # misma condición: det coprimo con m
            C = C_todos.extract(list(range(n)), list(columnas))
            return (C * Matrix(inversa_mod(P.tolist(), mod))).applyfunc(lambda x: x % mod)

    raise ValueError(
        f"Ninguna combinación de bloques conocidos es invertible módulo {mod}. "
        "Prueba con un texto conocido más largo o menos repetitivo."
    )
