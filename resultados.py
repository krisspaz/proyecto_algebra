"""Experimentos de la sección «Resultados» del reporte.

Ejecutar:  python resultados.py
Imprime las tablas del reporte y guarda las figuras en figuras/:
    claves_validas.png    proporción de claves válidas por módulo y tamaño
    histogramas.png       valores del canal rojo: original, cifrada y encadenada
    diagrama_flujo.png    diagrama de flujo del programa
"""
from fractions import Fraction
from pathlib import Path

import numpy as np
from sympy import Matrix, primefactors

from ataque import recuperar_clave
from hill import ALFANUMERICO, COMPLETO, LETRAS, cifrar, es_clave_valida
from imagen import cifrar_imagen, cifrar_imagen_encadenado, imagen_de_prueba

FIGURAS = Path(__file__).parent / "figuras"
K_IMAGEN = Matrix([[6, 24, 1], [13, 16, 10], [20, 17, 15]])  # la del demo, det = 441
MODULOS = (26, 37, 113, 256)
TAMANOS = (2, 3, 4)


# --- 1. ¿Qué proporción de matrices sirve como clave? -------------------------

def proporcion_teorica(n: int, m: int) -> Fraction:
    """Fracción de matrices n×n con entradas en Z_m que son invertibles mod m.

    Para cada primo p que divide a m, la matriz tiene que ser invertible mod p,
    y eso pasa con probabilidad (1 − 1/p)(1 − 1/p²)…(1 − 1/pⁿ): la primera
    columna no puede ser 0, la segunda no puede ser múltiplo de la primera, etc.
    """
    total = Fraction(1)
    for p in primefactors(m):
        for k in range(1, n + 1):
            total *= 1 - Fraction(1, p**k)
    return total


def proporcion_simulada(n: int, m: int, muestras: int, rng) -> float:
    """Sortea matrices al azar y cuenta cuántas pasan es_clave_valida."""
    validas = sum(
        es_clave_valida(Matrix(rng.integers(0, m, (n, n)).tolist()), m) for _ in range(muestras)
    )
    return validas / muestras


# --- 2. ¿Cuánto texto conocido necesita el ataque? ----------------------------

def bloques_para_atacar(n: int, alfabeto, rng, max_bloques: int = 40) -> int:
    """Cifra un mensaje al azar con una clave al azar y devuelve cuántos bloques
    conocidos (desde el inicio) necesitó recuperar_clave para sacar la clave."""
    m = alfabeto.mod
    while True:
        K = Matrix(rng.integers(0, m, (n, n)).tolist())
        if es_clave_valida(K, m):
            break
    simbolos = alfabeto.simbolos
    mensaje = "".join(simbolos[i] for i in rng.integers(0, m, n * max_bloques))
    cifrado = cifrar(mensaje, K, alfabeto)
    for k in range(n, max_bloques + 1):
        try:
            K_recuperada = recuperar_clave(mensaje[: k * n], cifrado[: k * n], n, alfabeto)
        except ValueError:
            continue
        assert K_recuperada == K
        return k
    raise RuntimeError("No se recuperó la clave")


# --- 3. ¿Cuánto se parecen los píxeles vecinos? -------------------------------

def correlacion_vecinos(img: np.ndarray, distancia: int = 1) -> float:
    """Correlación entre cada valor de color y el del píxel que está `distancia`
    lugares a su derecha. Con distancia = n se compara cada píxel con el que ocupa
    su mismo lugar en el bloque siguiente."""
    a = img[:, :-distancia].astype(float).ravel()
    b = img[:, distancia:].astype(float).ravel()
    return float(np.corrcoef(a, b)[0, 1])


# --- Figuras ------------------------------------------------------------------

def figura_claves_validas(tabla):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.4, 2.9), dpi=200)
    ancho = 0.2
    colores = ["#1f4e79", "#4f81bd", "#9bbbd9", "#c0504d"]
    for i, m in enumerate(MODULOS):
        valores = [100 * float(tabla[(n, m)]) for n in TAMANOS]
        x = np.arange(len(TAMANOS)) + (i - 1.5) * ancho
        barras = ax.bar(x, valores, ancho, label=f"m = {m}", color=colores[i])
        ax.bar_label(barras, fmt="%.0f%%", fontsize=7, padding=1)
    ax.set_xticks(range(len(TAMANOS)), [f"{n}×{n}" for n in TAMANOS])
    ax.set_ylabel("matrices que sirven (%)")
    ax.set_ylim(0, 112)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(ncol=4, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.13))
    fig.tight_layout()
    fig.savefig(FIGURAS / "claves_validas.png")
    plt.close(fig)


def figura_histogramas(imagenes):
    import matplotlib.pyplot as plt

    fig, ejes = plt.subplots(1, 3, figsize=(7.2, 2.2), dpi=200, sharey=True)
    for ax, (nombre, img) in zip(ejes, imagenes.items()):
        ax.hist(img[:, :, 0].ravel(), bins=64, range=(0, 256), color="#c0504d")
        ax.set_title(nombre, fontsize=9)
        ax.set_xlim(0, 255)
        ax.set_xlabel("valor del rojo", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.spines[["top", "right"]].set_visible(False)
    ejes[0].set_ylabel("píxeles", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURAS / "histogramas.png")
    plt.close(fig)


def figura_diagrama_flujo():
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Polygon

    fig, ax = plt.subplots(figsize=(7.2, 7.6), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 106)
    ax.axis("off")
    azul, claro, rojo = "#1f4e79", "#e8f0f8", "#c0504d"

    def caja(x, y, texto, funcion=None, ancho=34, alto=7, color=claro, borde=azul):
        ax.add_patch(FancyBboxPatch((x - ancho / 2, y - alto / 2), ancho, alto,
                                    boxstyle="round,pad=0.4,rounding_size=1.2",
                                    fc=color, ec=borde, lw=1.1))
        if funcion:
            ax.text(x, y + 1.3, texto, ha="center", va="center", fontsize=7.6)
            ax.text(x, y - 1.7, funcion, ha="center", va="center", fontsize=6.6,
                    family="monospace", color=azul)
        else:
            ax.text(x, y, texto, ha="center", va="center", fontsize=7.6)

    def rombo(x, y, texto, funcion, ancho=34, alto=11):
        ax.add_patch(Polygon([(x - ancho / 2, y), (x, y + alto / 2), (x + ancho / 2, y),
                              (x, y - alto / 2)], fc="#fff7e0", ec="#b8860b", lw=1.1))
        ax.text(x, y + 1.0, texto, ha="center", va="center", fontsize=7.6)
        ax.text(x, y - 2.0, funcion, ha="center", va="center", fontsize=6.6,
                family="monospace", color=azul)

    def linea(x1, y1, x2, y2):
        ax.plot([x1, x2], [y1, y2], color="#444", lw=0.9)

    def flecha(x1, y1, x2, y2, texto=None, lado="right"):
        ax.annotate("", (x2, y2), (x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color="#444", lw=0.9, shrinkA=0, shrinkB=0))
        if texto:
            dx = 1.2 if lado == "right" else -1.2
            ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + 0.8, texto, fontsize=7,
                    ha="left" if lado == "right" else "right", color="#444")

    # Columna principal: cifrar y descifrar texto
    ax.text(28, 104, "Cifrar y descifrar texto", ha="center", fontsize=9, weight="bold", color=azul)
    caja(28, 97, "Entrada: mensaje, clave K (n×n)\ny alfabeto (m = 26, 37 o 113)",
         ancho=40, alto=8, color="#ffffff")
    flecha(28, 93, 28, 89.5)
    caja(28, 86, "Limpiar el texto y rellenar\nhasta múltiplo de n", "preparar_mensaje", ancho=40, alto=9)
    flecha(28, 81.5, 28, 78.5)
    rombo(28, 73, "¿mcd(det K, m) = 1?", "validar_clave")
    flecha(45, 73, 50.5, 73, "no")
    caja(59.5, 73, "Error: la clave\nno tiene inversa\nmódulo m", ancho=16, alto=10,
         color="#fbeaea", borde=rojo)
    flecha(28, 67.5, 28, 63.5, "sí")
    caja(28, 60, "Símbolos → números → bloques de n", "texto_a_numeros, _bloques", ancho=40)
    flecha(28, 56.5, 28, 52.5)
    rombo(28, 47, "¿Cifrar o descifrar?", "cifrar / descifrar")
    # rama cifrar (izquierda) y descifrar (derecha)
    flecha(11, 47, 11, 33.5, "cifrar", lado="right")
    caja(11, 30, "C = K · P  (mod m)", "multiplicar_bloques", ancho=20)
    linea(45, 47, 47, 47)
    flecha(47, 47, 47, 42.5, "descifrar")
    caja(47, 38, "K⁻¹ = det(K)⁻¹ · adj(K)", "inversa_mod", ancho=24)
    flecha(47, 34.5, 47, 30.5)
    caja(47, 27, "P = K⁻¹ · C  (mod m)", "multiplicar_bloques", ancho=24)
    flecha(11, 26.5, 22, 17.5)
    flecha(47, 23.5, 34, 17.5)
    caja(28, 14, "Números → símbolos", "numeros_a_texto", ancho=30)
    flecha(28, 10.5, 28, 7.5)
    caja(28, 4, "Salida: texto cifrado o descifrado", ancho=40, color="#ffffff")

    # Columna derecha: ataque e imágenes, que reutilizan las mismas piezas
    ax.text(85, 104, "Ataque", ha="center", fontsize=9, weight="bold", color=azul)
    caja(85, 97, "Texto conocido y\nsu cifrado", ancho=24, alto=8, color="#ffffff")
    flecha(85, 92.5, 85, 89.5)
    caja(85, 85.5, "Elegir n bloques con\nP invertible", "recuperar_clave", ancho=24, alto=9)
    flecha(85, 80.5, 85, 77.5)
    caja(85, 74, "K = C · P⁻¹ (mod m)", "inversa_mod", ancho=24)

    ax.text(85, 62, "Imágenes", ha="center", fontsize=9, weight="bold", color=azul)
    caja(85, 55, "Imagen → canales R, G, B\n(valores de 0 a 255)", ancho=24, alto=8,
         color="#ffffff")
    flecha(85, 50.5, 85, 47.5)
    caja(85, 43.5, "¿det K impar?", "validar_clave_imagen", ancho=24)
    flecha(85, 39.5, 85, 36.5)
    caja(85, 31.5, "Bloques de n píxeles:\nc = K · p (mod 256)", "cifrar_imagen", ancho=24, alto=9)
    flecha(85, 26.5, 85, 23.5)
    caja(85, 18.5, "Encadenado:\ncᵢ = K · (pᵢ + cᵢ₋₁)", "cifrar_imagen_encadenado",
         ancho=26, alto=9)

    fig.tight_layout(pad=0.2)
    fig.savefig(FIGURAS / "diagrama_flujo.png")
    plt.close(fig)


# --- Programa principal -------------------------------------------------------

def main():
    rng = np.random.default_rng(2026)

    print("1. Proporción de matrices que sirven como clave (teoría / simulación)")
    print("| Tamaño | " + " | ".join(f"m = {m}" for m in MODULOS) + " |")
    print("|---" * (len(MODULOS) + 1) + "|")
    tabla = {}
    for n in TAMANOS:
        celdas = []
        for m in MODULOS:
            tabla[(n, m)] = teoria = proporcion_teorica(n, m)
            simulada = proporcion_simulada(n, m, 4000, rng)
            celdas.append(f"{100 * float(teoria):.1f} % / {100 * simulada:.1f} %")
        print(f"| {n}×{n} | " + " | ".join(celdas) + " |")
    print("Comprobación exacta 2×2 mod 26:", proporcion_teorica(2, 26) * 26**4, "claves")

    print("\n2. Bloques conocidos que necesitó el ataque (200 claves y mensajes al azar)")
    print("| Alfabeto | n | Mínimo posible | Promedio | Bastó con n bloques | Máximo |")
    print("|---|---|---|---|---|---|")
    for alfabeto in (LETRAS, ALFANUMERICO, COMPLETO):
        for n in TAMANOS:
            k = np.array([bloques_para_atacar(n, alfabeto, rng) for _ in range(200)])
            print(f"| {alfabeto.nombre} (m = {alfabeto.mod}) | {n} | {n} bloques ({n * n} símbolos) "
                  f"| {k.mean():.2f} bloques ({k.mean() * n:.1f} símbolos) "
                  f"| {100 * np.mean(k == n):.0f} % | {k.max()} |")

    print("\n3. Correlación entre píxeles vecinos (imagen de prueba 300×200)")
    img = imagen_de_prueba()
    imagenes = {
        "Original": img,
        "Cifrada (bloque por bloque)": cifrar_imagen(img, K_IMAGEN),
        "Cifrada encadenada": cifrar_imagen_encadenado(img, K_IMAGEN),
    }
    n = K_IMAGEN.shape[0]
    print(f"| Imagen | Con el píxel de al lado | Con el píxel {n} lugares a la derecha | Colores distintos |")
    print("|---|---|---|---|")
    for nombre, im in imagenes.items():
        colores = len(np.unique(im.reshape(-1, 3), axis=0))
        print(f"| {nombre} | {correlacion_vecinos(im):.3f} | {correlacion_vecinos(im, n):.3f} | {colores} |")

    figura_claves_validas(tabla)
    figura_histogramas(imagenes)
    figura_diagrama_flujo()
    print("\nFiguras guardadas en", FIGURAS)


if __name__ == "__main__":
    main()
