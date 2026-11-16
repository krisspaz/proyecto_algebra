"""Ataque de texto plano conocido contra el cifrado de Hill.

Si el atacante conoce n bloques de texto plano P y sus cifrados C (como
matrices n×n con un bloque por columna), entonces C = K·P (mod m) y, si P es
invertible módulo m:
    K = C · P⁻¹ (mod m)
Es decir, recuperar la clave es resolver un sistema lineal. Esa linealidad es
la debilidad del cifrado.
"""
from itertools import combinations, islice
from math import comb, gcd

from sympy import Matrix, factorint, isprime

from hill import COMPLETO, LETRAS, Alfabeto, _bloques, es_clave_valida, limpiar, texto_a_numeros
from inversa import determinante, inversa_mod

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

    probadas = 0
    for columnas in islice(combinations(range(total), n), max_intentos):
        probadas += 1
        P = P_todos.extract(list(range(n)), list(columnas))
        if es_clave_valida(P, mod):  # misma condición: det coprimo con m
            C = C_todos.extract(list(range(n)), list(columnas))
            return (C * Matrix(inversa_mod(P.tolist(), mod))).applyfunc(lambda x: x % mod)

    raise ValueError(_motivo_del_fallo(P_todos, total, n, probadas, mod))


def _motivo_del_fallo(P_todos, total, n, probadas, mod):
    """Explica por qué no se pudo despejar K y qué probar."""
    if total == n:
        d = determinante(P_todos.tolist()) % mod
        motivo = (f"Con {total} bloques conocidos solo hay una matriz P posible, y no es "
                  f"invertible módulo {mod}: det P ≡ {d} y mcd({d}, {mod}) = {gcd(d, mod)}.")
    else:
        cuales = "las" if probadas == comb(total, n) else "las primeras"
        motivo = (f"Con {total} bloques conocidos se probaron {cuales} {probadas} formas de "
                  f"elegir {n} y ninguna da una P invertible módulo {mod}: el determinante "
                  f"siempre comparte un factor con {mod}.")

    if isprime(mod):
        consejo = " Prueba con un trozo conocido más largo."
    else:
        factores = " · ".join(str(p) for p, e in factorint(mod).items() for _ in range(e))
        consejo = (f" Como {mod} = {factores} no es primo, esto pasa seguido. Prueba con otro "
                   f"trozo conocido, otro tamaño de clave o el alfabeto «{COMPLETO.nombre}», "
                   f"cuyo número de símbolos ({COMPLETO.mod}) es primo.")
    return motivo + consejo
