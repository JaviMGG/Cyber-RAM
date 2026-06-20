#!/usr/bin/env python3
"""
ram-popup.py

Lanza una ventana sin bordes con el popup visual de Cyber-RAM,
inyectando los datos reales de /proc/meminfo en la URL.
Se cierra automáticamente al perder el foco o al pulsar Escape.

Dependencias (Arch / CachyOS):
    sudo pacman -S python-gobject webkit2gtk
"""

import os
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gdk, Gtk, WebKit2

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 190


def get_ram():
    info = {}
    with open("/proc/meminfo", encoding="utf-8") as f:
        for line in f:
            key, value = line.split(":")
            info[key.strip()] = int(value.split()[0]) * 1024  # kB -> bytes

    total = info["MemTotal"]
    available = info["MemAvailable"]
    used = total - available
    return total, used, available


def main():
    total, used, available = get_ram()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, "ram-popup.html")

    if not os.path.exists(html_path):
        sys.stderr.write(f"[Cyber-RAM] No se encontró {html_path}\n")
        sys.exit(1)

    uri = f"file://{html_path}?total={total}&used={used}&available={available}"

    win = Gtk.Window()
    win.set_title("CYBERDECK RAM")
    win.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)
    win.set_resizable(False)
    win.set_decorated(False)
    win.set_keep_above(True)
    win.set_position(Gtk.WindowPosition.MOUSE)

    # Fondo transparente (si el compositor de Wayland lo soporta)
    screen = win.get_screen()
    visual = screen.get_rgba_visual()
    if visual is not None:
        win.set_visual(visual)
    win.set_app_paintable(True)

    webview = WebKit2.WebView()
    webview.load_uri(uri)
    win.add(webview)

    win.connect("focus-out-event", lambda *_: Gtk.main_quit())
    win.connect(
        "key-press-event",
        lambda _w, e: Gtk.main_quit() if e.keyval == Gdk.KEY_Escape else None,
    )
    win.connect("destroy", Gtk.main_quit)

    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
