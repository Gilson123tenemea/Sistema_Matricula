# -*- coding: utf-8 -*-
"""
view/dialogs.py
Todos los diálogos modales del sistema.
"""
import customtkinter as ctk
from tkinter import messagebox
from utils.constants import DIAS_SEMANA, HORAS, SEMESTRES, TITULOS_DOCENTE
from utils.validators import (validar_email, validar_cedula, validar_nota,
                               validar_creditos, validar_telefono, validar_nombre,
                               validar_codigo)

BG      = "#111820"
CARD_BG = "#161f2c"
CARD2   = "#1a2535"
ACCENT  = "#1f6feb"
ACCENT2 = "#388bfd"
SUCCESS = "#2ea043"
DANGER  = "#da3633"
TEXT    = "#e6edf3"
MUTED   = "#6e7681"
BORDER  = "#21262d"
WARN    = "#d29922"

FONT    = ("Segoe UI", 12)
FONT_SM = ("Segoe UI", 10)
FONT_LG = ("Segoe UI", 13, "bold")


def Info(parent, title, msg):
    messagebox.showinfo(title, msg, parent=parent)


def Confirm(parent, title, msg):
    return messagebox.askyesno(title, msg, parent=parent)


def _field(parent, label, row, placeholder="", width=320, show=""):
    ctk.CTkLabel(parent, text=label, font=FONT_SM,
                 text_color=MUTED, anchor="w").grid(
        row=row*2, column=0, sticky="w", pady=(8, 2))
    e = ctk.CTkEntry(parent, width=width, height=36, corner_radius=8,
                     fg_color="#0d1117", border_color=BORDER,
                     text_color=TEXT, font=FONT,
                     placeholder_text=placeholder, show=show)
    e.grid(row=row*2+1, column=0, sticky="ew", pady=(0, 4))
    return e


def _combo(parent, label, row, values, width=320):
    ctk.CTkLabel(parent, text=label, font=FONT_SM,
                 text_color=MUTED, anchor="w").grid(
        row=row*2, column=0, sticky="w", pady=(8, 2))
    c = ctk.CTkComboBox(parent, values=values, width=width, height=36,
                        fg_color="#0d1117", border_color=BORDER,
                        text_color=TEXT, font=FONT,
                        button_color=ACCENT, dropdown_fg_color=CARD2,
                        dropdown_text_color=TEXT)
    c.grid(row=row*2+1, column=0, sticky="ew", pady=(0, 4))
    return c


def _err_label(parent, row):
    lbl = ctk.CTkLabel(parent, text="", font=FONT_SM,
                       text_color=DANGER, wraplength=380)
    lbl.grid(row=row, column=0, sticky="w")
    return lbl


def _base_dialog(parent, title, width=440, height=None):
    win = ctk.CTkToplevel(parent)
    win.title(title)
    win.configure(fg_color=BG)
    win.grab_set()
    win.resizable(False, True)
    h = height or 600
    win.geometry(f"{width}x{h}")
    win.minsize(width, min(h, 400))
    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
    y = max(10, parent.winfo_rooty() + 20)
    win.geometry(f"+{x}+{y}")
    win.grid_rowconfigure(0, weight=1)
    win.grid_columnconfigure(0, weight=1)
    return win


# ═══════════════════════════════════════════════
# DIÁLOGO DOCENTE
# ═══════════════════════════════════════════════
class DialogDocente:
    def __init__(self, parent, ctrl, docente=None, on_save=None):
        self.ctrl    = ctrl
        self.docente = docente
        self.on_save = on_save
        self.result  = None

        self.win = _base_dialog(parent, "Registrar Docente" if not docente
                                else "Editar Docente", 460, 680)
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self.win, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="📋  Datos del Docente",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(row=1, column=0, sticky="ew", padx=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        inner.grid_columnconfigure(0, weight=1)

        self._e_ced   = _field(inner, "Cédula *", 0, "ej: 0912345678")
        self._e_nom   = _field(inner, "Nombres Completos *", 1, "ej: Juan Carlos Pérez")
        self._cb_tit  = _combo(inner, "Título *", 2, TITULOS_DOCENTE)
        self._e_email = _field(inner, "Correo Electrónico *", 3, "docente@uni.edu")
        self._e_esp   = _field(inner, "Especialidad *", 4, "ej: Programación Orientada a Objetos")
        self._e_tel   = _field(inner, "Número de Teléfono *", 5, "ej: 0991234567")

        if self.docente:
            d = self.docente
            self._e_ced.insert(0, d.cedula); self._e_ced.configure(state="disabled")
            self._e_nom.insert(0, d.nombres)
            self._cb_tit.set(d.titulo)
            self._e_email.insert(0, d.email)
            self._e_esp.insert(0, d.especialidad)
            self._e_tel.insert(0, d.telefono)

        self._err = _err_label(inner, 12)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        ctk.CTkButton(btns, text="Cancelar", width=100, height=36,
                      fg_color=CARD2, hover_color=BORDER, text_color=MUTED,
                      command=self.win.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="💾  Guardar", width=120, height=36,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._save).pack(side="right")

    def _save(self):
        cedula = self._e_ced.get().strip()
        nombres = self._e_nom.get().strip()
        titulo = self._cb_tit.get().strip()
        email = self._e_email.get().strip()
        esp = self._e_esp.get().strip()
        tel = self._e_tel.get().strip()

        if not all([cedula, nombres, titulo, email, esp, tel]):
            self._err.configure(text="⚠ Todos los campos son obligatorios."); return
        if not validar_cedula(cedula):
            self._err.configure(text="⚠ Cédula inválida (solo dígitos, 6-13 chars)."); return
        if not validar_nombre(nombres):
            self._err.configure(text="⚠ Nombre inválido (solo letras, mín. 3 chars)."); return
        if not validar_email(email):
            self._err.configure(text="⚠ Correo electrónico inválido."); return
        if not validar_telefono(tel):
            self._err.configure(text="⚠ Teléfono inválido (7-15 dígitos)."); return

        if self.docente:
            ok, msg = self.ctrl.editar_docente(cedula, nombres, titulo, email, esp, tel)
        else:
            ok, msg, creds = self.ctrl.registrar_docente(cedula, nombres, titulo,
                                                           email, esp, tel)
        if not ok:
            self._err.configure(text=f"⚠ {msg}"); return

        if not self.docente and creds:
            Info(self.win, "Credenciales generadas",
                 f"✅ Docente registrado exitosamente.\n\n"
                 f"🔑 Usuario : {creds[0]}\n"
                 f"🔑 Contraseña : {creds[1]}\n\n"
                 f"Comparte estas credenciales con el docente.")
        else:
            Info(self.win, "Éxito", msg)

        if self.on_save:
            self.on_save()
        self.win.destroy()


# ═══════════════════════════════════════════════
# DIÁLOGO CARRERA
# ═══════════════════════════════════════════════
class DialogCarrera:
    def __init__(self, parent, ctrl, carrera=None, on_save=None):
        self.ctrl    = ctrl
        self.carrera = carrera
        self.on_save = on_save

        self.win = _base_dialog(parent, "Registrar Carrera" if not carrera
                                else "Editar Carrera", 440, 420)
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self.win, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="🎓  Datos de la Carrera",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(row=1, column=0, sticky="ew", padx=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        inner.grid_columnconfigure(0, weight=1)

        self._e_cod   = _field(inner, "Código *", 0, "ej: ISW, ADM, MED")
        self._e_nom   = _field(inner, "Nombre de la Carrera *", 1, "ej: Ingeniería en Software")
        self._cb_cic  = _combo(inner, "Número de Ciclos *", 2,
                               [str(i) for i in range(1, 13)])
        self._e_desc  = _field(inner, "Descripción (opcional)", 3, "Descripción breve...")
        self._cb_cic.set("8")

        if self.carrera:
            c = self.carrera
            self._e_cod.insert(0, c.codigo); self._e_cod.configure(state="disabled")
            self._e_nom.insert(0, c.nombre)
            self._cb_cic.set(str(c.num_ciclos))
            self._e_desc.insert(0, c.descripcion)

        self._err = _err_label(inner, 8)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        ctk.CTkButton(btns, text="Cancelar", width=100, height=36,
                      fg_color=CARD2, hover_color=BORDER, text_color=MUTED,
                      command=self.win.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="💾  Guardar", width=120, height=36,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._save).pack(side="right")

    def _save(self):
        cod  = self._e_cod.get().strip().upper()
        nom  = self._e_nom.get().strip()
        nc   = self._cb_cic.get()
        desc = self._e_desc.get().strip()

        if not cod or not nom:
            self._err.configure(text="⚠ Código y nombre son obligatorios."); return
        if not validar_codigo(cod):
            self._err.configure(text="⚠ Código inválido (3-20 chars alfanuméricos)."); return

        if self.carrera:
            ok, msg = self.ctrl.editar_carrera(cod, nom, int(nc), desc)
        else:
            ok, msg = self.ctrl.registrar_carrera(cod, nom, int(nc), desc)

        if not ok:
            self._err.configure(text=f"⚠ {msg}"); return
        Info(self.win, "Éxito", msg)
        if self.on_save:
            self.on_save()
        self.win.destroy()


# ═══════════════════════════════════════════════
# DIÁLOGO HORARIO
# ═══════════════════════════════════════════════
class DialogHorario:
    def __init__(self, parent, ctrl, on_save=None):
        self.ctrl    = ctrl
        self.on_save = on_save
        self.win = _base_dialog(parent, "Registrar Horario", 420, 380)
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self.win, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="🕐  Nuevo Bloque Horario",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(row=1, column=0, sticky="ew", padx=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        inner.grid_columnconfigure(0, weight=1)

        self._cb_dia = _combo(inner, "Día *", 0, DIAS_SEMANA)
        self._cb_dia.set(DIAS_SEMANA[0])

        row2 = ctk.CTkFrame(inner, fg_color="transparent")
        row2.grid(row=3, column=0, sticky="ew")
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(inner, text="Hora inicio *", font=FONT_SM,
                     text_color=MUTED, anchor="w").grid(row=2, column=0, sticky="w", pady=(8, 2))
        self._cb_hi = ctk.CTkComboBox(row2, values=HORAS, width=120, height=36,
                                      fg_color="#0d1117", border_color=BORDER,
                                      text_color=TEXT, font=FONT,
                                      button_color=ACCENT, dropdown_fg_color=CARD2,
                                      dropdown_text_color=TEXT)
        self._cb_hi.set("07:00")
        self._cb_hi.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(row2, text=" → ", font=FONT, text_color=MUTED).grid(row=0, column=1)

        self._cb_hf = ctk.CTkComboBox(row2, values=HORAS, width=120, height=36,
                                      fg_color="#0d1117", border_color=BORDER,
                                      text_color=TEXT, font=FONT,
                                      button_color=ACCENT, dropdown_fg_color=CARD2,
                                      dropdown_text_color=TEXT)
        self._cb_hf.set("09:00")
        self._cb_hf.grid(row=0, column=2, sticky="w")

        self._e_aula = _field(inner, "Aula (opcional)", 2, "ej: Aula 101, Lab Informática")

        self._err = _err_label(inner, 8)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        ctk.CTkButton(btns, text="Cancelar", width=100, height=36,
                      fg_color=CARD2, hover_color=BORDER, text_color=MUTED,
                      command=self.win.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="💾  Guardar", width=120, height=36,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._save).pack(side="right")

    def _save(self):
        dia = self._cb_dia.get()
        hi  = self._cb_hi.get()
        hf  = self._cb_hf.get()
        aula = self._e_aula.get().strip()
        if hi >= hf:
            self._err.configure(text="⚠ La hora de inicio debe ser anterior a la hora fin."); return
        ok, msg, h = self.ctrl.registrar_horario(dia, hi, hf, aula)
        if not ok:
            self._err.configure(text=f"⚠ {msg}"); return
        Info(self.win, "Éxito", msg)
        if self.on_save:
            self.on_save()
        self.win.destroy()


# ═══════════════════════════════════════════════
# DIÁLOGO ASIGNATURA
# ═══════════════════════════════════════════════
class DialogAsignatura:
    def __init__(self, parent, ctrl, asignatura=None, on_save=None):
        self.ctrl       = ctrl
        self.asignatura = asignatura
        self.on_save    = on_save
        self.win = _base_dialog(parent, "Registrar Asignatura" if not asignatura
                                else "Editar Asignatura", 460, 720)
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self.win, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="📚  Datos de la Asignatura",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(row=1, column=0, sticky="ew", padx=20)

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        inner = scroll
        inner.grid_columnconfigure(0, weight=1)

        self._e_cod = _field(inner, "Código *", 0, "ej: MAT101")
        self._e_nom = _field(inner, "Nombre de la Materia *", 1, "ej: Cálculo I")

        # Carrera
        carreras = [""] + [f"{c.codigo} - {c.nombre}" for c in self.ctrl.data.carreras]
        self._cb_carr = _combo(inner, "Carrera *", 2, carreras)

        # Ciclo
        self._cb_sem = _combo(inner, "Ciclo *", 3, SEMESTRES)
        self._cb_sem.set("1")

        self._e_cred = _field(inner, "Créditos *", 4, "ej: 3")
        self._e_hs   = _field(inner, "Horas Semanales *", 5, "ej: 4  (créditos × 1h)")
        self._e_cupo = _field(inner, "Cupo Máximo", 6, "30")
        self._e_cupo.insert(0, "30")

        # Horario
        horarios = ["(sin horario)"] + [h.label() for h in self.ctrl.data.horarios]
        self._cb_hor = _combo(inner, "Horario (opcional, se asigna al registrar docente)", 7, horarios)
        self._cb_hor.set("(sin horario)")

        # Prerequisito
        asigs = ["(ninguno)"] + [f"{a.codigo} - {a.nombre}" for a in self.ctrl.data.asignaturas]
        self._cb_pre = _combo(inner, "Prerequisito", 8, asigs)
        self._cb_pre.set("(ninguno)")

        if self.asignatura:
            a = self.asignatura
            self._e_cod.insert(0, a.codigo); self._e_cod.configure(state="disabled")
            self._e_nom.insert(0, a.nombre)
            # Carrera
            match_c = next((f"{c.codigo} - {c.nombre}" for c in self.ctrl.data.carreras
                            if c.codigo == a.carrera), "")
            if match_c: self._cb_carr.set(match_c)
            self._cb_sem.set(str(a.semestre))
            self._e_cred.insert(0, str(a.creditos))
            self._e_hs.insert(0, str(a.horas_semanales))
            self._e_cupo.delete(0, "end"); self._e_cupo.insert(0, str(a.cupo_maximo))
            # Horario
            if a.horario_id:
                h = next((x for x in self.ctrl.data.horarios if x.id == a.horario_id), None)
                if h: self._cb_hor.set(h.label())
            if a.prerequisito:
                pre = next((f"{x.codigo} - {x.nombre}" for x in self.ctrl.data.asignaturas
                            if x.codigo == a.prerequisito), "")
                if pre: self._cb_pre.set(pre)

        self._err = _err_label(inner, 16)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        ctk.CTkButton(btns, text="Cancelar", width=100, height=36,
                      fg_color=CARD2, hover_color=BORDER, text_color=MUTED,
                      command=self.win.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="💾  Guardar", width=120, height=36,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._save).pack(side="right")

    def _save(self):
        cod  = self._e_cod.get().strip().upper()
        nom  = self._e_nom.get().strip()
        carr_sel = self._cb_carr.get()
        carrera  = carr_sel.split(" - ")[0] if " - " in carr_sel else ""
        sem  = int(self._cb_sem.get())
        cred_str = self._e_cred.get().strip()
        hs_str   = self._e_hs.get().strip()
        cupo_str = self._e_cupo.get().strip()
        hor_sel  = self._cb_hor.get()
        pre_sel  = self._cb_pre.get()

        if not cod or not nom or not carrera:
            self._err.configure(text="⚠ Código, nombre y carrera son obligatorios."); return
        if not validar_codigo(cod):
            self._err.configure(text="⚠ Código inválido."); return
        ok_c, cred = validar_creditos(cred_str)
        if not ok_c:
            self._err.configure(text="⚠ Créditos inválidos (1-10)."); return
        try:
            hs = int(hs_str) if hs_str else cred
            if hs < 1 or hs > 30: raise ValueError
        except ValueError:
            self._err.configure(text="⚠ Horas semanales inválidas (1-30)."); return
        try:
            cupo = int(cupo_str)
            if cupo < 1: raise ValueError
        except ValueError:
            self._err.configure(text="⚠ Cupo máximo inválido."); return

        # Horario ID
        hid = None
        if hor_sel != "(sin horario)":
            for h in self.ctrl.data.horarios:
                if h.label() == hor_sel:
                    hid = h.id; break

        # Prerequisito
        pre = None
        if pre_sel != "(ninguno)" and " - " in pre_sel:
            pre = pre_sel.split(" - ")[0]

        if self.asignatura:
            ok, msg = self.ctrl.editar_asignatura(cod, nom, self.asignatura.docente,
                                                   cred, cupo, sem, pre, carrera, hid, hs)
        else:
            ok, msg = self.ctrl.registrar_asignatura(cod, nom, "", cred, cupo,
                                                      sem, pre, carrera, hid, hs)
        if not ok:
            self._err.configure(text=f"⚠ {msg}"); return
        Info(self.win, "Éxito", msg)
        if self.on_save:
            self.on_save()
        self.win.destroy()



# ═══════════════════════════════════════════════
# DIÁLOGO ASIGNAR DOCENTE + HORARIO (flujo integrado)
# ═══════════════════════════════════════════════
class DialogAsignarDocenteHorario:
    """
    Diálogo principal para asignar un docente a una materia y definir su horario.
    - Muestra las horas semanales requeridas y sugiere distribución
    - Permite construir bloques (día + hora) con botón + 
    - Verifica conflictos en tiempo real
    """
    def __init__(self, parent, ctrl, asignatura=None, on_save=None):
        self.ctrl       = ctrl
        self.asignatura = asignatura
        self.on_save    = on_save
        self._bloques   = []   # list of (dia, hi, hf)

        self.win = _base_dialog(parent, "Asignar Docente y Horario", 560, 640)
        self._build()

    def _build(self):
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self.win, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(3, weight=1)

        # ── Título
        ctk.CTkLabel(card, text="👨\u200d🏫  Asignar Docente y Horario",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(
            row=1, column=0, sticky="ew", padx=20)

        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent")
        scroll.grid(row=2, column=0, sticky="nsew", padx=16, pady=8)
        scroll.grid_columnconfigure(0, weight=1)
        inner = scroll

        # ── Selector de asignatura
        asigs = [f"{a.codigo} - {a.nombre}  [{a.horas_semanales}h/sem]"
                 for a in self.ctrl.data.asignaturas]
        _lbl(inner, "Asignatura *", 0)
        self._cb_asig = ctk.CTkComboBox(
            inner, values=asigs if asigs else ["(sin asignaturas)"],
            width=480, height=36,
            fg_color="#0d1117", border_color=BORDER, text_color=TEXT, font=FONT,
            button_color=ACCENT, dropdown_fg_color=CARD2, dropdown_text_color=TEXT,
            command=self._on_asig_change)
        self._cb_asig.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        if self.asignatura:
            a = self.asignatura
            self._cb_asig.set(f"{a.codigo} - {a.nombre}  [{a.horas_semanales}h/sem]")
            self._cb_asig.configure(state="disabled")

        # ── Info de horas y sugerencia
        self._lbl_info = ctk.CTkLabel(inner, text="", font=FONT_SM,
                                       text_color=WARN, anchor="w", wraplength=460)
        self._lbl_info.grid(row=2, column=0, sticky="w", pady=(0, 8))

        # ── Selector de docente
        docs = [f"{d.cedula} - {d.nombres}" for d in self.ctrl.data.docentes]
        _lbl(inner, "Docente *", 3)
        self._cb_doc = ctk.CTkComboBox(
            inner, values=docs if docs else ["(sin docentes)"],
            width=480, height=36,
            fg_color="#0d1117", border_color=BORDER, text_color=TEXT, font=FONT,
            button_color=ACCENT, dropdown_fg_color=CARD2, dropdown_text_color=TEXT,
            command=self._on_doc_change)
        self._cb_doc.grid(row=4, column=0, sticky="ew", pady=(0, 6))

        # Horarios actuales del docente
        self._lbl_doc_hors = ctk.CTkLabel(inner, text="", font=FONT_SM,
                                           text_color=TEXT_MUTED, anchor="w", wraplength=460)
        self._lbl_doc_hors.grid(row=5, column=0, sticky="w", pady=(0, 10))

        # ── Aula
        _lbl(inner, "Aula", 6)
        self._e_aula = ctk.CTkEntry(inner, width=240, height=34, corner_radius=8,
                                     fg_color="#0d1117", border_color=BORDER,
                                     text_color=TEXT, font=FONT,
                                     placeholder_text="ej: Aula 101, Lab Inf.")
        self._e_aula.grid(row=7, column=0, sticky="w", pady=(0, 10))

        # ── Constructor de bloques horarios
        ctk.CTkLabel(inner, text="Bloques Horarios *", font=("Segoe UI", 11, "bold"),
                     text_color=TEXT).grid(row=8, column=0, sticky="w", pady=(4, 4))

        bloque_builder = ctk.CTkFrame(inner, fg_color=CARD2, corner_radius=8)
        bloque_builder.grid(row=9, column=0, sticky="ew", pady=(0, 6))
        bloque_builder.grid_columnconfigure(3, weight=1)

        # Día
        self._cb_dia = ctk.CTkComboBox(
            bloque_builder, values=DIAS_SEMANA, width=130, height=34,
            fg_color="#0d1117", border_color=BORDER, text_color=TEXT, font=FONT_SM,
            button_color=ACCENT, dropdown_fg_color=CARD2, dropdown_text_color=TEXT)
        self._cb_dia.set(DIAS_SEMANA[0])
        self._cb_dia.grid(row=0, column=0, padx=(10, 6), pady=10)

        # Hora inicio
        self._cb_hi = ctk.CTkComboBox(
            bloque_builder, values=HORAS, width=90, height=34,
            fg_color="#0d1117", border_color=BORDER, text_color=TEXT, font=FONT_SM,
            button_color=ACCENT, dropdown_fg_color=CARD2, dropdown_text_color=TEXT)
        self._cb_hi.set("07:00")
        self._cb_hi.grid(row=0, column=1, padx=(0, 4), pady=10)

        ctk.CTkLabel(bloque_builder, text="→", font=FONT, text_color=MUTED).grid(
            row=0, column=2, padx=2)

        # Hora fin
        self._cb_hf = ctk.CTkComboBox(
            bloque_builder, values=HORAS, width=90, height=34,
            fg_color="#0d1117", border_color=BORDER, text_color=TEXT, font=FONT_SM,
            button_color=ACCENT, dropdown_fg_color=CARD2, dropdown_text_color=TEXT)
        self._cb_hf.set("09:00")
        self._cb_hf.grid(row=0, column=3, padx=(0, 6), pady=10)

        ctk.CTkButton(bloque_builder, text="+ Agregar", width=90, height=34,
                      fg_color=SUCCESS, hover_color="#3fb950",
                      command=self._agregar_bloque).grid(row=0, column=4, padx=(0, 10))

        # Lista de bloques agregados
        ctk.CTkLabel(inner, text="Bloques agregados:", font=FONT_SM,
                     text_color=MUTED).grid(row=10, column=0, sticky="w", pady=(4, 2))
        self._bloques_frame = ctk.CTkFrame(inner, fg_color=CARD2, corner_radius=8,
                                            height=80)
        self._bloques_frame.grid(row=11, column=0, sticky="ew", pady=(0, 4))
        self._lbl_bloques_empty = ctk.CTkLabel(
            self._bloques_frame, text="  (ningún bloque agregado)",
            font=FONT_SM, text_color=MUTED)
        self._lbl_bloques_empty.pack(pady=14)

        # Resumen horas
        self._lbl_horas = ctk.CTkLabel(inner, text="", font=FONT_SM,
                                        text_color=CYAN, anchor="w")
        self._lbl_horas.grid(row=12, column=0, sticky="w", pady=(2, 4))

        # Aviso de conflicto
        self._lbl_conflicto = ctk.CTkLabel(inner, text="", font=FONT_SM,
                                            text_color=DANGER, anchor="w",
                                            wraplength=460)
        self._lbl_conflicto.grid(row=13, column=0, sticky="w")

        self._err = _err_label(inner, 14)

        # ── Botones fijos
        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=16, pady=(8, 14))
        ctk.CTkButton(btns, text="Cancelar", width=100, height=36,
                      fg_color=CARD2, hover_color=BORDER, text_color=MUTED,
                      command=self.win.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="✅  Guardar Asignación", width=180, height=36,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._save).pack(side="right")

        # Pre-cargar si hay asignatura
        self._on_asig_change(None)
        if self.asignatura and self.asignatura.docente:
            d = next((x for x in self.ctrl.data.docentes
                      if x.cedula == self.asignatura.docente), None)
            if d:
                self._cb_doc.set(f"{d.cedula} - {d.nombres}")
                self._on_doc_change(None)
        if self.asignatura and self.asignatura.horario_id:
            h = self.ctrl.data.horario_by_id(self.asignatura.horario_id)
            if h:
                self._bloques = [(b.dia, b.hora_inicio, b.hora_fin) for b in h.bloques]
                self._e_aula.insert(0, h.aula)
                self._refresh_bloques_ui()

    def _lbl_asig_hs(self):
        """Retorna horas semanales de la asignatura seleccionada."""
        sel = self._cb_asig.get()
        if "[" in sel and "h/sem]" in sel:
            try:
                return int(sel.split("[")[1].replace("h/sem]", ""))
            except Exception:
                pass
        return 4

    def _on_asig_change(self, val):
        hs = self._lbl_asig_hs()
        sugs = self.ctrl.calcular_bloques_sugeridos(hs)
        txt_sugs = "  |  ".join(f"{n} día(s) × {h}h" for n, h in sugs)
        self._lbl_info.configure(
            text=f"📋 Horas semanales requeridas: {hs}h  →  Distribuciones sugeridas: {txt_sugs}")

    def _on_doc_change(self, val):
        """Muestra los horarios actuales del docente."""
        sel = self._cb_doc.get()
        if " - " not in sel:
            self._lbl_doc_hors.configure(text="")
            return
        ced = sel.split(" - ")[0]
        materias_doc = [a for a in self.ctrl.data.asignaturas
                        if a.docente == ced and a.horario_id]
        if not materias_doc:
            self._lbl_doc_hors.configure(
                text="  ✅ Docente sin horarios asignados actualmente.")
            return
        nombres_c = {c.codigo: c.nombre for c in self.ctrl.data.carreras}
        lineas = ["  📅 Horarios actuales del docente:"]
        for a in materias_doc:
            h = self.ctrl.data.horario_by_id(a.horario_id)
            if h:
                nc = nombres_c.get(a.carrera, a.carrera)
                lineas.append(f"    • {a.nombre} ({nc}) → {h.resumen()}")
        self._lbl_doc_hors.configure(text="\n".join(lineas))

    def _agregar_bloque(self):
        dia = self._cb_dia.get()
        hi  = self._cb_hi.get()
        hf  = self._cb_hf.get()
        if hi >= hf:
            self._err.configure(text="⚠ Hora inicio debe ser menor que hora fin."); return
        # Verificar solapamiento con bloques ya agregados
        from model.horario import BloqueHorario
        nuevo = BloqueHorario(dia, hi, hf)
        for d2, h2i, h2f in self._bloques:
            existente = BloqueHorario(d2, h2i, h2f)
            if nuevo.solapado(existente):
                self._err.configure(
                    text=f"⚠ Este bloque se solapa con {d2} {h2i}-{h2f} ya agregado."); return
        self._err.configure(text="")
        self._bloques.append((dia, hi, hf))
        self._refresh_bloques_ui()
        self._verificar_conflicto_live()

    def _refresh_bloques_ui(self):
        for w in self._bloques_frame.winfo_children():
            w.destroy()
        if not self._bloques:
            ctk.CTkLabel(self._bloques_frame,
                         text="  (ningún bloque agregado)",
                         font=FONT_SM, text_color=MUTED).pack(pady=10)
            self._lbl_horas.configure(text="")
            return

        total_h = 0
        for i, (dia, hi, hf) in enumerate(self._bloques):
            h_bloque = int(hf.split(":")[0]) - int(hi.split(":")[0])
            total_h += h_bloque
            row_f = ctk.CTkFrame(self._bloques_frame, fg_color="transparent")
            row_f.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row_f,
                         text=f"  {dia:12s}  {hi} – {hf}  ({h_bloque}h)",
                         font=FONT_SM, text_color=TEXT).pack(side="left")
            idx = i
            ctk.CTkButton(row_f, text="✕", width=28, height=24,
                          fg_color=DANGER, hover_color="#b91c1c",
                          command=lambda ix=idx: self._quitar_bloque(ix)
                          ).pack(side="right", padx=4)

        hs_req = self._lbl_asig_hs()
        color = SUCCESS if total_h == hs_req else (WARN if total_h < hs_req else DANGER)
        self._lbl_horas.configure(
            text=f"  Total: {total_h}h semanales  (requeridas: {hs_req}h)",
            text_color=color)

    def _quitar_bloque(self, idx):
        if 0 <= idx < len(self._bloques):
            self._bloques.pop(idx)
            self._refresh_bloques_ui()
            self._verificar_conflicto_live()

    def _verificar_conflicto_live(self):
        """Verificación en tiempo real al agregar bloques."""
        self._lbl_conflicto.configure(text="")
        if not self._bloques: return
        doc_sel = self._cb_doc.get()
        if " - " not in doc_sel: return
        ced_doc = doc_sel.split(" - ")[0]
        asig_sel = self._cb_asig.get()
        cod_asig = asig_sel.split(" - ")[0] if " - " in asig_sel else None

        from model.horario import Horario, BloqueHorario
        bloques = [BloqueHorario(d, hi, hf) for d, hi, hf in self._bloques]
        h_nuevo = Horario(None, bloques)
        conflicto, detalle = self.ctrl.verificar_conflicto_docente(
            ced_doc, h_nuevo, excluir_asig=cod_asig)
        if conflicto:
            self._lbl_conflicto.configure(text=f"⛔ {detalle}")

    def _save(self):
        asig_sel = self._cb_asig.get()
        doc_sel  = self._cb_doc.get()
        aula     = self._e_aula.get().strip()

        if " - " not in asig_sel:
            self._err.configure(text="⚠ Selecciona una asignatura."); return
        if " - " not in doc_sel:
            self._err.configure(text="⚠ Selecciona un docente."); return
        if not self._bloques:
            self._err.configure(text="⚠ Agrega al menos un bloque horario."); return

        cod_asig = asig_sel.split(" - ")[0]
        ced_doc  = doc_sel.split(" - ")[0]

        ok, msg = self.ctrl.asignar_docente_con_horario(
            ced_doc, cod_asig, self._bloques, aula)

        if not ok:
            self._err.configure(text=msg); return

        Info(self.win, "✅ Asignación guardada", msg)
        if self.on_save: self.on_save()
        self.win.destroy()


# ── helpers internos del módulo ───────────────
def _lbl(parent, text, row):
    ctk.CTkLabel(parent, text=text, font=FONT_SM,
                 text_color=MUTED, anchor="w").grid(
        row=row, column=0, sticky="w", pady=(8, 2))

from utils.constants import DIAS_SEMANA, HORAS, SEMESTRES, TITULOS_DOCENTE
TEXT_MUTED = MUTED
CYAN = "#17a2b8"


# ═══════════════════════════════════════════════
# DIÁLOGO ESTUDIANTE
# ═══════════════════════════════════════════════
class DialogEstudiante:
    def __init__(self, parent, ctrl, estudiante=None, on_save=None):
        self.ctrl       = ctrl
        self.estudiante = estudiante
        self.on_save    = on_save
        self.win = _base_dialog(parent, "Registrar Estudiante" if not estudiante
                                else "Editar Estudiante", 460, 640)
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self.win, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="🎓  Datos del Estudiante",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(row=1, column=0, sticky="ew", padx=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        inner.grid_columnconfigure(0, weight=1)

        self._e_ced   = _field(inner, "Cédula *", 0, "ej: 0912345678")
        self._e_nom   = _field(inner, "Nombre Completo *", 1, "ej: María García")
        self._e_edad  = _field(inner, "Edad *", 2, "ej: 20")
        self._e_email = _field(inner, "Correo Electrónico *", 3, "ej: estudiante@uni.edu")

        carreras = [f"{c.codigo} - {c.nombre}" for c in self.ctrl.data.carreras]
        self._cb_carr = _combo(inner, "Carrera *", 4, carreras if carreras
                               else ["(sin carreras registradas)"])
        self._cb_sem  = _combo(inner, "Ciclo *", 5, SEMESTRES)
        self._cb_sem.set("1")

        if self.estudiante:
            e = self.estudiante
            self._e_ced.insert(0, e.cedula); self._e_ced.configure(state="disabled")
            self._e_nom.insert(0, e.nombre)
            self._e_edad.insert(0, str(e.edad))
            self._e_email.insert(0, e.email)
            match_c = next((f"{c.codigo} - {c.nombre}" for c in self.ctrl.data.carreras
                            if c.codigo == e.carrera), e.carrera)
            if match_c: self._cb_carr.set(match_c)
            self._cb_sem.set(str(e.semestre))

        self._err = _err_label(inner, 12)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        ctk.CTkButton(btns, text="Cancelar", width=100, height=36,
                      fg_color=CARD2, hover_color=BORDER, text_color=MUTED,
                      command=self.win.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="💾  Guardar", width=120, height=36,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._save).pack(side="right")

    def _save(self):
        ced   = self._e_ced.get().strip()
        nom   = self._e_nom.get().strip()
        edad_s = self._e_edad.get().strip()
        email = self._e_email.get().strip()
        carr_sel = self._cb_carr.get()
        sem   = int(self._cb_sem.get())

        if not all([ced, nom, edad_s, email, carr_sel]):
            self._err.configure(text="⚠ Todos los campos son obligatorios."); return
        if not validar_cedula(ced):
            self._err.configure(text="⚠ Cédula inválida."); return
        if not validar_nombre(nom):
            self._err.configure(text="⚠ Nombre inválido."); return
        if not validar_email(email):
            self._err.configure(text="⚠ Email inválido."); return
        try:
            edad = int(edad_s)
            if edad < 15 or edad > 80: raise ValueError
        except ValueError:
            self._err.configure(text="⚠ Edad inválida (15-80)."); return

        carrera = carr_sel.split(" - ")[0] if " - " in carr_sel else carr_sel

        if self.estudiante:
            ok, msg = self.ctrl.editar_estudiante(ced, nom, edad, carrera, email, sem)
        else:
            ok, msg, creds = self.ctrl.registrar_estudiante(ced, nom, edad, carrera, email, sem)

        if not ok:
            self._err.configure(text=f"⚠ {msg}"); return

        if not self.estudiante and creds:
            Info(self.win, "Credenciales generadas",
                 f"✅ Estudiante registrado exitosamente.\n\n"
                 f"🔑 Usuario : {creds[0]}\n"
                 f"🔑 Contraseña : {creds[1]}\n\n"
                 f"Comparte estas credenciales con el estudiante.")
        else:
            Info(self.win, "Éxito", msg)

        if self.on_save:
            self.on_save()
        self.win.destroy()


# ═══════════════════════════════════════════════
# DIÁLOGO MATRÍCULA MÚLTIPLE
# ═══════════════════════════════════════════════
class DialogMatricula:
    def __init__(self, parent, ctrl, matricula=None, on_save=None):
        self.ctrl     = ctrl
        self.matricula = matricula
        self.on_save  = on_save
        self._checks  = {}
        self.win = _base_dialog(parent, "Matricular Estudiante", 520, 700)
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self.win, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="📋  Nueva Matrícula",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(row=1, column=0, sticky="ew", padx=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        inner.grid_columnconfigure(0, weight=1)

        # Estudiante
        ests = [f"{e.cedula} - {e.nombre}" for e in self.ctrl.data.estudiantes]
        self._cb_est = _combo(inner, "Estudiante *", 0, ests if ests else ["(sin estudiantes)"])
        self._cb_est.configure(command=self._on_est_change)

        # Carrera y Ciclo (para filtrar materias)
        row_f = ctk.CTkFrame(inner, fg_color="transparent")
        row_f.grid(row=3, column=0, sticky="ew")
        row_f.grid_columnconfigure(0, weight=1)
        row_f.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(inner, text="Filtrar por Carrera / Ciclo",
                     font=FONT_SM, text_color=MUTED, anchor="w").grid(
            row=2, column=0, sticky="w", pady=(8, 2))

        carrs = ["(todas)"] + [f"{c.codigo} - {c.nombre}" for c in self.ctrl.data.carreras]
        self._cb_fcarr = ctk.CTkComboBox(row_f, values=carrs, width=230, height=34,
                                          fg_color="#0d1117", border_color=BORDER,
                                          text_color=TEXT, font=FONT_SM,
                                          button_color=ACCENT, dropdown_fg_color=CARD2,
                                          dropdown_text_color=TEXT,
                                          command=self._on_filtro_change)
        self._cb_fcarr.set("(todas)")
        self._cb_fcarr.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self._cb_fcic = ctk.CTkComboBox(row_f, values=["(todos)"] + SEMESTRES,
                                         width=110, height=34,
                                         fg_color="#0d1117", border_color=BORDER,
                                         text_color=TEXT, font=FONT_SM,
                                         button_color=ACCENT, dropdown_fg_color=CARD2,
                                         dropdown_text_color=TEXT,
                                         command=self._on_filtro_change)
        self._cb_fcic.set("(todos)")
        self._cb_fcic.grid(row=0, column=1, sticky="ew")

        # Lista scrollable de materias con checkboxes
        ctk.CTkLabel(inner, text="Seleccionar Materias *",
                     font=FONT_SM, text_color=MUTED, anchor="w").grid(
            row=4, column=0, sticky="w", pady=(8, 2))
        self._scroll = ctk.CTkScrollableFrame(inner, height=200,
                                               fg_color=CARD2, corner_radius=8)
        self._scroll.grid(row=5, column=0, sticky="ew")

        self._err = _err_label(inner, 8)
        self._refresh_materias()

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        ctk.CTkButton(btns, text="Cancelar", width=100, height=36,
                      fg_color=CARD2, hover_color=BORDER, text_color=MUTED,
                      command=self.win.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="✅  Matricular + PDF", width=160, height=36,
                      fg_color=SUCCESS, hover_color="#3fb950",
                      command=self._save).pack(side="right")

    def _on_est_change(self, val):
        self._refresh_materias()

    def _on_filtro_change(self, val):
        self._refresh_materias()

    def _refresh_materias(self):
        for w in self._scroll.winfo_children():
            w.destroy()
        self._checks = {}

        carr_sel = self._cb_fcarr.get()
        cic_sel  = self._cb_fcic.get()
        est_sel  = self._cb_est.get()

        carrera_filter = carr_sel.split(" - ")[0] if " - " in carr_sel else ""
        ciclo_filter   = int(cic_sel) if cic_sel != "(todos)" else None

        # Si hay estudiante seleccionado, pre-filtrar por su carrera/ciclo
        if " - " in est_sel:
            ced = est_sel.split(" - ")[0]
            est = next((e for e in self.ctrl.data.estudiantes if e.cedula == ced), None)
            if est and not carrera_filter:
                carrera_filter = est.carrera
            if est and not ciclo_filter:
                ciclo_filter   = est.semestre

        # Materias ya matriculadas y ciclos aprobados del estudiante
        ya_matriculadas = set()
        ciclos_aprobados = set()
        ced_est = None
        if " - " in self._cb_est.get():
            ced_est = self._cb_est.get().split(" - ")[0]
            for m in self.ctrl.data.matriculas:
                if m.estudiante.cedula == ced_est:
                    ya_matriculadas.add(m.asignatura.codigo)
                    if m.nota >= 7.0:
                        ciclos_aprobados.add(m.asignatura.semestre)

        # Ciclo maximo al que puede acceder:
        # Si tiene materias aprobadas, puede matricularse en ciclo_aprobado_max + 1
        max_ciclo_permitido = 1
        if ciclos_aprobados:
            # Puede matricularse en el siguiente ciclo al maximo que ha aprobado
            max_ciclo_permitido = max(ciclos_aprobados) + 1

        materias = [a for a in self.ctrl.data.asignaturas
                    if (not carrera_filter or a.carrera == carrera_filter)
                    and (not ciclo_filter or a.semestre == ciclo_filter)
                    and a.codigo not in ya_matriculadas
                    and (ced_est is None or a.semestre <= max_ciclo_permitido)]

        if not materias:
            if ced_est and ciclos_aprobados:
                msg = f"No hay materias disponibles. Puede matricularse hasta ciclo {max_ciclo_permitido}."
            else:
                msg = "No hay materias disponibles. Primero aprueba materias del ciclo 1."
            ctk.CTkLabel(self._scroll, text=msg,
                         font=FONT_SM, text_color=MUTED).pack(padx=10, pady=8)
            return

        dic_doc = {d.cedula: d.nombres for d in self.ctrl.data.docentes}
        for a in materias:
            cupos = self.ctrl.cupos_disponibles(a.codigo)
            doc_n = dic_doc.get(a.docente, "Sin asignar")
            var   = ctk.BooleanVar(value=False)
            frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
            frame.pack(fill="x", pady=2)
            cb = ctk.CTkCheckBox(
                frame, variable=var,
                text=f"{a.codigo} — {a.nombre}",
                font=("Segoe UI", 11), text_color=TEXT,
                fg_color=ACCENT, hover_color=ACCENT2,
                state="normal" if cupos > 0 else "disabled")
            cb.pack(side="left", padx=8)
            ctk.CTkLabel(frame,
                         text=f"  {doc_n}  |  Ciclo {a.semestre}  |  Cupos: {cupos}",
                         font=(FONT_SM[0], 9), text_color=MUTED).pack(side="left")
            self._checks[a.codigo] = var

    def _save(self):
        est_sel = self._cb_est.get()
        if " - " not in est_sel:
            self._err.configure(text="⚠ Selecciona un estudiante."); return
        ced = est_sel.split(" - ")[0]

        seleccionados = [cod for cod, var in self._checks.items() if var.get()]
        if not seleccionados:
            self._err.configure(text="⚠ Selecciona al menos una materia."); return

        ok, msg = self.ctrl.matricular_multiples(ced, seleccionados)
        Info(self.win, "Resultado de Matrícula", msg)

        # Generar PDF
        if ok:
            from tkinter import filedialog
            ruta = filedialog.asksaveasfilename(
                parent=self.win, defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile=f"matricula_{ced}.pdf",
                title="Guardar Comprobante de Matrícula")
            if ruta:
                ok_pdf, msg_pdf = self.ctrl.generar_pdf_matricula(ced, ruta)
                Info(self.win, "PDF", msg_pdf)

        if self.on_save:
            self.on_save()
        self.win.destroy()


# ═══════════════════════════════════════════════
# DIÁLOGO EDITAR NOTA
# ═══════════════════════════════════════════════
class DialogEditarNota:
    def __init__(self, parent, ctrl, cedula, codigo, nota_actual, on_save=None):
        self.ctrl     = ctrl
        self.cedula   = cedula
        self.codigo   = codigo
        self.on_save  = on_save
        self.win = _base_dialog(parent, "Editar Nota", 380, 300)
        self._build(nota_actual)

    def _build(self, nota_actual):
        card = ctk.CTkFrame(self.win, fg_color=CARD_BG, corner_radius=12)
        card.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="✏️  Editar Nota",
                     font=("Segoe UI", 15, "bold"),
                     text_color=TEXT).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 4))
        ctk.CTkFrame(card, height=1, fg_color=BORDER).grid(row=1, column=0, sticky="ew", padx=20)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        inner.grid_columnconfigure(0, weight=1)

        asig = next((a for a in self.ctrl.data.asignaturas if a.codigo == self.codigo), None)
        est  = next((e for e in self.ctrl.data.estudiantes if e.cedula == self.cedula), None)
        if asig:
            ctk.CTkLabel(inner, text=f"Asignatura: {asig.nombre}",
                         font=FONT, text_color=TEXT).grid(row=0, column=0, sticky="w", pady=4)
        if est:
            ctk.CTkLabel(inner, text=f"Estudiante: {est.nombre}",
                         font=FONT, text_color=TEXT).grid(row=1, column=0, sticky="w", pady=4)

        ctk.CTkLabel(inner, text="Nueva Nota (0.0 - 10.0) *",
                     font=FONT_SM, text_color=MUTED, anchor="w").grid(
            row=2, column=0, sticky="w", pady=(12, 2))
        self._e_nota = ctk.CTkEntry(inner, width=200, height=40, corner_radius=8,
                                     fg_color="#0d1117", border_color=BORDER,
                                     text_color=TEXT, font=("Segoe UI", 18, "bold"))
        self._e_nota.insert(0, str(nota_actual))
        self._e_nota.grid(row=3, column=0, sticky="w")

        self._err = _err_label(inner, 4)

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        ctk.CTkButton(btns, text="Cancelar", width=100, height=36,
                      fg_color=CARD2, hover_color=BORDER, text_color=MUTED,
                      command=self.win.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(btns, text="💾  Guardar", width=120, height=36,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._save).pack(side="right")

    def _save(self):
        ok, nota = validar_nota(self._e_nota.get())
        if not ok:
            self._err.configure(text="⚠ Nota inválida (0.0 - 10.0)."); return
        ok2, msg = self.ctrl.editar_nota(self.cedula, self.codigo, nota)
        if not ok2:
            self._err.configure(text=f"⚠ {msg}"); return
        Info(self.win, "Éxito", msg)
        if self.on_save:
            self.on_save()
        self.win.destroy()
