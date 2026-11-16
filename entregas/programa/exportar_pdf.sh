#!/bin/bash
# Arma cifrado_hill.pdf a partir del notebook: nbconvert -> HTML -> Chromium headless.
# Requiere nbconvert en el .venv: .venv/bin/pip install nbconvert
set -e
cd "$(dirname "$0")"
RAIZ="$(cd ../.. && pwd)"
CHROME="/Applications/Chromium.app/Contents/MacOS/Chromium"
[ -x "$CHROME" ] || CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

"$RAIZ/.venv/bin/jupyter" nbconvert --to html "$RAIZ/cifrado_hill.ipynb" --output-dir "$PWD" --output .notebook
# que las líneas largas de código hagan salto de línea en vez de cortarse
"$RAIZ/.venv/bin/python" - "$PWD/.notebook.html" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
s = s.replace("</head>", "<style>@media print { pre { white-space: pre-wrap !important; word-break: break-word; }"
              " @page { size: letter; margin: 1.6cm 1.4cm; } }</style></head>", 1)
open(p, "w").write(s)
PY
"$CHROME" --headless --disable-gpu --no-sandbox --virtual-time-budget=15000 \
  --run-all-compositor-stages-before-draw --no-pdf-header-footer \
  --print-to-pdf="$PWD/cifrado_hill.pdf" "file://$PWD/.notebook.html" 2>/dev/null
rm -f "$PWD/.notebook.html"
echo "Listo: $PWD/cifrado_hill.pdf"
