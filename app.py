"""Interfaz web para el cifrado de Hill.

Uso:
    .venv/bin/python app.py      # abre http://127.0.0.1:5050

Variables de entorno opcionales: HOST (por defecto 127.0.0.1) y PORT (5050;
el 5000 lo ocupa AirPlay en macOS).

Toda la matemática vive en hill.py, ataque.py e imagen.py; aquí solo se
validan las entradas y se da formato a las respuestas.
"""
import base64
import io
import json
import os
import secrets
from math import gcd

import numpy as np
from flask import Flask, jsonify, render_template, request
from PIL import Image, UnidentifiedImageError
from sympy import Matrix
from werkzeug.exceptions import HTTPException

from ataque import recuperar_clave
from hill import (
    ALFABETOS,
    COMPLETO,
    analizar_clave,
    multiplicar_bloques,
    numeros_a_texto,
    preparar_cifrado,
    preparar_mensaje,
    simbolos_ignorados,
)
from imagen import (
    MOD_IMG,
    cifrar_imagen,
    cifrar_imagen_encadenado,
    descifrar_imagen_encadenado,
    explicar_bloque,
    imagen_de_prueba,
)
from inversa import determinante

TAMANOS = (2, 3, 4)
MAX_TEXTO = 5000
MAX_PASOS = 8
MAX_VALOR_CLAVE = 10**6
NOMBRES_INVISIBLES = {"\n": "salto de línea", "\r": "salto de línea", "\t": "tabulación"}
LADO_MAX_IMAGEN = 320  # las fotos se achican para que el cifrado encadenado sea rápido
MAX_PIXELES_ARCHIVO = 40_000_000

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # por las imágenes; los textos tienen su propio límite
app.json.ensure_ascii = False


class EntradaInvalida(ValueError):
    pass


# --- Lectura y validación de entradas ----------------------------------------

def _datos() -> dict:
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        raise EntradaInvalida("El cuerpo de la petición debe ser un objeto JSON.")
    return datos


def _alfabeto(nombre):
    if nombre not in ALFABETOS:
        raise EntradaInvalida("Alfabeto desconocido.")
    return ALFABETOS[nombre]


def _tamano(valor) -> int:
    try:
        n = int(valor)
    except (TypeError, ValueError):
        n = 0
    if n not in TAMANOS:
        raise EntradaInvalida("El tamaño de la clave debe ser 2, 3 o 4.")
    return n


def _texto(valor, campo: str) -> str:
    if not isinstance(valor, str):
        raise EntradaInvalida(f"El campo «{campo}» debe ser texto.")
    if len(valor) > MAX_TEXTO:
        raise EntradaInvalida(f"El texto no puede pasar de {MAX_TEXTO} caracteres.")
    return valor


def _clave(datos) -> Matrix:
    n = len(datos) if isinstance(datos, list) else 0
    if n not in TAMANOS or any(not isinstance(fila, list) or len(fila) != n for fila in datos):
        raise EntradaInvalida("La clave debe ser una matriz cuadrada de 2×2, 3×3 o 4×4.")
    try:
        valores = [[int(x) for x in fila] for fila in datos]
    except (TypeError, ValueError):
        raise EntradaInvalida("Cada casilla de la clave debe tener un número entero.")
    if any(abs(x) > MAX_VALOR_CLAVE for fila in valores for x in fila):
        raise EntradaInvalida("Los números de la clave son demasiado grandes.")
    return Matrix(valores)


def _a_lista(M: Matrix | None):
    return None if M is None else [[int(x) for x in fila] for fila in M.tolist()]


def _nombre_visible(ch: str) -> str:
    return NOMBRES_INVISIBLES.get(ch, ch)


# --- Rutas ------------------------------------------------------------------

@app.get("/")
def inicio():
    alfabetos = [
        dict(clave=a.clave, nombre=a.nombre, simbolos=a.simbolos, mod=a.mod,
             relleno=a.relleno, descripcion=a.descripcion)
        for a in ALFABETOS.values()
    ]
    return render_template("index.html", alfabetos=alfabetos, inicial=COMPLETO.clave)


@app.post("/api/procesar")
def procesar():
    datos = _datos()
    alfabeto = _alfabeto(datos.get("alfabeto"))
    K = _clave(datos.get("clave"))
    modo = datos.get("modo")
    if modo not in ("cifrar", "descifrar"):
        raise EntradaInvalida("El modo debe ser «cifrar» o «descifrar».")
    texto = _texto(datos.get("texto", ""), "texto")

    n = K.shape[0]
    info = analizar_clave(K, alfabeto.mod)
    respuesta = dict(
        mod=alfabeto.mod,
        det=info["det"],
        det_mod=info["det_mod"],
        mcd=info["mcd"],
        valida=info["valida"],
        inversa=_a_lista(info["inversa"]),
        ignorados=sorted({_nombre_visible(ch) for ch in simbolos_ignorados(texto, alfabeto)}),
    )
    if not info["valida"]:
        return jsonify(ok=False, error="Esta clave no tiene inversa: cambia algún número o pulsa «Clave aleatoria».", **respuesta)

    try:
        if modo == "cifrar":
            entrada, M = preparar_mensaje(texto, n, alfabeto), K
        else:
            entrada, M = preparar_cifrado(texto, n, alfabeto), info["inversa"]
    except ValueError as e:
        return jsonify(ok=False, error=str(e), **respuesta)

    if not entrada:
        return jsonify(ok=True, entrada="", resultado="", pasos=[], total_bloques=0, **respuesta)

    P, producto, C = multiplicar_bloques(M, entrada, alfabeto)
    resultado = numeros_a_texto((C[i, j] for j in range(C.cols) for i in range(n)), alfabeto)
    pasos = [
        dict(
            bloque=entrada[j * n:(j + 1) * n],
            vector=[int(x) for x in P.col(j)],
            producto=[int(x) for x in producto.col(j)],
            reducido=[int(x) for x in C.col(j)],
            salida=resultado[j * n:(j + 1) * n],
        )
        for j in range(min(C.cols, MAX_PASOS))
    ]
    return jsonify(ok=True, entrada=entrada, resultado=resultado, pasos=pasos, total_bloques=C.cols, **respuesta)


@app.get("/api/clave-aleatoria")
def clave_aleatoria():
    alfabeto = _alfabeto(request.args.get("alfabeto"))
    n = _tamano(request.args.get("n", 3))
    azar = secrets.SystemRandom()
    while True:  # con m primo casi todas sirven; con m = 26, alrededor de un tercio
        K = Matrix(n, n, lambda i, j: azar.randrange(alfabeto.mod))
        if analizar_clave(K, alfabeto.mod)["valida"]:
            return jsonify(ok=True, clave=_a_lista(K))


@app.post("/api/atacar")
def atacar():
    datos = _datos()
    alfabeto = _alfabeto(datos.get("alfabeto"))
    n = _tamano(datos.get("n"))
    plano = _texto(datos.get("texto_plano", ""), "texto_plano")
    cifrado = _texto(datos.get("texto_cifrado", ""), "texto_cifrado")
    try:
        K = recuperar_clave(plano, cifrado, n, alfabeto)
    except ValueError as e:
        return jsonify(ok=False, error=str(e))
    return jsonify(ok=True, clave=_a_lista(K))


@app.post("/api/imagen")
def imagen():
    """Cifra una imagen con la clave de la página (mod 256).

    Recibe un formulario con `clave` (JSON), `archivo` (opcional; si no viene se
    usa la imagen de prueba) y opcionalmente `fila` y `columna` del bloque que se
    quiere explicar.
    """
    try:
        clave = json.loads(request.form.get("clave", ""))
    except ValueError:
        raise EntradaInvalida("La clave debe venir como JSON.")
    K = _clave(clave)
    det = int(determinante(K.tolist()))
    respuesta = dict(det=det, det_mod=det % MOD_IMG, mcd=gcd(det % MOD_IMG, MOD_IMG))
    if respuesta["mcd"] != 1:
        return jsonify(ok=False, valida=False, error=(
            "Para imágenes la clave necesita det K impar (256 = 2⁸). "
            "Cambia algún número de la clave."), **respuesta)

    archivo = request.files.get("archivo")
    if archivo:
        original, achicada = _leer_imagen(archivo)
    else:
        original, achicada = imagen_de_prueba(), False
    alto, ancho = original.shape[:2]

    fila = _entero(request.form.get("fila"), 60 if not archivo else alto // 2, alto - 1)
    columna = _entero(request.form.get("columna"), 90 if not archivo else ancho // 2, ancho - 1)
    bloque = explicar_bloque(original, K, fila, columna)

    cifrada = cifrar_imagen(original, K)
    encadenada = cifrar_imagen_encadenado(original, K)
    descifrada = descifrar_imagen_encadenado(encadenada, K, ancho=ancho)
    return jsonify(
        ok=True, valida=True, alto=alto, ancho=ancho, achicada=achicada,
        original=_png(original), cifrada=_png(cifrada), encadenada=_png(encadenada),
        descifrada=_png(descifrada), identica=bool(np.array_equal(original, descifrada)),
        bloque=bloque, **respuesta,
    )


def _leer_imagen(archivo) -> tuple[np.ndarray, bool]:
    try:
        img = Image.open(archivo.stream)
        if img.width * img.height > MAX_PIXELES_ARCHIVO:
            raise EntradaInvalida("La imagen es demasiado grande.")
        img = img.convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise EntradaInvalida("No se pudo abrir el archivo como imagen (prueba con PNG o JPG).")
    achicada = max(img.size) > LADO_MAX_IMAGEN
    if achicada:
        img.thumbnail((LADO_MAX_IMAGEN, LADO_MAX_IMAGEN))
    return np.array(img), achicada


def _entero(valor, por_defecto: int, maximo: int) -> int:
    try:
        return min(max(int(valor), 0), maximo)
    except (TypeError, ValueError):
        return por_defecto


def _png(img: np.ndarray) -> str:
    buffer = io.BytesIO()
    Image.fromarray(img).save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


# --- Errores: siempre JSON en /api, sin detalles internos --------------------

@app.errorhandler(EntradaInvalida)
def entrada_invalida(e):
    return jsonify(ok=False, error=str(e)), 400


@app.errorhandler(HTTPException)
def error_http(e):
    if not request.path.startswith("/api/"):
        return e
    mensajes = {404: "Esa ruta no existe.", 405: "Método no permitido.", 413: "La petición es demasiado grande."}
    return jsonify(ok=False, error=mensajes.get(e.code, "Petición no válida.")), e.code


@app.errorhandler(Exception)
def error_interno(e):
    app.logger.exception("Error no controlado")
    return jsonify(ok=False, error="Error interno del servidor."), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 5050)), debug=False)
