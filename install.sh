#!/usr/bin/env bash
#
# install.sh — Instalador de Cyber-RAM para Waybar
#
# Copia los scripts a ~/.config/waybar/scripts/, comprueba dependencias
# y muestra los fragmentos a añadir en config y style.css.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.config/waybar/scripts"

c_red='\033[0;31m'
c_cyan='\033[0;36m'
c_green='\033[0;32m'
c_reset='\033[0m'

echo -e "${c_cyan}╔══════════════════════════════════════╗${c_reset}"
echo -e "${c_cyan}║          CYBER-RAM · INSTALADOR       ║${c_reset}"
echo -e "${c_cyan}╚══════════════════════════════════════╝${c_reset}"
echo

# ── Comprobar dependencias ──────────────────────────────
missing=()
command -v waybar >/dev/null 2>&1 || missing+=("waybar")
command -v python3 >/dev/null 2>&1 || missing+=("python3")
python3 -c "import gi; gi.require_version('Gtk','3.0'); gi.require_version('WebKit2','4.0')" >/dev/null 2>&1 \
  || missing+=("python-gobject + webkit2gtk")

if [ "${#missing[@]}" -gt 0 ]; then
  echo -e "${c_red}⚠ Faltan dependencias:${c_reset}"
  printf '  - %s\n' "${missing[@]}"
  echo
  echo "En Arch / CachyOS:"
  echo "  sudo pacman -S waybar python-gobject webkit2gtk"
  echo
  read -r -p "¿Continuar de todas formas? [y/N] " ans
  [[ "$ans" =~ ^[Yy]$ ]] || exit 1
fi

# ── Copiar archivos ──────────────────────────────────────
mkdir -p "$TARGET_DIR"
cp "$REPO_DIR/scripts/ram-status.sh"   "$TARGET_DIR/"
cp "$REPO_DIR/waybar/ram-popup.py"     "$TARGET_DIR/"
cp "$REPO_DIR/waybar/ram-popup.html"   "$TARGET_DIR/"
chmod +x "$TARGET_DIR/ram-status.sh" "$TARGET_DIR/ram-popup.py"

echo -e "${c_green}✓ Archivos copiados a $TARGET_DIR${c_reset}"
echo

# ── Instrucciones manuales ──────────────────────────────
echo -e "${c_cyan}Pasos restantes (manuales):${c_reset}"
echo
echo "1. Añade este bloque dentro de \"modules\" en ~/.config/waybar/config:"
echo "   (contenido en waybar/config-snippet.jsonc)"
echo
echo "2. Añade \"custom/cyber-ram\" al array modules-left/center/right"
echo "   de tu config, donde quieras que aparezca."
echo
echo "3. Añade el contenido de waybar/style-snippet.css al final de"
echo "   ~/.config/waybar/style.css"
echo
echo "4. Recarga Waybar:"
echo "   killall waybar && waybar &"
echo
echo -e "${c_green}Instalación de archivos completada.${c_reset}"
