#!/usr/bin/env python3
"""
ram-popup.py

Lanza una ventana sin bordes con el popup visual de Cyber-RAM.
Se posiciona debajo de la waybar en el lado derecho mediante regla de Hyprland.
Se cierra solo desde el toggle de waybar.

Dependencias (Arch / CachyOS):
    sudo pacman -S python-gobject webkit2gtk-4.1
"""

import json
import os
import subprocess
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gdk, GLib, Gtk, WebKit2

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 120

REFRESH_MS = 2000


def add_window_rule():
    try:
        monitors = subprocess.run(
            ["hyprctl", "monitors", "-j"],
            capture_output=True, text=True, timeout=5,
        )
        monitors_data = json.loads(monitors.stdout)
        active = None
        for m in monitors_data:
            if m.get("focused", False):
                active = m
                break
        if not active and monitors_data:
            active = monitors_data[0]
        if active:
            scale = active.get("scale", 1)
            logical_w = int(active["width"] / scale)
            x = active["x"] + logical_w - WINDOW_WIDTH
            y = active["y"] + 33
            title = "^CYBERDECK RAM$"
            subprocess.run(
                ["hyprctl", "keyword", "windowrule", f"float,title:{title}"],
                capture_output=True, text=True, timeout=5,
            )
            subprocess.run(
                ["hyprctl", "keyword", "windowrule", f"pin,title:{title}"],
                capture_output=True, text=True, timeout=5,
            )
            subprocess.run(
                ["hyprctl", "keyword", "windowrule", f"move {x} {y},title:{title}"],
                capture_output=True, text=True, timeout=5,
            )
            subprocess.run(
                ["hyprctl", "keyword", "windowrule", f"size {WINDOW_WIDTH} {WINDOW_HEIGHT},title:{title}"],
                capture_output=True, text=True, timeout=5,
            )
    except Exception:
        pass


def get_ram():
    out = subprocess.check_output(["free", "-b"]).decode()
    parts = out.splitlines()[1].split()
    total = int(parts[1])
    used = int(parts[2])
    available = int(parts[6])
    return total, used, available


def reposition_window():
    try:
        monitors = subprocess.run(
            ["hyprctl", "monitors", "-j"],
            capture_output=True, text=True, timeout=5,
        )
        monitors_data = json.loads(monitors.stdout)
        active = None
        for m in monitors_data:
            if m.get("focused", False):
                active = m
                break
        if not active and monitors_data:
            active = monitors_data[0]
        if active:
            scale = active.get("scale", 1)
            logical_w = int(active["width"] / scale)
            x = active["x"] + logical_w - WINDOW_WIDTH
            y = active["y"] + 33
            title = "^CYBERDECK RAM$"
            subprocess.run(
                ["hyprctl", "dispatch", "movewindowpixel",
                 f"exact {x} {y},title:{title}"],
                capture_output=True, text=True, timeout=5,
            )
            subprocess.run(
                ["hyprctl", "dispatch", "resizewindowpixel",
                 f"exact {WINDOW_WIDTH} {WINDOW_HEIGHT},title:{title}"],
                capture_output=True, text=True, timeout=5,
            )
    except Exception:
        pass


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
    win.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)
    win.set_resizable(False)
    win.set_decorated(False)
    win.set_keep_above(True)
    win.set_position(Gtk.WindowPosition.NONE)

    screen = win.get_screen()
    visual = screen.get_rgba_visual()
    if visual is not None:
        win.set_visual(visual)
    win.set_app_paintable(True)

    webview = WebKit2.WebView()
    win.add(webview)

    def update_ram():
        t, u, a = get_ram()
        new_uri = f"file://{html_path}?total={t}&used={u}&available={a}"
        webview.load_uri(new_uri)
        return True

    GLib.timeout_add(REFRESH_MS, update_ram)
    GLib.idle_add(reposition_window)
    webview.load_uri(uri)

    win.connect("destroy", Gtk.main_quit)

    def cleanup(*_):
        pid_file = "/tmp/cyber-ram-popup.pid"
        if os.path.exists(pid_file):
            with open(pid_file) as f:
                saved_pid = int(f.read().strip())
                if saved_pid == os.getpid():
                    os.remove(pid_file)

    win.connect("destroy", cleanup)

    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
