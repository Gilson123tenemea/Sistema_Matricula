# -*- coding: utf-8 -*-
"""
app_launcher.py — Callback que recibe el usuario autenticado y lanza MainWindow.
Se inyecta el controller a través de builtins para evitar dependencias circulares.
"""
import builtins


def lanzar_main_window(usuario):
    """Callback invocado por LoginWindow al autenticar exitosamente."""
    import tkinter as tk
    from view.main_window import MainWindow

    root = tk._default_root
    ctrl = getattr(builtins, "_sisacad_ctrl", None)
    if root and ctrl:
        for w in root.winfo_children():
            w.destroy()
        MainWindow(root, ctrl, usuario)
