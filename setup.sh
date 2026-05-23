#!/usr/bin/env bash
# setup.sh — Instalador de historias-ig-skill (macOS / Linux)
# Uso:  chmod +x setup.sh && ./setup.sh
set -e

PROJ="$(cd "$(dirname "$0")" && pwd)"
echo ""
echo "  Instalando historias-ig-skill..."
echo ""

# 1) Python 3.10+
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "  [x] Necesitas Python 3.10+ . Instalalo desde https://python.org"
  exit 1
fi
echo "  [ok] Python detectado ($PY)"

# 2) Dependencias
"$PY" -m pip install --quiet "pillow>=10.0.0"
echo "  [ok] Dependencias instaladas (Pillow)"

# 3) Fuentes (Space Grotesk)
mkdir -p "$PROJ/fonts"
descargar() { [ -f "$2" ] || curl -fsSL "$1" -o "$2"; }
descargar "https://fonts.gstatic.com/s/spacegrotesk/v22/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj7oUUsj.ttf" "$PROJ/fonts/SpaceGrotesk-Variable.ttf"
descargar "https://fonts.gstatic.com/s/spacegrotesk/v22/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj4PVksj.ttf" "$PROJ/fonts/SpaceGrotesk-Bold.ttf"
echo "  [ok] Fuentes listas"

# 4) Instalar el comando /historias-ig
DEST="$HOME/.claude/commands/historias-ig.md"
mkdir -p "$(dirname "$DEST")"
sed "s|{{PROJ_DIR}}|$PROJ|g" "$PROJ/skill/historias-ig.md" > "$DEST"
echo "  [ok] Comando instalado en $DEST"

# 5) .env
if [ ! -f "$PROJ/.env" ]; then
  cp "$PROJ/.env.example" "$PROJ/.env"
  echo "  [ok] .env creado (agrega tus claves)"
fi

echo ""
echo "  Listo. Cierra y vuelve a abrir Claude Code, luego escribe: /historias-ig"
echo ""
