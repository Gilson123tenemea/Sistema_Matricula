# -*- coding: utf-8 -*-
"""
view/main_window.py
Ventana principal con sidebar dinámico por rol: Admin / Docente / Estudiante.
"""
import customtkinter as ctk
from view.pages import (
    DashboardPage, DocentesPage, CarrerasPage, EstudiantesPage,
    HorariosPage, BusquedaPage, ReportesPage, HistorialPage,
    DashboardDocentePage, NotasDocentePage,
    DashboardEstudiantePage
)

SIDEBAR_BG = "#0f1923"
SIDEBAR_W  = 230
ACCENT     = "#1f6feb"
TEXT_MUTED = "#6e7681"
TEXT_LIGHT = "#e6edf3"

# (key, label, icono, roles_permitidos)
NAV_ITEMS = [
    ("dashboard",     "Inicio",           "🏠", ("admin",)),
    ("doc_dashboard", "Mi Panel",         "🏠", ("docente",)),
    ("est_dashboard", "Mi Dashboard",     "🏠", ("estudiante",)),
    ("docentes",      "Docentes",         "👨‍🏫", ("admin",)),
    ("carreras",      "Carreras & Materias","🎓", ("admin",)),
    ("estudiantes",   "Estudiantes",      "📚", ("admin",)),
    ("horarios",      "Horarios",         "🕐", ("admin",)),
    ("busqueda",      "Búsqueda Avanzada","🔍", ("admin",)),
    ("notas_doc",     "Gestión de Notas", "✏️",  ("docente",)),
    ("reportes",      "Reportes",         "📊", ("admin", "docente")),
    ("historial",     "Historial Académico","📖", ("admin", "estudiante")),
]


class MainWindow:
    def __init__(self, root: ctk.CTk, controller, usuario):
        self.root    = root
        self.ctrl    = controller
        self.usuario = usuario
        self.rol     = usuario.rol
        self._active_key = None

        self._setup_window()
        self._build_sidebar()
        self._build_content_area()
        self._build_pages()

        # Navegar a la página de inicio según rol
        if self.rol == "admin":
            self._nav_to("dashboard")
        elif self.rol == "docente":
            self._nav_to("doc_dashboard")
        else:
            self._nav_to("est_dashboard")

    def _setup_window(self):
        rol_label = {"admin": "Administrador", "docente": "Docente",
                     "estudiante": "Estudiante"}.get(self.rol, self.rol)
        self.root.title(f"Kognos | {rol_label} — {self.usuario.username}")
        self.root.geometry("1280x760")
        self.root.minsize(1000, 640)
        self.root.configure(fg_color="#111820")
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self.root, width=SIDEBAR_W,
                          fg_color=SIDEBAR_BG, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(20, weight=1)

        # Logo
        logo = ctk.CTkFrame(sb, fg_color="transparent")
        logo.grid(row=0, column=0, padx=20, pady=(26, 8), sticky="ew")
        ctk.CTkLabel(logo, text="🎓", font=("Segoe UI", 26),
                     text_color=ACCENT).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(logo, text="Kognos",
                     font=("Segoe UI", 17, "bold"),
                     text_color=TEXT_LIGHT).pack(side="left")

        ctk.CTkFrame(sb, height=1, fg_color="#1e2d3d").grid(
            row=1, column=0, sticky="ew", padx=16, pady=(4, 12))

        # Badge usuario
        rol_color = {"admin": ACCENT, "docente": "#d29922",
                     "estudiante": "#2ea043"}.get(self.rol, ACCENT)
        rol_label = {"admin": "Admin", "docente": "Docente",
                     "estudiante": "Estudiante"}.get(self.rol, self.rol)

        uframe = ctk.CTkFrame(sb, fg_color="#1a2535", corner_radius=8)
        uframe.grid(row=2, column=0, padx=12, pady=(0, 14), sticky="ew")
        ctk.CTkLabel(uframe, text=f"👤 {self.usuario.username}",
                     font=("Segoe UI", 11, "bold"),
                     text_color=TEXT_LIGHT).pack(side="left", padx=10, pady=6)
        ctk.CTkLabel(uframe, text=rol_label, font=("Segoe UI", 9),
                     text_color=rol_color).pack(side="right", padx=10)

        ctk.CTkLabel(sb, text="NAVEGACIÓN", font=("Segoe UI", 9),
                     text_color=TEXT_MUTED).grid(
            row=3, column=0, sticky="w", padx=24, pady=(0, 4))

        self._nav_buttons = {}
        fila = 4
        for key, label, icon, roles in NAV_ITEMS:
            if self.rol not in roles:
                continue
            btn = ctk.CTkButton(
                sb, text=f"{icon}  {label}",
                anchor="w", height=40, corner_radius=8,
                font=("Segoe UI", 12),
                fg_color="transparent", hover_color="#1a2535",
                text_color=TEXT_MUTED,
                command=lambda k=key: self._nav_to(k))
            btn.grid(row=fila, column=0, padx=10, pady=2, sticky="ew")
            self._nav_buttons[key] = btn
            fila += 1

        ctk.CTkFrame(sb, height=1, fg_color="#1e2d3d").grid(
            row=18, column=0, sticky="ew", padx=16, pady=(8, 6))
        ctk.CTkButton(
            sb, text="⏻  Cerrar Sesión", height=36,
            anchor="w", corner_radius=8, font=("Segoe UI", 11),
            fg_color="transparent", hover_color="#3b1a1a",
            text_color="#f85149", command=self._logout
        ).grid(row=19, column=0, padx=10, pady=(0, 4), sticky="ew")
        ctk.CTkLabel(sb, text="Kognos v1.0",
                     font=("Segoe UI", 9),
                     text_color=TEXT_MUTED).grid(row=20, column=0, pady=(0, 14))

    def _build_content_area(self):
        self.content = ctk.CTkFrame(self.root, fg_color="#111820", corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    def _build_pages(self):
        self.pages = {}
        es_admin  = self.rol == "admin"
        es_docente = self.rol == "docente"
        cedula    = self.ctrl.cedula_activa()

        page_map = {
            # Admin
            "dashboard":     (DashboardPage,          {}, ("admin",)),
            "docentes":      (DocentesPage,            {}, ("admin",)),
            "carreras":      (CarrerasPage,            {}, ("admin",)),
            "estudiantes":   (EstudiantesPage,         {}, ("admin",)),
            "horarios":      (HorariosPage,            {}, ("admin",)),
            "busqueda":      (BusquedaPage,            {}, ("admin",)),
            "reportes":      (ReportesPage,            {"es_admin": es_admin,
                                                         "cedula_fija": cedula},
                              ("admin", "docente")),
            "historial":     (HistorialPage,           {"cedula_fija": cedula if not es_admin else None},
                              ("admin", "estudiante")),
            # Docente
            "doc_dashboard": (DashboardDocentePage,    {}, ("docente",)),
            "notas_doc":     (NotasDocentePage,        {}, ("docente",)),
            # Estudiante
            "est_dashboard": (DashboardEstudiantePage, {}, ("estudiante",)),
        }

        for key, (cls, kwargs, roles) in page_map.items():
            if self.rol not in roles:
                continue
            page = cls(self.content, self.ctrl, **kwargs)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[key] = page

    def _nav_to(self, key):
        if key not in self.pages:
            return
        if self._active_key and self._active_key in self._nav_buttons:
            self._nav_buttons[self._active_key].configure(
                fg_color="transparent", text_color=TEXT_MUTED)
        self._active_key = key
        if key in self._nav_buttons:
            self._nav_buttons[key].configure(
                fg_color="#1a2d45", text_color=TEXT_LIGHT)
        self.pages[key].tkraise()
        if hasattr(self.pages[key], "refresh"):
            self.pages[key].refresh()

    def _logout(self):
        self.ctrl.logout()
        for w in self.root.winfo_children():
            w.destroy()
        from view.login_window import LoginWindow
        from app_launcher import lanzar_main_window
        LoginWindow(self.root, self.ctrl, lanzar_main_window)
