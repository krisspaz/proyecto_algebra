#!/bin/bash
# Arma INFORME.pdf a partir de ../../INFORME.md: pandoc -> HTML -> Chromium headless.
set -e
cd "$(dirname "$0")"
RAIZ="$(cd ../.. && pwd)"

HTML="$PWD/.informe.html"
CSS="$PWD/.informe.css"
CHROME="/Applications/Chromium.app/Contents/MacOS/Chromium"
[ -x "$CHROME" ] || CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

cat > "$CSS" <<'EOF'
:root { --acento: #1f4e79; --acento-claro: #e8f0f8; --texto: #1d1d1f; --gris: #5f6368; --linea: #d5dbe1; }
@page {
  size: letter;
  margin: 2cm 2.1cm 2.2cm;
  @bottom-left  { content: "Grupo 15 · Cifrado de Hill · Reporte final";
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
h1, h2, h3, th, figcaption { font-family: "Avenir Next", "Helvetica Neue", sans-serif; text-align: left; }
h1 { font-size: 2.1em; line-height: 1.1; color: var(--acento); border-top: 5px solid var(--acento);
     padding-top: 0.6em; margin: 0 0 0.6em; }
h2 { font-size: 1.3em; color: var(--acento); margin: 1.4em 0 0.45em; padding-bottom: 0.2em;
     border-bottom: 1.5px solid var(--acento-claro); break-after: avoid; }
h3 { font-size: 1.08em; color: var(--texto); margin: 1.1em 0 0.35em; break-after: avoid; }
p, li { margin: 0.4em 0; }
ol, ul { padding-left: 1.4em; }
li::marker { color: var(--acento); font-weight: 600; }
strong { color: #000; }
a { color: var(--acento); }
code { font-family: "SF Mono", Menlo, monospace; font-size: 0.86em; background: #f3f5f7;
       padding: 0.05em 0.3em; border-radius: 3px; }
pre { background: #f6f8fa; border: 1px solid var(--linea); border-left: 3px solid var(--acento);
      border-radius: 3px; padding: 0.55em 0.9em; overflow-x: auto; break-inside: avoid; text-align: left; }
pre code { background: none; padding: 0; font-size: 0.84em; line-height: 1.45; }
table { border-collapse: collapse; margin: 0.6em 0; font-size: 0.92em; break-inside: avoid; }
col { width: auto !important; }
thead th { text-align: left; font-size: 0.82em; text-transform: uppercase; letter-spacing: 0.06em;
           color: var(--acento); border-bottom: 2px solid var(--acento); padding: 4px 10px; }
td { padding: 4px 10px; border-bottom: 1px solid var(--linea); text-align: left; vertical-align: top; }
figure { margin: 0.8em 0; text-align: center; break-inside: avoid; }
img { max-width: 100% !important; height: auto !important; box-sizing: border-box; }
figure img, p > img { border: 1px solid var(--linea); border-radius: 3px; }
figcaption { font-size: 0.82em; color: var(--gris); margin-top: 0.35em; }
.caratula { height: 23.3cm; display: flex; flex-direction: column; justify-content: center;
            align-items: center; text-align: center; break-after: page; font-family: "Avenir Next", sans-serif; }
.caratula p { text-align: center; margin: 0.3em 0; color: var(--gris); font-size: 1.05em; }
.caratula h1 { font-size: 2.4em; border-top: 5px solid var(--acento); border-bottom: 5px solid var(--acento);
               padding: 0.5em 0; margin: 1.2em 0 0.8em; text-align: center; }
.caratula p strong { color: var(--acento); font-size: 1.3em; }
.caratula table { margin: 0.8em auto 1.6em; font-size: 1.05em; }
.caratula td, .caratula th { text-align: left; }
EOF

pandoc "$RAIZ/INFORME.md" -s --embed-resources --resource-path="$RAIZ" -o "$HTML" -V lang=es \
  --metadata pagetitle="Reporte - Grupo 15 - Cifrado de Hill" --css "$CSS"

"$CHROME" --headless --disable-gpu --no-sandbox \
  --virtual-time-budget=10000 --run-all-compositor-stages-before-draw \
  --no-pdf-header-footer --print-to-pdf="$PWD/INFORME.pdf" "file://$HTML" 2>/dev/null

rm -f "$HTML" "$CSS"
echo "Listo: $PWD/INFORME.pdf"
