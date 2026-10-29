"""Demo: cifrar, descifrar y romper el cifrado de Hill."""
from sympy import Matrix

from ataque import recuperar_clave
from hill import cifrar, descifrar, es_clave_valida

K = Matrix([[6, 24, 1], [13, 16, 10], [20, 17, 15]])  # clave clásica 3×3

print("== Clave ==")
print(K, "| det mod 26 =", int(K.det()) % 26, "| válida:", es_clave_valida(K))

mensaje = "Ataquen al amanecer por el flanco norte"
cifrado = cifrar(mensaje, K)
print("\n== Cifrado ==")
print("Mensaje:  ", mensaje)
print("Cifrado:  ", cifrado)
print("Descifrado:", descifrar(cifrado, K))

print("\n== Clave inválida ==")
try:
    cifrar("hola", Matrix([[2, 4], [6, 8]]))
except ValueError as e:
    print("Rechazada:", e)

print("\n== Ataque de texto plano conocido ==")
# El atacante conoce el inicio del mensaje. Con "ATAQUENALAMANECER" (5 bloques)
# no alcanza: ninguna terna de bloques es invertible mod 26.
conocido = "ATAQUENALAMANECERPOR"
K_recuperada = recuperar_clave(conocido, cifrado, n=3)
print("Clave recuperada:", K_recuperada)
print("¿Coincide con la original?", K_recuperada == K)
