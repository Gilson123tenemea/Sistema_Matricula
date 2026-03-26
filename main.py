# -*- coding: utf-8 -*-
"""
main.py — Punto de entrada de SisAcad v4.0
"""
import builtins
import customtkinter as ctk

from model.data_manager import DataManager
from controller.controller import Controller
from view.login_window import LoginWindow
from app_launcher import lanzar_main_window


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Cargar datos
    data = DataManager()
    data.cargar()

    # Crear controller y guardarlo globalmente para app_launcher
    ctrl = Controller(data)
    builtins._sisacad_ctrl = ctrl

    # Crear ventana raíz
    root = ctk.CTk()
    LoginWindow(root, ctrl, lanzar_main_window)
    root.mainloop()


if __name__ == "__main__":
    main()
