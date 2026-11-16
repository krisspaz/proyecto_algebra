"""Pruebas del cifrado, el ataque y la API.

Ejecutar:  .venv/bin/python -m unittest -v
"""
import io
import json
import time
import unittest

import numpy as np
from PIL import Image
from sympy import Matrix, isprime

from app import app
from ataque import recuperar_clave
from hill import (
    ALFABETOS,
    ALFANUMERICO,
    COMPLETO,
    LETRAS,
    cifrar,
    descifrar,
    es_clave_valida,
    limpiar,
    simbolos_ignorados,
)
from imagen import (
    cifrar_imagen,
    cifrar_imagen_encadenado,
    descifrar_imagen_encadenado,
    explicar_bloque,
    imagen_de_prueba,
)
from resultados import correlacion_vecinos, proporcion_teorica

CLAVES = [
    Matrix([[3, 2], [5, 7]]),
    Matrix([[2, 5, 7], [3, 8, 1], [4, 6, 11]]),
    Matrix([[1, 2, 0, 1], [0, 1, 3, 2], [2, 0, 1, 1], [1, 3, 1, 0]]),
]
def lista(K):
    return [[int(x) for x in fila] for fila in K.tolist()]


MENSAJE = "¿Nos vemos mañana? Aula #204, a las 9:30 (¡no faltes!) <b>50€</b> & 20°C"


class TestAlfabetos(unittest.TestCase):
    def test_sin_simbolos_repetidos(self):
        for a in ALFABETOS.values():
            self.assertEqual(len(set(a.simbolos)), a.mod, a.nombre)

    def test_modulos(self):
        self.assertEqual(LETRAS.mod, 26)
        self.assertEqual(ALFANUMERICO.mod, 37)
        self.assertEqual(COMPLETO.mod, 113)
        self.assertTrue(isprime(ALFANUMERICO.mod) and isprime(COMPLETO.mod))

    def test_claves_de_ejemplo_validas_en_todos(self):
        for K in CLAVES:
            for a in ALFABETOS.values():
                self.assertTrue(es_clave_valida(K, a.mod), (K, a.nombre))

    def test_limpiar_segun_alfabeto(self):
        self.assertEqual(limpiar("Ñandú ¿qué?", LETRAS), "NANDUQUE")
        self.assertEqual(limpiar("Ñandú ¿qué?", ALFANUMERICO), "NANDU QUE")
        self.assertEqual(limpiar("Ñandú ¿qué?", COMPLETO), "Ñandú ¿qué?")

    def test_tildes_descompuestas(self):
        # "é" escrita como e + acento combinado (frecuente al pegar texto)
        self.assertEqual(limpiar("café", COMPLETO), "café")

    def test_ignorados(self):
        self.assertEqual(simbolos_ignorados("hola 😀\nadiós 😀", COMPLETO), ["😀", "\n"])
        self.assertEqual(simbolos_ignorados("hola", COMPLETO), [])


class TestCifrado(unittest.TestCase):
    def test_ida_y_vuelta_texto_completo(self):
        for K in CLAVES:
            descifrado = descifrar(cifrar(MENSAJE, K, COMPLETO), K, COMPLETO)
            self.assertEqual(descifrado.rstrip(" "), MENSAJE)

    def test_ida_y_vuelta_otros_alfabetos(self):
        for a in (LETRAS, ALFANUMERICO):
            for K in CLAVES:
                esperado = limpiar(MENSAJE, a)
                descifrado = descifrar(cifrar(MENSAJE, K, a), K, a)
                self.assertTrue(descifrado.startswith(esperado))
                self.assertEqual(len(descifrado) % K.shape[0], 0)

    def test_ejemplo_clasico(self):
        self.assertEqual(cifrar("HELP", Matrix([[3, 3], [2, 5]])), "HIAT")

    def test_clave_invalida(self):
        with self.assertRaises(ValueError):
            cifrar("hola", Matrix([[2, 4], [6, 8]]))
        with self.assertRaises(ValueError):
            cifrar("hola", Matrix([[1, 0], [0, 113]]), COMPLETO)

    def test_longitud_incorrecta_al_descifrar(self):
        with self.assertRaises(ValueError):
            descifrar("ABCD", CLAVES[1])


class TestAtaque(unittest.TestCase):
    def test_recupera_la_clave(self):
        for a in ALFABETOS.values():
            for K in CLAVES:
                if a is LETRAS and K.shape[0] == 4:
                    continue  # el mensaje limpio es corto para 4×4 en mod 26
                c = cifrar(MENSAJE, K, a)
                recuperada = recuperar_clave(MENSAJE, c, K.shape[0], a)
                self.assertEqual(recuperada, K.applyfunc(lambda x: x % a.mod))

    def test_error_explica_por_que_no_se_puede(self):
        # 4 bloques conocidos → una sola P posible, con det P ≡ 10 y mcd(10, 26) = 2
        K = Matrix([[0, 3, 1, 9], [19, 22, 6, 12], [23, 7, 17, 4], [22, 9, 24, 20]])
        plano = "¿Nos vemos mañana? Aula #204"
        cifrado = cifrar(plano, K)[:16]
        with self.assertRaises(ValueError) as ctx:
            recuperar_clave(plano, cifrado, 4)
        mensaje = str(ctx.exception)
        self.assertIn("4 bloques", mensaje)
        self.assertIn("mcd(10, 26) = 2", mensaje)
        self.assertIn("Todo el teclado", mensaje)  # sugiere un módulo primo

    def test_texto_repetitivo_no_se_cuelga(self):
        K = CLAVES[2]
        inicio = time.time()
        with self.assertRaises(ValueError):
            recuperar_clave("A" * 4000, cifrar("A" * 4000, K), 4)
        self.assertLess(time.time() - inicio, 10)


class TestImagenEncadenada(unittest.TestCase):
    def setUp(self):
        # imagen de un solo color con un ancho que no es múltiplo de 3
        self.img = np.full((20, 31, 3), (200, 40, 40), dtype=np.uint8)
        self.K = Matrix([[6, 24, 1], [13, 16, 10], [20, 17, 15]])

    def test_ida_y_vuelta(self):
        cifrada = cifrar_imagen_encadenado(self.img, self.K)
        descifrada = descifrar_imagen_encadenado(cifrada, self.K, ancho=31)
        self.assertTrue(np.array_equal(descifrada, self.img))

    def test_ida_y_vuelta_gris(self):
        gris = self.img[:, :, 0]
        cifrada = cifrar_imagen_encadenado(gris, self.K)
        self.assertTrue(np.array_equal(descifrar_imagen_encadenado(cifrada, self.K, ancho=31), gris))

    def test_bloques_iguales_dan_cifrados_distintos(self):
        sin_encadenar = cifrar_imagen(self.img, self.K)[0, :30].reshape(-1, 3, 3)
        encadenada = cifrar_imagen_encadenado(self.img, self.K)[0, :30].reshape(-1, 3, 3)
        self.assertEqual(len(np.unique(sin_encadenar, axis=0)), 1)
        self.assertGreater(len(np.unique(encadenada, axis=0)), 1)

    def test_explicar_bloque_el_ejemplo_del_informe(self):
        # tres píxeles (200, 40, 40) del círculo rojo, columnas 90 a 92 (INFORME 5.2)
        img = np.full((1, 96, 3), (200, 40, 40), dtype=np.uint8)
        b = explicar_bloque(img, self.K, 0, 91)
        self.assertEqual(b["columnas"], [90, 91, 92])
        self.assertEqual(b["canales"][0]["Kp"], [6200, 7800, 10400])
        self.assertEqual(b["cifrado"], [[56, 216, 216], [120, 24, 24], [160, 32, 32]])

    def test_explicar_bloque_coincide_con_cifrar(self):
        rng = np.random.default_rng(0)
        img = rng.integers(0, 256, (5, 31, 3), dtype=np.uint8)
        cifrada = cifrar_imagen(img, self.K)
        for columna in (0, 14, 30):
            b = explicar_bloque(img, self.K, 2, columna)
            self.assertEqual(b["cifrado"], cifrada[2, b["columnas"]].tolist())


class TestResultados(unittest.TestCase):
    def test_formula_de_claves_validas_coincide_con_contarlas(self):
        # las 26⁴ matrices 2×2: det = ad − bc, y sirven las que tienen mcd(det, 26) = 1
        a, b, c, d = np.meshgrid(*[np.arange(26)] * 4, indexing="ij")
        det = (a * d - b * c) % 26
        validas = int(np.sum((det % 2 != 0) & (det % 13 != 0)))
        self.assertEqual(validas, 157_248)
        self.assertEqual(proporcion_teorica(2, 26) * 26**4, validas)

    def test_encadenar_borra_el_parecido_entre_bloques(self):
        img = imagen_de_prueba()
        K = Matrix([[6, 24, 1], [13, 16, 10], [20, 17, 15]])
        # sin encadenar, cada píxel se parece al del mismo lugar en el bloque siguiente
        self.assertGreater(correlacion_vecinos(cifrar_imagen(img, K), 3), 0.5)
        self.assertLess(abs(correlacion_vecinos(cifrar_imagen_encadenado(img, K), 3)), 0.05)


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.cliente = app.test_client()

    def procesar(self, **datos):
        cuerpo = dict(texto=MENSAJE, clave=lista(CLAVES[1]), alfabeto="completo", modo="cifrar")
        cuerpo.update(datos)
        return self.cliente.post("/api/procesar", json=cuerpo)

    def test_pagina(self):
        r = self.cliente.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Todo el teclado", r.get_data(as_text=True))

    def test_cifrar_y_descifrar(self):
        cifrado = self.procesar().get_json()
        self.assertTrue(cifrado["ok"])
        self.assertEqual(cifrado["mod"], 113)
        descifrado = self.procesar(texto=cifrado["resultado"], modo="descifrar").get_json()
        self.assertEqual(descifrado["resultado"].rstrip(" "), MENSAJE)

    def test_clave_sin_inversa(self):
        r = self.procesar(clave=[[2, 4], [6, 8]], alfabeto="letras").get_json()
        self.assertFalse(r["ok"])
        self.assertFalse(r["valida"])
        self.assertEqual(r["mcd"], 2)

    def test_entradas_invalidas(self):
        casos = [
            dict(clave=[["a", 1], [2, 3]]),
            dict(clave=[[1, 2, 3], [4, 5]]),
            dict(clave=[[1] * 5] * 5),
            dict(alfabeto="klingon"),
            dict(modo="romper"),
            dict(texto=123),
            dict(texto="a" * 6000),
        ]
        for caso in casos:
            r = self.procesar(**caso)
            self.assertEqual(r.status_code, 400, caso)
            self.assertFalse(r.get_json()["ok"])

    def test_cuerpo_no_json(self):
        r = self.cliente.post("/api/procesar", data="hola", content_type="text/plain")
        self.assertEqual(r.status_code, 400)

    def test_ignorados(self):
        r = self.procesar(texto="hola 😀\nchao").get_json()
        self.assertEqual(sorted(r["ignorados"]), ["salto de línea", "😀"])

    def test_clave_aleatoria(self):
        for nombre, a in ALFABETOS.items():
            r = self.cliente.get(f"/api/clave-aleatoria?n=3&alfabeto={nombre}").get_json()
            self.assertTrue(es_clave_valida(Matrix(r["clave"]), a.mod))
        self.assertEqual(self.cliente.get("/api/clave-aleatoria?n=9&alfabeto=letras").status_code, 400)

    def test_atacar(self):
        cifrado = self.procesar().get_json()["resultado"]
        r = self.cliente.post("/api/atacar", json=dict(
            texto_plano=MENSAJE, texto_cifrado=cifrado, n=3, alfabeto="completo",
        )).get_json()
        self.assertTrue(r["ok"])
        self.assertEqual(r["clave"], lista(CLAVES[1]))

    def test_atacar_texto_corto(self):
        r = self.cliente.post("/api/atacar", json=dict(
            texto_plano="ab", texto_cifrado="cd", n=3, alfabeto="completo",
        )).get_json()
        self.assertFalse(r["ok"])

    def imagen(self, clave=((6, 24, 1), (13, 16, 10), (20, 17, 15)), **campos):
        datos = dict(clave=json.dumps(clave), **campos)
        return self.cliente.post("/api/imagen", data=datos, content_type="multipart/form-data")

    def test_imagen_de_ejemplo(self):
        r = self.imagen().get_json()
        self.assertTrue(r["ok"])
        self.assertTrue(r["identica"])
        self.assertEqual(r["det_mod"], 441 % 256)
        self.assertEqual(r["bloque"]["cifrado"], [[56, 216, 216], [120, 24, 24], [160, 32, 32]])
        self.assertTrue(r["encadenada"].startswith("data:image/png;base64,"))

    def test_imagen_subida_y_bloque_elegido(self):
        buffer = io.BytesIO()
        Image.new("RGB", (40, 10), (10, 20, 30)).save(buffer, format="PNG")
        buffer.seek(0)
        r = self.imagen(archivo=(buffer, "foto.png"), fila="3", columna="7").get_json()
        self.assertTrue(r["ok"])
        self.assertEqual((r["alto"], r["ancho"]), (10, 40))
        self.assertEqual(r["bloque"]["columnas"], [6, 7, 8])
        self.assertEqual(r["bloque"]["original"], [[10, 20, 30]] * 3)

    def test_imagen_clave_con_det_par(self):
        r = self.imagen(clave=[[2, 4], [6, 8]]).get_json()
        self.assertFalse(r["ok"])
        self.assertEqual(r["mcd"], 8)

    def test_imagen_archivo_que_no_es_imagen(self):
        r = self.imagen(archivo=(io.BytesIO(b"hola"), "nota.txt"))
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.get_json()["ok"])

    def test_ruta_inexistente_devuelve_json(self):
        r = self.cliente.get("/api/nada")
        self.assertEqual(r.status_code, 404)
        self.assertFalse(r.get_json()["ok"])


if __name__ == "__main__":
    unittest.main()
