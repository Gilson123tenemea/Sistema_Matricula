# -*- coding: utf-8 -*-
"""
view/login_window.py — Kognos Sistema Académico Universitario
"""
import customtkinter as ctk

BG      = "#0d1117"
CARD_BG = "#161b22"
ACCENT  = "#1f6feb"
ACCENT2 = "#388bfd"
TEXT    = "#e6edf3"
MUTED   = "#8b949e"
BORDER  = "#30363d"
ERROR   = "#f85149"
FONT    = ("Segoe UI", 12)


class LoginWindow:
    """Ventana de inicio de sesión de Kognos."""

    def __init__(self, root: ctk.CTk, controller, on_success):
        self.root        = root
        self.ctrl        = controller
        self.on_success  = on_success
        self._build()

    def _build(self):
        self.root.title("Kognos — Inicio de Sesión")
        self.root.geometry("480x560")
        self.root.resizable(False, False)
        self.root.configure(fg_color=BG)

        card = ctk.CTkFrame(self.root, fg_color=CARD_BG,
                            corner_radius=16, border_width=1,
                            border_color=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center",
                   relwidth=0.82, relheight=0.85)

        # Birrete + título
        ctk.CTkLabel(card, text="🎓",
                     font=("Segoe UI", 52),
                     text_color=ACCENT).pack(pady=(36, 2))

        ctk.CTkLabel(card, text="Kognos",
                     font=("Segoe UI", 26, "bold"),
                     text_color=TEXT).pack()

        ctk.CTkLabel(card, text="Sistema Académico Universitario",
                     font=("Segoe UI", 11),
                     text_color=ACCENT).pack(pady=(0, 2))

        ctk.CTkLabel(card, text="Ingresa tus credenciales para continuar",
                     font=("Segoe UI", 10),
                     text_color=MUTED).pack(pady=(0, 18))

        ctk.CTkFrame(card, height=1, fg_color=BORDER).pack(fill="x", padx=28, pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", padx=32)

        ctk.CTkLabel(inner, text="Usuario", font=("Segoe UI", 10),
                     text_color=MUTED, anchor="w").pack(fill="x", pady=(0, 4))
        self._e_user = ctk.CTkEntry(
            inner, height=40, corner_radius=8,
            fg_color="#0d1117", border_color=BORDER,
            text_color=TEXT, font=FONT,
            placeholder_text="Nombre de usuario")
        self._e_user.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(inner, text="Contraseña", font=("Segoe UI", 10),
                     text_color=MUTED, anchor="w").pack(fill="x", pady=(0, 4))
        self._e_pass = ctk.CTkEntry(
            inner, height=40, corner_radius=8,
            fg_color="#0d1117", border_color=BORDER,
            text_color=TEXT, font=FONT,
            placeholder_text="••••••••", show="•")
        self._e_pass.pack(fill="x", pady=(0, 8))

        self._err_var = ctk.StringVar()
        ctk.CTkLabel(inner, textvariable=self._err_var,
                     text_color=ERROR, font=("Segoe UI", 10)).pack()

        ctk.CTkButton(
            inner, text="Iniciar Sesión", height=42,
            corner_radius=10, font=("Segoe UI", 13, "bold"),
            fg_color=ACCENT, hover_color=ACCENT2,
            command=self._login
        ).pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(
            card,
            text="Admin por defecto: admin / admin123",
            font=("Segoe UI", 9), text_color=MUTED
        ).pack(pady=(14, 0))

        self.root.bind("<Return>", lambda _: self._login())
        self._e_user.focus_set()

    def _login(self):
        username = self._e_user.get().strip()
        password = self._e_pass.get()
        if not username or not password:
            self._err_var.set("Completa todos los campos.")
            return
        try:
            ok, resultado = self.ctrl.login(username, password)
        except Exception as ex:
            self._err_var.set(f"Error: {ex}")
            return
        if not ok:
            self._err_var.set(resultado)
            return
        self._err_var.set("")
        self.on_success(resultado)
