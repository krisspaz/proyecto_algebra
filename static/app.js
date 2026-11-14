// La matemática se hace en Python (hill.py). Este archivo solo lee lo que
// escribe el usuario, llama a la API y pinta la respuesta. Todo el texto se
// inserta con textContent: el alfabeto completo incluye < > & " y no debe
// interpretarse como HTML.

// Claves de ejemplo válidas en los tres alfabetos (det coprimo con 26, 37 y 113)
const CLAVES_INICIALES = {
  2: [[3, 2], [5, 7]],
  3: [[2, 5, 7], [3, 8, 1], [4, 6, 11]],
  4: [[1, 2, 0, 1], [0, 1, 3, 2], [2, 0, 1, 1], [1, 3, 1, 0]],
};

const ALFABETOS = Object.fromEntries(window.ALFABETOS.map((a) => [a.clave, a]));

const estado = {
  alfabeto: document.querySelector('input[name="alfabeto"]:checked').value,
  modo: "cifrar",
  clave: copiar(CLAVES_INICIALES[3]),
};

const $ = (id) => document.getElementById(id);
const entrada = $("entrada");
const salida = $("salida");

let ultimaPeticion = 0;
let espera;

function copiar(matriz) {
  return matriz.map((fila) => [...fila]);
}

// El espacio también es un símbolo: se muestra como ␣ para que se vea
function visible(texto) {
  return texto.replaceAll(" ", "␣");
}

function tupla(valores) {
  return `(${valores.join(", ")})`;
}

function crear(etiqueta, clase, texto) {
  const el = document.createElement(etiqueta);
  if (clase) el.className = clase;
  if (texto !== undefined) el.textContent = texto;
  return el;
}

async function api(ruta, opciones = {}) {
  try {
    const respuesta = await fetch(ruta, {
      ...opciones,
      headers: { "Content-Type": "application/json" },
    });
    return await respuesta.json();
  } catch {
    return { ok: false, error: "No hay conexión con el servidor. ¿Sigue abierto app.py?" };
  }
}

function mostrarError(id, mensaje) {
  const el = $(id);
  el.hidden = !mensaje;
  el.textContent = mensaje || "";
}

// --- Alfabeto ---------------------------------------------------------------

function pintarAlfabeto() {
  const alfabeto = ALFABETOS[estado.alfabeto];
  $("tira").replaceChildren(
    ...[...alfabeto.simbolos].map((s, i) => {
      const li = crear("li");
      li.append(crear("b", "", visible(s)), crear("small", "", String(i)));
      return li;
    })
  );
  $("nota-alfabeto").textContent = `${alfabeto.mod} símbolos. ${alfabeto.descripcion}`;
  document.querySelectorAll("[data-mod]").forEach((el) => (el.textContent = alfabeto.mod));
}

// --- Matrices ---------------------------------------------------------------

function pintarMatriz(destino, valores) {
  destino.style.setProperty("--n", valores.length);
  destino.replaceChildren(...valores.flat().map((x) => crear("span", "", String(x))));
}

function pintarClave() {
  const matriz = $("matriz");
  matriz.style.setProperty("--n", estado.clave.length);
  matriz.replaceChildren();
  estado.clave.forEach((fila, i) =>
    fila.forEach((valor, j) => {
      const casilla = document.createElement("input");
      casilla.type = "number";
      casilla.inputMode = "numeric";
      casilla.value = valor;
      casilla.setAttribute("aria-label", `Fila ${i + 1}, columna ${j + 1}`);
      casilla.addEventListener("input", () => {
        estado.clave[i][j] = casilla.value;
        programar();
      });
      matriz.appendChild(casilla);
    })
  );
}

function pintarInversa(inversa) {
  $("bloque-inversa").hidden = !inversa;
  if (inversa) pintarMatriz($("inversa"), inversa);
}

function pintarEstado(r) {
  const el = $("estado");
  if (r.det === undefined) {
    el.className = "estado";
    el.replaceChildren();
    return;
  }
  const calculo = crear("span", "mate", `det K = ${r.det} ≡ ${r.det_mod} (mod ${r.mod})`);
  const explicacion = r.valida
    ? `. Como mcd(${r.det_mod}, ${r.mod}) = 1, la clave tiene inversa y sirve.`
    : `. Como mcd(${r.det_mod}, ${r.mod}) = ${r.mcd}, la clave no tiene inversa y no sirve.`;
  el.className = r.valida ? "estado ok" : "estado mal";
  el.replaceChildren(calculo, explicacion);
  $("matriz").classList.toggle("mala", !r.valida);
}

// --- Mensaje y paso a paso --------------------------------------------------

function pintarIgnorados(ignorados) {
  const el = $("ignorados");
  el.hidden = !ignorados || !ignorados.length;
  if (!el.hidden) {
    el.textContent = `No se cifran con este alfabeto: ${ignorados.map((s) => (s.length === 1 ? visible(s) : s)).join(", ")}`;
  }
}

function pintarPasos(r) {
  const nota = $("nota-pasos");
  const lista = $("pasos");
  if (!r.ok || !r.pasos || !r.pasos.length) {
    lista.replaceChildren();
    nota.textContent = r.ok ? "Escribe un mensaje para ver cada bloque." : "";
    return;
  }
  const cifrando = estado.modo === "cifrar";
  const matrizUsada = cifrando ? "K" : "K⁻¹";
  const letra = cifrando ? "p" : "c";
  const n = estado.clave.length;
  const relleno = ALFABETOS[estado.alfabeto].relleno === " " ? "espacios" : "X";

  let texto = `El texto se reparte en bloques de ${n} símbolos y cada bloque se multiplica por ${matrizUsada}.`;
  if (cifrando) texto += ` Si al último bloque le faltan símbolos, se completa con ${relleno}.`;
  if (r.total_bloques > r.pasos.length) texto += ` Se muestran ${r.pasos.length} de ${r.total_bloques} bloques.`;
  nota.textContent = texto;

  // Cada bloque se dibuja como la multiplicación del pizarrón:
  //   HE   p = [7 4]ᵀ   K · p = [33 34]ᵀ ≡ [7 8]ᵀ   →  HI
  lista.replaceChildren(
    ...r.pasos.map((p) => {
      const li = crear("li", "paso");
      li.append(
        crear("span", "bloque-texto", visible(p.bloque)),
        termino(crear("span", "var", letra), crear("span", "signo", "="), vectorColumna(p.vector)),
        termino(
          crear("span", "clave-var", matrizUsada),
          crear("span", "signo", "·"),
          crear("span", "var", letra),
          crear("span", "signo", "="),
          vectorColumna(p.producto, "sin-reducir"),
          crear("span", "signo", "≡"),
          vectorColumna(p.reducido)
        ),
        crear("span", "signo", "→"),
        crear("span", "bloque-salida", visible(p.salida))
      );
      return li;
    })
  );
}

function vectorColumna(valores, clase = "") {
  const v = crear("span", `matriz vector ${clase}`.trim());
  v.style.setProperty("--n", 1);
  v.setAttribute("aria-label", tupla(valores));
  v.append(...valores.map((x) => crear("span", "", String(x))));
  return v;
}

function termino(...partes) {
  const t = crear("span", "termino");
  t.append(...partes);
  return t;
}

function pintarTextos() {
  const cifrando = estado.modo === "cifrar";
  $("etiqueta-entrada").textContent = cifrando ? "Texto a cifrar" : "Texto cifrado";
  $("etiqueta-salida").textContent = cifrando ? "Texto cifrado" : "Texto descifrado";
  $("invertir").textContent = cifrando ? "Descifrar este resultado" : "Cifrar este resultado";
}

async function procesar() {
  const id = ++ultimaPeticion;
  const r = await api("/api/procesar", {
    method: "POST",
    body: JSON.stringify({
      texto: entrada.value,
      clave: estado.clave,
      alfabeto: estado.alfabeto,
      modo: estado.modo,
    }),
  });
  if (id !== ultimaPeticion) return; // ya llegó una respuesta más nueva

  pintarEstado(r);
  pintarInversa(r.inversa);
  pintarIgnorados(r.ignorados);
  pintarPasos(r);
  mostrarError("error", r.ok ? "" : r.error);

  const nuevo = r.ok ? r.resultado : "";
  if (salida.textContent !== nuevo) {
    salida.textContent = nuevo;
    salida.classList.remove("cambio");
    void salida.offsetWidth; // reinicia la animación
    salida.classList.add("cambio");
  }

  // si hay una imagen abierta y cambió la clave, se vuelve a cifrar
  if (imagen.fuente && JSON.stringify(estado.clave) !== imagen.clave) programarImagen();
}

function programar() {
  clearTimeout(espera);
  espera = setTimeout(procesar, 120);
}

// --- Ataque -----------------------------------------------------------------

async function atacar() {
  const r = await api("/api/atacar", {
    method: "POST",
    body: JSON.stringify({
      texto_plano: $("ataque-plano").value,
      texto_cifrado: $("ataque-cifrado").value,
      n: estado.clave.length,
      alfabeto: estado.alfabeto,
    }),
  });
  $("ataque-resultado").hidden = !r.ok;
  mostrarError("ataque-error", r.ok ? "" : r.error);
  if (!r.ok) return;

  pintarMatriz($("ataque-matriz"), r.clave);
  const mod = ALFABETOS[estado.alfabeto].mod;
  const actual = estado.clave.map((fila) => fila.map((x) => ((Number(x) % mod) + mod) % mod));
  const coincide = JSON.stringify(actual) === JSON.stringify(r.clave);
  const veredicto = $("ataque-veredicto");
  veredicto.className = coincide ? "estado ok" : "estado";
  veredicto.textContent = coincide
    ? "Es exactamente la clave que estás usando (módulo m). El cifrado está roto."
    : "Esta es la clave que encaja con los textos dados. No coincide con la clave de arriba: revisa que el cifrado sea de este mensaje.";
}

// --- Imágenes ---------------------------------------------------------------
// Se cifran en Python con la clave de arriba (mod 256). Al hacer clic en la
// original se pide la cuenta del bloque de píxeles que cae en ese punto.

const imagen = { fuente: null, clave: "", fila: null, columna: null, peticion: 0 };
const CANALES = [
  { nombre: "rojo", clase: "r" },
  { nombre: "verde", clase: "g" },
  { nombre: "azul", clase: "b" },
];
let esperaImagen;

async function procesarImagen() {
  if (!imagen.fuente) return;
  const id = ++imagen.peticion;
  imagen.clave = JSON.stringify(estado.clave);
  const datos = new FormData();
  datos.append("clave", imagen.clave);
  if (imagen.fuente instanceof File) datos.append("archivo", imagen.fuente);
  if (imagen.fila !== null) {
    datos.append("fila", imagen.fila);
    datos.append("columna", imagen.columna);
  }
  $("imagen-estado").className = "estado";
  $("imagen-estado").textContent = "Cifrando la imagen…";

  let r;
  try {
    r = await (await fetch("/api/imagen", { method: "POST", body: datos })).json();
  } catch {
    r = { ok: false, error: "No hay conexión con el servidor. ¿Sigue abierto app.py?" };
  }
  if (id !== imagen.peticion) return; // ya llegó una respuesta más nueva

  pintarEstadoImagen(r);
  mostrarError("imagen-error", r.ok ? "" : r.error);
  $("imagen-resultado").hidden = !r.ok;
  if (!r.ok) return;

  for (const nombre of ["original", "cifrada", "encadenada", "descifrada"]) {
    $(`imagen-${nombre}`).src = r[nombre];
  }
  $("imagen-identica").textContent = r.identica ? "(idéntica a la original ✓)" : "(no coincide con la original)";
  pintarBloque(r.bloque, r.ancho, r.alto);
}

function programarImagen() {
  clearTimeout(esperaImagen);
  esperaImagen = setTimeout(procesarImagen, 250);
}

function pintarEstadoImagen(r) {
  const el = $("imagen-estado");
  if (r.det === undefined) {
    el.className = "estado";
    el.replaceChildren();
    return;
  }
  const calculo = crear("span", "mate", `det K = ${r.det} ≡ ${r.det_mod} (mod 256)`);
  let texto = r.mcd === 1
    ? ": es impar, así que la clave también sirve para imágenes."
    : `: es par (mcd(${r.det_mod}, 256) = ${r.mcd}), así que no sirve para imágenes.`;
  if (r.ok && r.achicada) texto += ` La foto se achicó a ${r.ancho}×${r.alto} píxeles para que sea rápido.`;
  el.className = r.mcd === 1 ? "estado ok" : "estado mal";
  el.replaceChildren(calculo, texto);
}

function pixel(valores, columna) {
  const [r, g, b] = valores.length === 1 ? [valores[0], valores[0], valores[0]] : valores;
  const casilla = crear("div", "pixel");
  casilla.style.background = `rgb(${r}, ${g}, ${b})`;
  casilla.classList.toggle("oscuro", 0.299 * r + 0.587 * g + 0.114 * b < 140);
  casilla.append(crear("span", "", tupla(valores)), crear("small", "", `col. ${columna}`));
  return casilla;
}

function pintarBloque(b, ancho, alto) {
  const n = b.columnas.length;
  $("bloque-titulo").textContent =
    `Un bloque de cerca: fila ${b.fila}, columnas ${b.columnas[0]} a ${b.columnas[n - 1]}`;
  $("pixeles-original").replaceChildren(...b.original.map((px, i) => pixel(px, b.columnas[i])));
  $("pixeles-cifrado").replaceChildren(...b.cifrado.map((px, i) => pixel(px, b.columnas[i])));

  const canales = b.canales.length === 1 ? [{ nombre: "gris", clase: "" }] : CANALES;
  $("bloque-canales").replaceChildren(
    ...b.canales.map((c, i) => {
      const li = crear("li", "paso");
      li.append(
        crear("span", `canal ${canales[i].clase}`, canales[i].nombre),
        termino(
          crear("span", "clave-var", "K"),
          crear("span", "signo", "·"),
          vectorColumna(c.p),
          crear("span", "signo", "="),
          vectorColumna(c.Kp, "sin-reducir"),
          crear("span", "signo", "≡"),
          vectorColumna(c.c)
        )
      );
      return li;
    })
  );

  // marca en la original dónde está el bloque
  const marca = $("imagen-marca") || crear("span", "marca");
  marca.id = "imagen-marca";
  marca.style.left = `${((b.columnas[0] + n / 2) / ancho) * 100}%`;
  marca.style.top = `${((b.fila + 0.5) / alto) * 100}%`;
  $("imagen-original-boton").append(marca);
}

function elegirImagen(fuente) {
  imagen.fuente = fuente;
  imagen.fila = imagen.columna = null; // el servidor elige un bloque de ejemplo
  procesarImagen();
}

// --- Eventos ----------------------------------------------------------------

$("imagen-ejemplo").addEventListener("click", () => elegirImagen("ejemplo"));

$("imagen-archivo").addEventListener("change", (e) => {
  if (e.target.files.length) elegirImagen(e.target.files[0]);
  e.target.value = ""; // permite volver a elegir el mismo archivo
});

$("imagen-original-boton").addEventListener("click", (e) => {
  const img = $("imagen-original");
  const caja = img.getBoundingClientRect();
  if (!img.naturalWidth || !caja.width) return;
  const x = e.clientX ? (e.clientX - caja.left) / caja.width : 0.5;
  const y = e.clientY ? (e.clientY - caja.top) / caja.height : 0.5;
  imagen.columna = Math.floor(Math.min(Math.max(x, 0), 0.9999) * img.naturalWidth);
  imagen.fila = Math.floor(Math.min(Math.max(y, 0), 0.9999) * img.naturalHeight);
  procesarImagen();
});

document.querySelectorAll('input[name="alfabeto"]').forEach((radio) =>
  radio.addEventListener("change", () => {
    estado.alfabeto = radio.value;
    pintarAlfabeto();
    procesar();
  })
);

document.querySelectorAll('input[name="tamano"]').forEach((radio) =>
  radio.addEventListener("change", () => {
    estado.clave = copiar(CLAVES_INICIALES[Number(radio.value)]);
    pintarClave();
    procesar();
  })
);

document.querySelectorAll('input[name="modo"]').forEach((radio) =>
  radio.addEventListener("change", () => {
    estado.modo = radio.value;
    pintarTextos();
    procesar();
  })
);

$("aleatoria").addEventListener("click", async () => {
  const r = await api(`/api/clave-aleatoria?n=${estado.clave.length}&alfabeto=${estado.alfabeto}`);
  if (!r.ok) return mostrarError("error", r.error);
  estado.clave = r.clave;
  pintarClave();
  procesar();
});

$("invertir").addEventListener("click", () => {
  entrada.value = salida.textContent;
  estado.modo = estado.modo === "cifrar" ? "descifrar" : "cifrar";
  document.querySelector(`input[name="modo"][value="${estado.modo}"]`).checked = true;
  pintarTextos();
  procesar();
});

$("copiar").addEventListener("click", async () => {
  const boton = $("copiar");
  try {
    await navigator.clipboard.writeText(salida.textContent);
    boton.textContent = "Copiado";
  } catch {
    boton.textContent = "No se pudo copiar";
  }
  setTimeout(() => (boton.textContent = "Copiar"), 1500);
});

$("ataque-rellenar").addEventListener("click", () => {
  const cifrando = estado.modo === "cifrar";
  $("ataque-plano").value = cifrando ? entrada.value : salida.textContent;
  $("ataque-cifrado").value = cifrando ? salida.textContent : entrada.value;
});

$("ataque-lanzar").addEventListener("click", atacar);

entrada.addEventListener("input", programar);

pintarAlfabeto();
pintarClave();
pintarTextos();
procesar();
