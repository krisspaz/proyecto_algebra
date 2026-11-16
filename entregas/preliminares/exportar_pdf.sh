#!/bin/bash
# Arma preliminares.pdf a partir de preliminares.md: pandoc -> HTML (MathJax) -> Chromium headless.
set -e
cd "$(dirname "$0")"

HTML="$PWD/.preliminares.html"
CSS="$PWD/.preliminares.css"
CHROME="/Applications/Chromium.app/Contents/MacOS/Chromium"
[ -x "$CHROME" ] || CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

cat > "$CSS" <<'EOF'
:root {
  --acento: #1f4e79;
  --acento-claro: #e8f0f8;
  --texto: #1d1d1f;
  --gris: #5f6368;
  --linea: #d5dbe1;
}
@page {
  size: letter;
  margin: 2cm 2.1cm 2.2cm;
  @bottom-left  { content: "Grupo 15 · Cifrado de Hill · Preliminares";
                  font: 8pt "Avenir Next", sans-serif; color: #8a9099; }
  @bottom-right { content: counter(page) " / " counter(pages);
                  font: 8pt "Avenir Next", sans-serif; color: #8a9099; }
}
html { font-size: 10.6pt; }
body {
  font-family: "Charter", "Iowan Old Style", Georgia, serif;
  color: var(--texto); line-height: 1.5; max-width: none; margin: 0; padding: 0;
  hyphens: auto; text-align: justify;
}
h1, h2, h3, .sobretitulo, .entrega, .ficha, th, figcaption, .repo {
  font-family: "Avenir Next", "Helvetica Neue", sans-serif;
}

/* ---------- portada ---------- */
.portada {
  border-top: 5px solid var(--acento);
  padding-top: 1.1em; margin-bottom: 1.6em; text-align: left;
}
.sobretitulo {
  text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.78em;
  color: var(--gris); margin: 0 0 0.6em; font-weight: 500;
}
.titulo {
  font-size: 2.5em; line-height: 1.05; margin: 0; color: var(--acento); font-weight: 700;
}
.subtitulo { font-size: 1.25em; margin: 0.2em 0 0.1em; color: var(--texto); font-style: italic; }
.entrega {
  display: inline-block; margin: 0.8em 0 1.2em; padding: 0.2em 0.75em;
  background: var(--acento); color: white; font-size: 0.82em; font-weight: 600;
  letter-spacing: 0.05em; border-radius: 3px;
}
.ficha { display: flex; margin-bottom: 1.1em; border: 1px solid var(--linea); border-radius: 4px; }
.ficha > div { flex: 1; padding: 0.5em 0.9em; border-right: 1px solid var(--linea); }
.ficha > div:first-child { flex: 0 0 5.5em; }
.ficha > div:last-child { border-right: none; }
.ficha .etq {
  display: block; font-size: 0.68em; text-transform: uppercase; letter-spacing: 0.12em; color: var(--gris);
}
.ficha .val { display: block; font-size: 1.05em; font-weight: 600; color: var(--texto); }
.ficha > div:first-child .val { font-size: 1.5em; color: var(--acento); line-height: 1.1; }
table.integrantes { width: 60%; margin: 0 0 0.8em; font-size: 0.95em; }
table.integrantes td:last-child, table.integrantes th:last-child {
  text-align: right; font-variant-numeric: tabular-nums;
}
.repo { font-size: 0.85em; color: var(--gris); margin: 0; text-align: left; }
.repo a { color: var(--acento); text-decoration: none; border-bottom: 1px solid var(--linea); }

/* ---------- cuerpo ---------- */
h2 {
  font-size: 1.22em; color: var(--acento); font-weight: 700;
  margin: 1.25em 0 0.45em; padding-bottom: 0.2em; border-bottom: 1.5px solid var(--acento-claro);
  break-after: avoid; text-align: left;
}
p, li { margin: 0.4em 0; }
ol, ul { padding-left: 1.4em; }
li::marker { color: var(--acento); font-weight: 600; }
strong { color: #000; }

.teorema {
  margin: 0.9em 0; padding: 0.6em 1em; background: var(--acento-claro);
  border-left: 4px solid var(--acento); border-radius: 0 4px 4px 0; break-inside: avoid;
}
.teorema p { margin: 0; }
.ejemplo {
  margin: 0.6em 0; padding: 0.5em 1em 0.5em 0.9em; border: 1px solid var(--linea);
  border-radius: 4px; background: #fafbfc; break-inside: avoid;
}
.ejemplo > p:first-child { margin-top: 0.2em; }
.ejemplo ol { margin: 0.3em 0 0.2em; }

/* ---------- tablas ---------- */
table { border-collapse: collapse; margin: 0.6em 0; font-size: 0.93em; break-inside: avoid; width: 100%; }
col { width: auto !important; }
thead th {
  text-align: left; font-size: 0.82em; text-transform: uppercase; letter-spacing: 0.08em;
  color: var(--acento); border-bottom: 2px solid var(--acento); padding: 4px 10px; background: none;
  hyphens: none; white-space: nowrap;
}
td { padding: 5px 10px; border-bottom: 1px solid var(--linea); text-align: left; vertical-align: top; }
td:nth-child(-n+2) { white-space: nowrap; }

/* ---------- figuras y matemática ---------- */
figure { margin: 0.6em 0; text-align: center; break-inside: avoid; }
figure img { width: 80%; border: 1px solid var(--linea); border-radius: 3px; }
figcaption { font-size: 0.82em; color: var(--gris); margin-top: 0.35em; }
mjx-container[display="true"] { margin: 0.5em 0 !important; }
a { color: var(--acento); }
.izq p { text-align: left; }
EOF

pandoc preliminares.md -s --mathjax="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js" \
  -o "$HTML" -V lang=es --metadata pagetitle="Preliminares - Grupo 15 - Cifrado de Hill" \
  --css "$CSS"

"$CHROME" --headless --disable-gpu --no-sandbox \
  --virtual-time-budget=20000 --run-all-compositor-stages-before-draw \
  --no-pdf-header-footer --print-to-pdf="$PWD/preliminares.pdf" "file://$HTML" 2>/dev/null

rm -f "$HTML" "$CSS"
echo "Listo: $PWD/preliminares.pdf"
