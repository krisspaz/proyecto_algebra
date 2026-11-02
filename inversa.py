"""Inversa de una matriz modulo m, hecha a mano (sin sympy).

Usa la formula del informe (seccion 2.3):
    K^-1 = det(K)^-1 * adj(K)   (mod m)
Las matrices son listas de listas, por ejemplo [[3, 3], [2, 5]].
"""


def inverso_modular(a, m):
    # euclides extendido: busca x tal que a*x = 1 (mod m)
    a = a % m
    r0, r1 = m, a
    x0, x1 = 0, 1
    while r1 != 0:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        x0, x1 = x1, x0 - q * x1
    # al terminar, r0 es el mcd(a, m)
    if r0 != 1:
        raise ValueError(f"{a} no tiene inverso modulo {m}, mcd({a}, {m}) = {r0}")
    return x0 % m


def menor(A, i, j):
    # matriz sin la fila i y sin la columna j
    M = []
    for k in range(len(A)):
        if k != i:
            M.append(A[k][:j] + A[k][j + 1:])
    return M


def determinante(A):
    # desarrollo por cofactores en la primera fila
    if len(A) == 1:
        return A[0][0]
    det = 0
    for j in range(len(A)):
        det += (-1) ** j * A[0][j] * determinante(menor(A, 0, j))
    return det


def adjunta(A):
    # traspuesta de la matriz de cofactores: adj[i][j] = C[j][i]
    n = len(A)
    adj = []
    for i in range(n):
        fila = []
        for j in range(n):
            fila.append((-1) ** (i + j) * determinante(menor(A, j, i)))
        adj.append(fila)
    return adj


def inversa_mod(A, m):
    det = determinante(A) % m
    det_inv = inverso_modular(det, m)  # aqui falla si mcd(det, m) != 1
    adj = adjunta(A)
    inv = []
    for fila in adj:
        inv.append([(det_inv * x) % m for x in fila])
    return inv


def multiplicar_mod(A, B, m):
    n = len(A)
    C = []
    for i in range(n):
        fila = []
        for j in range(len(B[0])):
            suma = 0
            for k in range(n):
                suma += A[i][k] * B[k][j]
            fila.append(suma % m)
        C.append(fila)
    return C


if __name__ == "__main__":
    from sympy import Matrix

    # ejemplo resuelto del informe
    print("9^-1 mod 26 =", inverso_modular(9, 26))
    K = [[3, 3], [2, 5]]
    print("K =", K, "| det =", determinante(K))
    print("adj(K) =", adjunta(K))
    print("K^-1 mod 26 =", inversa_mod(K, 26))

    # comparar con sympy en las claves del proyecto y los tres modulos
    claves = [
        [[3, 3], [2, 5]],
        [[6, 24, 1], [13, 16, 10], [20, 17, 15]],
        [[1, 2, 0, 1], [0, 1, 3, 2], [2, 0, 1, 1], [1, 3, 1, 0]],
    ]
    for m in (26, 37, 113, 256):
        for K in claves:
            inv = inversa_mod(K, m)
            identidad = multiplicar_mod(K, inv, m)
            igual_sympy = inv == Matrix(K).inv_mod(m).tolist()
            es_identidad = identidad == Matrix.eye(len(K)).tolist()
            print(f"m = {m:3}, {len(K)}x{len(K)}: igual a sympy {igual_sympy}, K*K^-1 = I {es_identidad}")

    # clave que no sirve: det = -8 = 18 (mod 26)
    try:
        inversa_mod([[2, 4], [6, 8]], 26)
    except ValueError as e:
        print("clave rechazada:", e)
