# -*- coding: utf-8 -*-
"""
view/pages.py -- Kognos Sistema Academico Universitario
"""
import os
import customtkinter as ctk
from tkinter import ttk, filedialog

from view.dialogs import (
    DialogDocente, DialogCarrera,
    DialogAsignatura, DialogAsignarDocenteHorario,
    DialogEstudiante, DialogMatricula, DialogEditarNota,
    Confirm, Info
)

BG         = "#111820"
CARD_BG    = "#161f2c"
CARD2_BG   = "#1a2535"
ACCENT     = "#1f6feb"
ACCENT2    = "#388bfd"
SUCCESS    = "#2ea043"
DANGER     = "#da3633"
WARN       = "#d29922"
TEXT       = "#e6edf3"
TEXT_MUTED = "#6e7681"
BORDER     = "#21262d"
PURPLE     = "#9b59b6"
CYAN       = "#17a2b8"

FONT_H1    = ("Segoe UI", 22, "bold")
FONT_H2    = ("Segoe UI", 15, "bold")
FONT_BODY  = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)

from utils.constants import SEMESTRES


def _tree_style(tree, tag_colors=None):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
        background=CARD2_BG, fieldbackground=CARD2_BG,
        foreground=TEXT, rowheight=34, font=("Segoe UI", 11),
        borderwidth=0, relief="flat")
    style.configure("Custom.Treeview.Heading",
        background=CARD_BG, foreground=TEXT_MUTED,
        font=("Segoe UI", 10, "bold"), borderwidth=0, relief="flat")
    style.map("Custom.Treeview",
        background=[("selected", ACCENT)], foreground=[("selected", "#ffffff")])
    tree.configure(style="Custom.Treeview")
    if tag_colors:
        for tag, color in tag_colors.items():
            tree.tag_configure(tag, foreground=color)


def _header(parent, title, subtitle=""):
    hdr = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(hdr, text=title, font=FONT_H1, text_color=TEXT).pack(side="left")
    if subtitle:
        ctk.CTkLabel(hdr, text=subtitle, font=FONT_SMALL,
                     text_color=TEXT_MUTED).pack(side="left", padx=(12, 0), pady=(8, 0))
    return hdr


def _stat_card(parent, title, value, color=ACCENT, subtitle=""):
    card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
    ctk.CTkLabel(card, text=str(value),
                 font=("Segoe UI", 32, "bold"), text_color=color).pack(pady=(16, 2))
    ctk.CTkLabel(card, text=title, font=FONT_SMALL, text_color=TEXT_MUTED).pack()
    if subtitle:
        ctk.CTkLabel(card, text=subtitle, font=("Segoe UI", 9),
                     text_color=TEXT_MUTED).pack(pady=(0, 4))
    ctk.CTkLabel(card, text="", font=("Segoe UI", 4)).pack(pady=(0, 10))
    return card


def _scrolled_tree(parent, cols, hdrs, widths, anchors=None):
    frame = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    CENTER_COLS = ("nota","estado","cedula","codigo","pos","cupos",
                   "creditos","semestre","edad","id","ciclo","num_ciclos","horas","hs")
    for c, h, w in zip(cols, hdrs, widths):
        tree.heading(c, text=h)
        anc = "center" if c in CENTER_COLS else "w"
        if anchors and c in anchors:
            anc = anchors[c]
        tree.column(c, width=w, anchor=anc)
    _tree_style(tree)
    tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
    sb = ctk.CTkScrollbar(frame, command=tree.yview)
    sb.grid(row=0, column=1, sticky="ns", pady=8)
    tree.configure(yscrollcommand=sb.set)
    return frame, tree


def _combo_widget(parent, values, placeholder, width=160, height=34):
    c = ctk.CTkComboBox(parent, values=values, width=width, height=height,
                        fg_color="#0d1117", border_color=BORDER,
                        text_color=TEXT, font=FONT_SMALL,
                        button_color=ACCENT, dropdown_fg_color=CARD2_BG,
                        dropdown_text_color=TEXT)
    c.set(placeholder)
    return c


def _filter_bar(parent, placeholders, on_filter):
    bar = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
    entries = []
    for ph in placeholders:
        e = ctk.CTkEntry(bar, placeholder_text=ph, height=34, width=180,
                         fg_color="#0d1117", border_color=BORDER,
                         text_color=TEXT, font=FONT_SMALL)
        e.pack(side="left", padx=(10, 4), pady=8)
        entries.append(e)
    ctk.CTkButton(bar, text="Filtrar", width=80, height=34,
                  fg_color=ACCENT, hover_color=ACCENT2,
                  command=on_filter).pack(side="left", padx=4)
    ctk.CTkButton(bar, text="Limpiar", width=70, height=34,
                  fg_color=CARD2_BG, hover_color=BORDER, text_color=TEXT_MUTED,
                  command=lambda: [e.delete(0, "end") for e in entries] or on_filter()
                  ).pack(side="left", padx=4)
    return bar, entries


def _render_matplotlib(frame, fig_func, empty_msg="Sin datos"):
    for w in frame.winfo_children():
        try: w.destroy()
        except: pass
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        fig = fig_func()
        if fig is None:
            ctk.CTkLabel(frame, text=empty_msg, font=FONT_SMALL,
                         text_color=TEXT_MUTED).pack(expand=True)
            return
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        plt.close(fig)
    except ImportError:
        ctk.CTkLabel(frame, text="pip install matplotlib",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(expand=True)


def _mpl_style(fig, axes_list):
    fig.patch.set_facecolor(CARD_BG)
    for ax in axes_list:
        ax.set_facecolor(CARD2_BG)
        ax.tick_params(colors=TEXT_MUTED, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
        ax.title.set_color(TEXT)
        ax.xaxis.label.set_color(TEXT_MUTED)
        ax.yaxis.label.set_color(TEXT_MUTED)


# =========================================================
# DASHBOARD ADMIN
# =========================================================
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(24, 4))
        ctk.CTkLabel(top, text="Kognos",
                     font=("Segoe UI", 26, "bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(top, text="  Sistema Academico Universitario",
                     font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(
            side="left", pady=(8, 0))

        self._sf = ctk.CTkFrame(self, fg_color="transparent")
        self._sf.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 12))
        for i in range(6):
            self._sf.grid_columnconfigure(i, weight=1)

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0, 24))
        bottom.grid_columnconfigure(0, weight=2)
        bottom.grid_columnconfigure(1, weight=3)
        bottom.grid_rowconfigure(0, weight=1)

        # Ranking
        rank_frame = ctk.CTkFrame(bottom, fg_color=CARD_BG, corner_radius=12)
        rank_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        rank_frame.grid_columnconfigure(0, weight=1)
        rank_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(rank_frame, text="Top 10 Estudiantes",
                     font=FONT_H2, text_color=TEXT).grid(
            row=0, column=0, sticky="w", padx=20, pady=(14, 6))
        self._rank_tree = ttk.Treeview(rank_frame,
            columns=("pos","nombre","carrera","prom"), show="headings")
        for col, w, lbl in [("pos",40,"#"),("nombre",180,"Estudiante"),
                             ("carrera",120,"Carrera"),("prom",70,"Prom.")]:
            self._rank_tree.heading(col, text=lbl)
            self._rank_tree.column(col, width=w,
                anchor="center" if col in ("pos","prom") else "w")
        _tree_style(self._rank_tree,
                    {"gold":"#f0c040","silver":"#aaaaaa","bronze":"#cd7f32","normal":TEXT})
        self._rank_tree.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0,8))
        sb = ctk.CTkScrollbar(rank_frame, command=self._rank_tree.yview)
        sb.grid(row=1, column=1, sticky="ns", pady=8)
        self._rank_tree.configure(yscrollcommand=sb.set)

        # Graficas
        self._charts = ctk.CTkFrame(bottom, fg_color=CARD_BG, corner_radius=12)
        self._charts.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(self._charts, text="Estadisticas Visuales",
                     font=FONT_H2, text_color=TEXT).pack(anchor="w", padx=20, pady=(14,4))
        self._chart_inner = ctk.CTkFrame(self._charts, fg_color="transparent")
        self._chart_inner.pack(fill="both", expand=True, padx=8, pady=(0,8))

    def refresh(self):
        for w in self._sf.winfo_children(): w.destroy()
        d  = self.ctrl.data
        ap = sum(1 for m in d.matriculas if m.nota >= 7.0)
        stats_data = [
            ("Estudiantes",  len(d.estudiantes),  ACCENT,   "Registrados"),
            ("Docentes",     len(d.docentes),      PURPLE,   "Activos"),
            ("Carreras",     len(d.carreras),      CYAN,     "Activas"),
            ("Asignaturas",  len(d.asignaturas),   WARN,     "Total"),
            ("Matriculas",   len(d.matriculas),    "#e67e22","Total"),
            ("Aprobados",    ap,                   SUCCESS,  "Nota >= 7"),
        ]
        for i, (t, v, c, s) in enumerate(stats_data):
            _stat_card(self._sf, t, v, c, s).grid(row=0, column=i, padx=4, sticky="ew")

        for row in self._rank_tree.get_children(): self._rank_tree.delete(row)
        nombres_carr = {c.codigo: c.nombre for c in d.carreras}
        promedios = []
        for e in d.estudiantes:
            notas = [m.nota for m in d.matriculas if m.estudiante.cedula == e.cedula]
            if notas:
                promedios.append((e, sum(notas)/len(notas)))
        promedios.sort(key=lambda x: x[1], reverse=True)
        for i, (e, prom) in enumerate(promedios[:10], 1):
            tag = "gold" if i==1 else ("silver" if i==2 else ("bronze" if i==3 else "normal"))
            nc  = nombres_carr.get(e.carrera, e.carrera)
            self._rank_tree.insert("", "end", tags=(tag,),
                values=(i, e.nombre, nc, f"{prom:.2f}"))

        self._render_charts()

    def _render_charts(self):
        def make_fig():
            import matplotlib.pyplot as plt
            import matplotlib.gridspec as gridspec
            d = self.ctrl.data
            fig = plt.figure(figsize=(8, 4), facecolor=CARD_BG)
            gs  = gridspec.GridSpec(1, 3, figure=fig, wspace=0.4)
            ax1 = fig.add_subplot(gs[0])
            ax2 = fig.add_subplot(gs[1])
            ax3 = fig.add_subplot(gs[2])
            _mpl_style(fig, [ax1, ax2, ax3])

            total = len(d.matriculas)
            if total:
                ap  = sum(1 for m in d.matriculas if m.nota >= 7.0)
                rep = total - ap
                wedges, texts, autotexts = ax1.pie(
                    [ap, rep], labels=["Aprobados","Reprobados"],
                    colors=[SUCCESS, DANGER], autopct="%1.1f%%", startangle=90,
                    textprops={"color": TEXT, "fontsize": 8},
                    wedgeprops={"edgecolor": CARD_BG, "linewidth": 2})
                for at in autotexts: at.set_color("white"); at.set_fontsize(8)
            else:
                ax1.text(0.5,0.5,"Sin datos",ha="center",va="center",
                          color=TEXT_MUTED,transform=ax1.transAxes)
            ax1.set_title("Aprobados / Reprobados", color=TEXT, fontsize=9, pad=6)

            por_c = {}
            for m in d.matriculas:
                por_c.setdefault(m.estudiante.carrera, []).append(m.nota)
            nombres_c = {c.codigo: c.nombre[:10] for c in d.carreras}
            if por_c:
                keys   = list(por_c.keys())
                labels = [nombres_c.get(k, k[:10]) for k in keys]
                vals   = [sum(v)/len(v) for v in por_c.values()]
                bars   = ax2.bar(labels, vals,
                                 color=[SUCCESS if v>=7 else DANGER for v in vals],
                                 edgecolor=CARD_BG, linewidth=1.5)
                ax2.axhline(7.0, color=WARN, linewidth=1.5, linestyle="--", alpha=0.8)
                ax2.set_ylim(0, 10)
                ax2.set_ylabel("Promedio", fontsize=8)
                for bar, val in zip(bars, vals):
                    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.15,
                              f"{val:.1f}", ha="center", va="bottom", color=TEXT, fontsize=7)
                ax2.tick_params(axis="x", labelsize=7)
            else:
                ax2.text(0.5,0.5,"Sin datos",ha="center",va="center",
                          color=TEXT_MUTED,transform=ax2.transAxes)
            ax2.set_title("Promedio por Carrera", color=TEXT, fontsize=9, pad=6)

            todas = [m.nota for m in d.matriculas]
            if todas:
                n, bins, patches = ax3.hist(todas, bins=10, range=(0,10),
                                             edgecolor=CARD_BG, linewidth=1.5)
                for patch, left in zip(patches, bins[:-1]):
                    patch.set_facecolor(SUCCESS if left>=7 else (WARN if left>=5 else DANGER))
                ax3.axvline(7.0, color=WARN, linewidth=1.5, linestyle="--", alpha=0.8)
                ax3.set_xlabel("Nota", fontsize=8)
                ax3.set_ylabel("Frecuencia", fontsize=8)
            else:
                ax3.text(0.5,0.5,"Sin datos",ha="center",va="center",
                          color=TEXT_MUTED,transform=ax3.transAxes)
            ax3.set_title("Distribucion de Notas", color=TEXT, fontsize=9, pad=6)
            fig.tight_layout(pad=1.5)
            return fig
        _render_matplotlib(self._chart_inner, make_fig)


# =========================================================
# DOCENTES PAGE
# =========================================================
class DocentesPage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(28,0))
        _header(top, "Docentes", "Gestion de docentes").pack(side="left")
        ctk.CTkButton(top, text="+ Nuevo Docente", height=36, width=150,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._nuevo).pack(side="right")
        fbar, self._filtros = _filter_bar(
            self, ["Nombre...", "Cedula...", "Especialidad..."], self._aplicar_filtro)
        fbar.grid(row=1, column=0, sticky="ew", padx=32, pady=8)
        tf, self._tree = _scrolled_tree(self,
            ("cedula","nombres","titulo","especialidad","email","telefono"),
            ("Cedula","Nombres","Titulo","Especialidad","Email","Telefono"),
            (120,200,120,170,180,120))
        tf.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0,8))
        bbar = ctk.CTkFrame(self, fg_color="transparent")
        bbar.grid(row=3, column=0, sticky="w", padx=32, pady=(0,20))
        ctk.CTkButton(bbar, text="Editar", width=100, height=34,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._editar).pack(side="left", padx=4)
        ctk.CTkButton(bbar, text="Eliminar", width=100, height=34,
                      fg_color=DANGER, hover_color="#b91c1c",
                      command=self._eliminar).pack(side="left", padx=4)
        ctk.CTkButton(bbar, text="Asignar Materia + Horario", width=200, height=34,
                      fg_color=PURPLE, hover_color="#7d3c98",
                      command=self._asignar).pack(side="left", padx=4)

    def refresh(self): self._aplicar_filtro()

    def _aplicar_filtro(self):
        for row in self._tree.get_children(): self._tree.delete(row)
        f0 = self._filtros[0].get().lower()
        f1 = self._filtros[1].get().lower()
        f2 = self._filtros[2].get().lower()
        for d in self.ctrl.data.docentes:
            if f0 and f0 not in d.nombres.lower(): continue
            if f1 and f1 not in d.cedula.lower(): continue
            if f2 and f2 not in d.especialidad.lower(): continue
            self._tree.insert("", "end",
                values=(d.cedula,d.nombres,d.titulo,d.especialidad,d.email,d.telefono))

    def _nuevo(self): DialogDocente(self, self.ctrl, on_save=self.refresh)

    def _get_sel(self):
        sel = self._tree.selection()
        if not sel: Info(self,"Aviso","Selecciona un docente."); return None
        ced = str(self._tree.item(sel[0])["values"][0])
        return next((d for d in self.ctrl.data.docentes if d.cedula==ced), None)

    def _editar(self):
        d = self._get_sel()
        if d: DialogDocente(self, self.ctrl, docente=d, on_save=self.refresh)

    def _eliminar(self):
        d = self._get_sel()
        if not d: return
        if Confirm(self,"Confirmar",f"Eliminar al docente '{d.nombres}'?"):
            ok, msg = self.ctrl.eliminar_docente(d.cedula)
            Info(self,"Resultado",msg); self.refresh()

    def _asignar(self):
        DialogAsignarDocenteHorario(self, self.ctrl, on_save=self.refresh)


# =========================================================
# CARRERAS PAGE
# =========================================================
class CarrerasPage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(28,0))
        _header(top, "Carreras y Materias", "Gestion por carrera y ciclo").pack(side="left")
        rb = ctk.CTkFrame(top, fg_color="transparent")
        rb.pack(side="right")
        ctk.CTkButton(rb, text="+ Nueva Carrera", height=36, width=140,
                      fg_color=SUCCESS, hover_color="#3fb950",
                      command=self._nueva_carrera).pack(side="left", padx=4)
        ctk.CTkButton(rb, text="+ Nueva Materia", height=36, width=140,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._nueva_materia).pack(side="left", padx=4)

        fbar, self._filtros = _filter_bar(
            self, ["Carrera/Codigo...", "Nombre materia...", "Ciclo..."],
            self._aplicar_filtro)
        fbar.grid(row=1, column=0, sticky="ew", padx=32, pady=8)

        tabs = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=8)
        tabs.grid(row=2, column=0, sticky="ew", padx=32, pady=(0,4))
        self._modo = ctk.StringVar(value="carreras")
        self._tab_btns = {}
        for text, val in [("Carreras","carreras"),("Materias","materias")]:
            b = ctk.CTkButton(tabs, text=text, height=34, width=150,
                              fg_color=ACCENT if val=="carreras" else "transparent",
                              hover_color=ACCENT2,
                              command=lambda v=val: self._switch_tab(v))
            b.pack(side="left", padx=4, pady=4)
            self._tab_btns[val] = b

        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.grid(row=3, column=0, sticky="nsew", padx=32)
        self._container.grid_columnconfigure(0, weight=1)
        self._container.grid_rowconfigure(0, weight=1)

        cf, self._tree_carr = _scrolled_tree(self._container,
            ("codigo","nombre","ciclos","desc","asigs","ests"),
            ("Codigo","Nombre","Ciclos","Descripcion","Materias","Estudiantes"),
            (80,220,60,200,70,80))
        cf.grid(row=0, column=0, sticky="nsew"); self._carr_frame = cf

        mf, self._tree_mat = _scrolled_tree(self._container,
            ("codigo","nombre","carrera","ciclo","hs","creditos","docente","horario"),
            ("Codigo","Materia","Carrera","Ciclo","H/Sem","Cred.","Docente","Horario"),
            (80,170,100,55,55,55,160,200))
        mf.grid(row=0, column=0, sticky="nsew"); self._mat_frame = mf

        bbar = ctk.CTkFrame(self, fg_color="transparent")
        bbar.grid(row=4, column=0, sticky="w", padx=32, pady=(4,20))
        ctk.CTkButton(bbar, text="Editar", width=100, height=34,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._editar).pack(side="left", padx=4)
        ctk.CTkButton(bbar, text="Eliminar", width=100, height=34,
                      fg_color=DANGER, hover_color="#b91c1c",
                      command=self._eliminar).pack(side="left", padx=4)
        ctk.CTkButton(bbar, text="Asignar Docente + Horario", width=200, height=34,
                      fg_color=PURPLE, hover_color="#7d3c98",
                      command=self._asignar_docente).pack(side="left", padx=4)
        self._switch_tab("carreras")

    def _switch_tab(self, modo):
        self._modo.set(modo)
        for k, b in self._tab_btns.items():
            b.configure(fg_color=ACCENT if k==modo else "transparent")
        if modo=="carreras":
            self._mat_frame.grid_remove(); self._carr_frame.grid()
        else:
            self._carr_frame.grid_remove(); self._mat_frame.grid()
        self._aplicar_filtro()

    def refresh(self): self._aplicar_filtro()

    def _aplicar_filtro(self):
        f0 = self._filtros[0].get().lower()
        f1 = self._filtros[1].get().lower()
        f2 = self._filtros[2].get().strip()
        dic_doc  = {d.cedula: d.nombres for d in self.ctrl.data.docentes}
        nombres_c = {c.codigo: c.nombre for c in self.ctrl.data.carreras}
        if self._modo.get()=="carreras":
            for row in self._tree_carr.get_children(): self._tree_carr.delete(row)
            for c in self.ctrl.data.carreras:
                if f0 and f0 not in c.codigo.lower() and f0 not in c.nombre.lower(): continue
                asigs = sum(1 for a in self.ctrl.data.asignaturas if a.carrera==c.codigo)
                ests  = sum(1 for e in self.ctrl.data.estudiantes if e.carrera==c.codigo)
                self._tree_carr.insert("","end",
                    values=(c.codigo,c.nombre,c.num_ciclos,c.descripcion[:40],asigs,ests))
        else:
            for row in self._tree_mat.get_children(): self._tree_mat.delete(row)
            for a in self.ctrl.data.asignaturas:
                if f0 and f0 not in a.carrera.lower() and f0 not in a.codigo.lower(): continue
                if f1 and f1 not in a.nombre.lower(): continue
                if f2 and str(a.semestre)!=f2: continue
                doc_n  = dic_doc.get(a.docente,"Sin asignar")
                carr_n = nombres_c.get(a.carrera, a.carrera)
                hor_str = ""
                if a.horario_id:
                    h = self.ctrl.data.horario_by_id(a.horario_id)
                    if h: hor_str = h.resumen()
                self._tree_mat.insert("","end",
                    values=(a.codigo,a.nombre,carr_n,a.semestre,
                            a.horas_semanales,a.creditos,doc_n,hor_str))

    def _nueva_carrera(self): DialogCarrera(self, self.ctrl, on_save=self.refresh)
    def _nueva_materia(self): DialogAsignatura(self, self.ctrl, on_save=self.refresh)

    def _editar(self):
        if self._modo.get()=="carreras":
            sel = self._tree_carr.selection()
            if not sel: Info(self,"Aviso","Selecciona una carrera."); return
            cod = str(self._tree_carr.item(sel[0])["values"][0])
            c = next((x for x in self.ctrl.data.carreras if x.codigo==cod),None)
            if c: DialogCarrera(self, self.ctrl, carrera=c, on_save=self.refresh)
        else:
            sel = self._tree_mat.selection()
            if not sel: Info(self,"Aviso","Selecciona una materia."); return
            cod = str(self._tree_mat.item(sel[0])["values"][0])
            a = next((x for x in self.ctrl.data.asignaturas if x.codigo==cod),None)
            if a: DialogAsignatura(self, self.ctrl, asignatura=a, on_save=self.refresh)

    def _eliminar(self):
        if self._modo.get()=="carreras":
            sel = self._tree_carr.selection()
            if not sel: Info(self,"Aviso","Selecciona una carrera."); return
            cod = str(self._tree_carr.item(sel[0])["values"][0])
            if Confirm(self,"Confirmar",f"Eliminar la carrera '{cod}'?"):
                ok, msg = self.ctrl.eliminar_carrera(cod)
                Info(self,"Resultado",msg); self.refresh()
        else:
            sel = self._tree_mat.selection()
            if not sel: Info(self,"Aviso","Selecciona una materia."); return
            cod = str(self._tree_mat.item(sel[0])["values"][0])
            if Confirm(self,"Confirmar",f"Eliminar la materia '{cod}'?"):
                ok, msg, n = self.ctrl.eliminar_asignatura(cod)
                Info(self,"Resultado",msg); self.refresh()

    def _asignar_docente(self):
        a = None
        if self._modo.get()=="materias":
            sel = self._tree_mat.selection()
            if not sel:
                Info(self,"Aviso","Selecciona una materia en el tab Materias."); return
            cod = str(self._tree_mat.item(sel[0])["values"][0])
            a   = next((x for x in self.ctrl.data.asignaturas if x.codigo==cod),None)
        elif self._modo.get()=="carreras":
            Info(self,"Aviso","Ve al tab 'Materias', selecciona una y presiona Asignar."); return
        DialogAsignarDocenteHorario(self, self.ctrl, asignatura=a, on_save=self.refresh)


# =========================================================
# HORARIOS PAGE
# =========================================================
class HorariosPage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(28,16))
        _header(top,"Horarios Registrados","Bloques asignados a materias").pack(side="left")
        hint = ctk.CTkFrame(top, fg_color=CARD_BG, corner_radius=8)
        hint.pack(side="right")
        ctk.CTkLabel(hint, text="Para crear: Carreras y Materias > Asignar Docente",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(padx=12, pady=6)
        tf, self._tree = _scrolled_tree(self,
            ("id","horario","horas","aula","docente","asigs"),
            ("ID","Bloques del Horario","H/Sem","Aula","Docente","Materia(s)"),
            (45,300,60,140,180,200))
        tf.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0,8))
        bbar = ctk.CTkFrame(self, fg_color="transparent")
        bbar.grid(row=2, column=0, sticky="w", padx=32, pady=(0,20))
        ctk.CTkButton(bbar, text="Eliminar", width=100, height=34,
                      fg_color=DANGER, hover_color="#b91c1c",
                      command=self._eliminar).pack(side="left", padx=4)

    def refresh(self):
        for row in self._tree.get_children(): self._tree.delete(row)
        dic_doc = {d.cedula: d.nombres for d in self.ctrl.data.docentes}
        asigs_por_hor = {}
        for a in self.ctrl.data.asignaturas:
            if a.horario_id:
                asigs_por_hor.setdefault(a.horario_id,[]).append((a.nombre, a.docente))
        for h in self.ctrl.data.horarios:
            info     = asigs_por_hor.get(h.id, [])
            asigs_s  = ", ".join(n for n,_ in info) or "---"
            docs     = list({dic_doc.get(ced,"") for _,ced in info if ced})
            doc_s    = ", ".join(d for d in docs if d) or "---"
            self._tree.insert("","end",
                values=(h.id,h.resumen(),f"{h.horas_semanales():.0f}",
                        h.aula,doc_s,asigs_s))

    def _eliminar(self):
        sel = self._tree.selection()
        if not sel: Info(self,"Aviso","Selecciona un horario."); return
        hid = int(self._tree.item(sel[0])["values"][0])
        if Confirm(self,"Confirmar","Eliminar este horario?"):
            ok, msg = self.ctrl.eliminar_horario(hid)
            Info(self,"Resultado",msg); self.refresh()


# =========================================================
# ESTUDIANTES PAGE
# =========================================================
class EstudiantesPage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(28,0))
        _header(top,"Estudiantes","Gestion y matriculas").pack(side="left")
        rb = ctk.CTkFrame(top, fg_color="transparent")
        rb.pack(side="right")
        ctk.CTkButton(rb, text="+ Nuevo", height=36, width=100,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._nuevo).pack(side="left", padx=4)
        ctk.CTkButton(rb, text="Matricular", height=36, width=120,
                      fg_color=SUCCESS, hover_color="#3fb950",
                      command=self._matricular).pack(side="left", padx=4)
        fbar, self._filtros = _filter_bar(
            self, ["Cedula...","Nombre...","Carrera...","Ciclo..."],
            self._aplicar_filtro)
        fbar.grid(row=1, column=0, sticky="ew", padx=32, pady=8)
        tf, self._tree = _scrolled_tree(self,
            ("cedula","nombre","edad","carrera","ciclo","email","mats"),
            ("Cedula","Nombre","Edad","Carrera","Ciclo","Email","Mats."),
            (110,200,55,150,55,190,55))
        tf.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0,8))
        bbar = ctk.CTkFrame(self, fg_color="transparent")
        bbar.grid(row=3, column=0, sticky="w", padx=32, pady=(0,20))
        for text, cmd, color, hov in [
            ("Editar",       self._editar,    ACCENT, ACCENT2),
            ("Eliminar",     self._eliminar,  DANGER, "#b91c1c"),
            ("PDF Matricula", self._pdf,      WARN,   "#b7770d"),
            ("Historial",    self._historial, PURPLE, "#7d3c98"),
        ]:
            ctk.CTkButton(bbar, text=text, width=130, height=34,
                          fg_color=color, hover_color=hov,
                          command=cmd).pack(side="left", padx=4)

    def refresh(self): self._aplicar_filtro()

    def _aplicar_filtro(self):
        for row in self._tree.get_children(): self._tree.delete(row)
        f0 = self._filtros[0].get().lower()
        f1 = self._filtros[1].get().lower()
        f2 = self._filtros[2].get().lower()
        f3 = self._filtros[3].get().strip()
        nombres_c = {c.codigo: c.nombre for c in self.ctrl.data.carreras}
        for e in self.ctrl.data.estudiantes:
            if f0 and f0 not in e.cedula.lower(): continue
            if f1 and f1 not in e.nombre.lower(): continue
            nc = nombres_c.get(e.carrera, e.carrera)
            if f2 and f2 not in e.carrera.lower() and f2 not in nc.lower(): continue
            if f3 and str(e.semestre)!=f3: continue
            mats = sum(1 for m in self.ctrl.data.matriculas
                       if m.estudiante.cedula==e.cedula)
            self._tree.insert("","end",
                values=(e.cedula,e.nombre,e.edad,nc,e.semestre,e.email,mats))

    def _nuevo(self): DialogEstudiante(self, self.ctrl, on_save=self.refresh)

    def _get_sel(self):
        sel = self._tree.selection()
        if not sel: Info(self,"Aviso","Selecciona un estudiante."); return None
        ced = str(self._tree.item(sel[0])["values"][0])
        return next((e for e in self.ctrl.data.estudiantes if e.cedula==ced), None)

    def _editar(self):
        e = self._get_sel()
        if e: DialogEstudiante(self, self.ctrl, estudiante=e, on_save=self.refresh)

    def _eliminar(self):
        e = self._get_sel()
        if not e: return
        if Confirm(self,"Confirmar",f"Eliminar al estudiante '{e.nombre}'?"):
            ok, msg, n = self.ctrl.eliminar_estudiante(e.cedula)
            Info(self,"Resultado",msg); self.refresh()

    def _matricular(self): DialogMatricula(self, self.ctrl, on_save=self.refresh)

    def _pdf(self):
        e = self._get_sel()
        if not e: return
        ruta = filedialog.asksaveasfilename(
            parent=self, defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")],
            initialfile=f"matricula_{e.cedula}.pdf")
        if ruta:
            ok, msg = self.ctrl.generar_pdf_matricula(e.cedula, ruta)
            Info(self,"PDF",msg)

    def _historial(self):
        e = self._get_sel()
        if e: _mostrar_historial(self, self.ctrl, e.cedula, e.nombre)


# =========================================================
# BUSQUEDA AVANZADA
# =========================================================
class BusquedaPage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        _header(self,"Busqueda Avanzada","Filtros multiples sobre matriculas").grid(
            row=0, column=0, sticky="w", padx=32, pady=(28,12))
        fcard = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10)
        fcard.grid(row=1, column=0, sticky="ew", padx=32, pady=(0,10))
        row1 = ctk.CTkFrame(fcard, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(12,4))

        carr_opts = ["(todas las carreras)"] + [
            f"{c.codigo} - {c.nombre}" for c in self.ctrl.data.carreras]
        self._cb_carr = _combo_widget(row1, carr_opts, "(todas las carreras)", 220)
        self._cb_carr.pack(side="left", padx=(0,8))

        self._cb_cic = _combo_widget(
            row1, ["(todos los ciclos)"] + SEMESTRES, "(todos los ciclos)", 160)
        self._cb_cic.pack(side="left", padx=(0,8))

        self._cb_est = _combo_widget(
            row1, ["(todos)","Aprobado","Reprobado"], "(todos)", 140)
        self._cb_est.pack(side="left", padx=(0,8))

        doc_opts = ["(todos los docentes)"] + [
            f"{d.cedula} - {d.nombres}" for d in self.ctrl.data.docentes]
        self._cb_doc = _combo_widget(row1, doc_opts, "(todos los docentes)", 200)
        self._cb_doc.pack(side="left", padx=(0,8))

        ctk.CTkButton(row1, text="Buscar", width=80, height=34,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self.refresh).pack(side="left", padx=4)
        ctk.CTkButton(row1, text="Limpiar", width=70, height=34,
                      fg_color=CARD2_BG, hover_color=BORDER, text_color=TEXT_MUTED,
                      command=self._limpiar).pack(side="left", padx=2)
        self._lbl_count = ctk.CTkLabel(fcard, text="", font=FONT_SMALL,
                                        text_color=TEXT_MUTED)
        self._lbl_count.pack(anchor="w", padx=16, pady=(0,10))

        tf, self._tree = _scrolled_tree(self,
            ("cedula","nombre","carrera","ciclo","asig","nota","estado","periodo"),
            ("Cedula","Estudiante","Carrera","Ciclo","Asignatura","Nota","Estado","Periodo"),
            (110,170,120,55,170,60,90,80))
        _tree_style(self._tree, {"Aprobado":SUCCESS,"Reprobado":DANGER})
        tf.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0,20))

    def _limpiar(self):
        self._cb_carr.set("(todas las carreras)")
        self._cb_cic.set("(todos los ciclos)")
        self._cb_est.set("(todos)")
        self._cb_doc.set("(todos los docentes)")
        self.refresh()

    def refresh(self):
        for row in self._tree.get_children(): self._tree.delete(row)
        carr_sel = self._cb_carr.get()
        carrera  = carr_sel.split(" - ")[0] if " - " in carr_sel else ""
        cic_sel  = self._cb_cic.get()
        ciclo    = cic_sel if cic_sel not in ("(todos los ciclos)","") else ""
        estado   = self._cb_est.get()
        if estado=="(todos)": estado=""
        doc_sel  = self._cb_doc.get()
        docente  = doc_sel.split(" - ")[0] if " - " in doc_sel else ""
        rows     = self.ctrl.busqueda_avanzada(carrera, ciclo, estado, docente)
        nombres_c = {c.codigo: c.nombre for c in self.ctrl.data.carreras}
        for r in rows:
            nc = nombres_c.get(r["carrera"], r["carrera"])
            self._tree.insert("","end", tags=(r["estado"],),
                values=(r["cedula"],r["nombre"],nc,r["semestre"],
                        r["asig_nombre"],f"{r['nota']:.2f}",r["estado"],r["periodo"]))
        self._lbl_count.configure(text=f"  {len(rows)} resultado(s)")


# =========================================================
# HISTORIAL helpers
# =========================================================
def _mostrar_historial(parent, ctrl, cedula, nombre):
    from view.dialogs import _base_dialog
    win = _base_dialog(parent, f"Historial - {nombre}", 700, 520)
    win.grid_columnconfigure(0, weight=1)
    win.grid_rowconfigure(1, weight=1)
    ctk.CTkLabel(win, text=f"Historial de {nombre}",
                 font=FONT_H2, text_color=TEXT).grid(
        row=0, column=0, sticky="w", padx=20, pady=(16,8))
    tf, tree = _scrolled_tree(win,
        ("periodo","codigo","asig","nota","creditos","estado"),
        ("Periodo","Codigo","Asignatura","Nota","Cred.","Estado"),
        (80,80,220,70,60,90))
    _tree_style(tree, {"Aprobado":SUCCESS,"Reprobado":DANGER})
    tf.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0,10))
    rows = ctrl.historial_estudiante(cedula)
    total_cred = 0; total_pond = 0
    for r in rows:
        estado = "Aprobado" if r["nota"]>=7.0 else "Reprobado"
        tree.insert("","end", tags=(estado,),
            values=(r["periodo"],r["codigo"],r["nombre_asig"],
                    f"{r['nota']:.2f}",r["creditos"],estado))
        total_cred += r["creditos"]; total_pond += r["nota"]*r["creditos"]
    prom_h = total_pond/total_cred if total_cred else 0
    ctk.CTkLabel(win,
        text=f"  Promedio ponderado historico: {prom_h:.2f}  |  Creditos cursados: {total_cred}",
        font=FONT_SMALL, text_color=TEXT_MUTED).grid(
        row=2, column=0, sticky="w", padx=20, pady=(0,16))


class HistorialPage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, cedula_fija=None, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl; self.cedula_fija = cedula_fija
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        _header(self,"Historial Academico","Registro historico de notas").grid(
            row=0, column=0, sticky="w", padx=32, pady=(28,12))
        sel_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10)
        sel_frame.grid(row=1, column=0, sticky="ew", padx=32, pady=(0,10))
        if not self.cedula_fija:
            ests = [f"{e.cedula} - {e.nombre}" for e in self.ctrl.data.estudiantes]
            self._cb_est = _combo_widget(sel_frame,
                ests if ests else ["(ninguno)"], "(seleccionar estudiante)", 320, 36)
            self._cb_est.pack(side="left", padx=12, pady=10)
            ctk.CTkButton(sel_frame, text="Ver Historial", height=36, width=130,
                          fg_color=ACCENT, hover_color=ACCENT2,
                          command=self.refresh).pack(side="left", padx=4)
        else:
            e = next((x for x in self.ctrl.data.estudiantes
                      if x.cedula==self.cedula_fija), None)
            txt = f"Estudiante: {e.nombre} - {e.cedula}" if e else self.cedula_fija
            ctk.CTkLabel(sel_frame, text=txt, font=FONT_BODY,
                         text_color=TEXT).pack(side="left", padx=12, pady=10)
        tf, self._tree = _scrolled_tree(self,
            ("periodo","codigo","asig","nota","creditos","estado"),
            ("Periodo","Codigo","Asignatura","Nota","Cred.","Estado"),
            (80,80,250,70,60,100))
        _tree_style(self._tree, {"Aprobado":SUCCESS,"Reprobado":DANGER})
        tf.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0,8))
        self._lbl_prom = ctk.CTkLabel(self, text="", font=FONT_SMALL, text_color=TEXT_MUTED)
        self._lbl_prom.grid(row=3, column=0, sticky="w", padx=32, pady=(0,20))

    def refresh(self):
        for row in self._tree.get_children(): self._tree.delete(row)
        cedula = self.cedula_fija
        if not cedula and hasattr(self,"_cb_est"):
            sel = self._cb_est.get()
            cedula = sel.split(" - ")[0] if " - " in sel else None
        if not cedula: return
        rows = self.ctrl.historial_estudiante(cedula)
        total_cred = 0; total_pond = 0
        for r in rows:
            estado = "Aprobado" if r["nota"]>=7.0 else "Reprobado"
            self._tree.insert("","end", tags=(estado,),
                values=(r["periodo"],r["codigo"],r["nombre_asig"],
                        f"{r['nota']:.2f}",r["creditos"],estado))
            total_cred += r["creditos"]; total_pond += r["nota"]*r["creditos"]
        prom_h = total_pond/total_cred if total_cred else 0
        self._lbl_prom.configure(
            text=f"  Promedio ponderado: {prom_h:.2f}  |  Creditos: {total_cred}")


# =========================================================
# REPORTES PAGE -- con graficas
# =========================================================
class ReportesPage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, es_admin=True, cedula_fija=None, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl=ctrl; self.es_admin=es_admin; self.cedula_fija=cedula_fija
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        _header(self,"Reportes y Graficas","Informes visuales del sistema").grid(
            row=0, column=0, sticky="w", padx=32, pady=(28,16))
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0,20))
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=12, width=220)
        panel.grid(row=0, column=0, sticky="ns", padx=(0,12))
        panel.grid_propagate(False)
        ctk.CTkLabel(panel, text="Reportes con Grafica",
                     font=("Segoe UI",11,"bold"), text_color=TEXT_MUTED
                     ).pack(anchor="w", padx=16, pady=(16,8))

        def btn(text, cmd, color=ACCENT):
            ctk.CTkButton(panel, text=text, height=36, width=190,
                          fg_color=color, hover_color=ACCENT2,
                          anchor="w", command=cmd).pack(padx=14, pady=3)

        if self.es_admin:
            btn("Estadisticas Generales",   self._r_stats)
            btn("Aprobados / Reprobados",   self._r_estados)
            btn("Ranking Estudiantes",      self._r_ranking)
            btn("Promedio por Carrera",     self._r_por_carrera)
            btn("Promedio Estudiante",      self._r_prom_est)
        else:
            btn("Mis Estadisticas",         self._r_stats)

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(panel, text="Exportar",
                     font=("Segoe UI",11,"bold"), text_color=TEXT_MUTED
                     ).pack(anchor="w", padx=16, pady=(4,6))
        if self.es_admin:
            btn("PDF Matricula",            self._pdf_matricula, WARN)
            btn("Excel por Asignatura",     self._excel_asig, SUCCESS)
        else:
            btn("Excel mis notas",          self._excel_asig, SUCCESS)

        self._chart_area = ctk.CTkFrame(content, fg_color=CARD_BG, corner_radius=12)
        self._chart_area.grid(row=0, column=1, sticky="nsew")
        self._chart_title = ctk.CTkLabel(self._chart_area, text="",
                                          font=FONT_H2, text_color=TEXT)
        self._chart_title.pack(anchor="w", padx=20, pady=(14,4))
        self._chart_inner = ctk.CTkFrame(self._chart_area, fg_color="transparent")
        self._chart_inner.pack(fill="both", expand=True, padx=8, pady=(0,8))

    def refresh(self): pass
    def _set_title(self, t): self._chart_title.configure(text=t)

    def _r_stats(self):
        self._set_title("Estadisticas Generales")
        def make_fig():
            import matplotlib.pyplot as plt
            d = self.ctrl.data
            stats = d.estadisticas_sql()
            if not stats or not stats["total_matriculas"]: return None
            fig, axes = plt.subplots(1, 3, figsize=(9,3.5), facecolor=CARD_BG)
            _mpl_style(fig, axes)
            ap = stats["aprobados"]; rep = stats["reprobados"]
            axes[0].pie([ap,rep], labels=["Aprobados","Reprobados"],
                        colors=[SUCCESS,DANGER], autopct="%1.1f%%", startangle=90,
                        textprops={"color":TEXT,"fontsize":8},
                        wedgeprops={"edgecolor":CARD_BG,"linewidth":2})
            axes[0].set_title("Tasa Global", color=TEXT, fontsize=9)
            labels = ["Promedio","Nota Max","Nota Min"]
            vals = [stats["promedio"] or 0, stats["max_nota"] or 0, stats["min_nota"] or 0]
            bars = axes[1].bar(labels, vals, color=[ACCENT,SUCCESS,DANGER],
                               edgecolor=CARD_BG, linewidth=2)
            axes[1].set_ylim(0,10)
            axes[1].axhline(7.0, color=WARN, linewidth=1.5, linestyle="--", alpha=0.7)
            for bar, val in zip(bars, vals):
                axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                              f"{val:.2f}", ha="center", color=TEXT, fontsize=9, fontweight="bold")
            axes[1].set_title("Metricas de Notas", color=TEXT, fontsize=9)
            labels2 = ["Estudiantes","Asignaturas","Matriculas","Carreras"]
            vals2   = [len(d.estudiantes),len(d.asignaturas),len(d.matriculas),len(d.carreras)]
            bars2 = axes[2].barh(labels2, vals2, color=[ACCENT,PURPLE,WARN,CYAN],
                                  edgecolor=CARD_BG, linewidth=1.5)
            for bar, val in zip(bars2, vals2):
                axes[2].text(bar.get_width()+0.2, bar.get_y()+bar.get_height()/2,
                              str(val), va="center", color=TEXT, fontsize=9)
            axes[2].set_title("Totales del Sistema", color=TEXT, fontsize=9)
            fig.tight_layout(pad=1.5)
            return fig
        _render_matplotlib(self._chart_inner, make_fig, "No hay datos suficientes")

    def _r_estados(self):
        self._set_title("Aprobados vs Reprobados por Asignatura")
        def make_fig():
            import matplotlib.pyplot as plt
            d = self.ctrl.data
            data_asigs = []
            for a in d.asignaturas:
                mats = [m for m in d.matriculas if m.asignatura.codigo==a.codigo]
                if not mats: continue
                ap = sum(1 for m in mats if m.nota>=7.0)
                data_asigs.append((a.nombre[:14], ap, len(mats)-ap, len(mats)))
            if not data_asigs: return None
            data_asigs.sort(key=lambda x: x[3], reverse=True)
            data_asigs = data_asigs[:12]
            names = [x[0] for x in data_asigs]
            aps   = [x[1] for x in data_asigs]
            reps  = [x[2] for x in data_asigs]
            fig, ax = plt.subplots(figsize=(9, max(3.5,len(names)*0.45)), facecolor=CARD_BG)
            _mpl_style(fig, [ax])
            y = list(range(len(names)))
            ax.barh(y, aps,  color=SUCCESS, label="Aprobados",  edgecolor=CARD_BG, linewidth=1)
            ax.barh(y, reps, left=aps, color=DANGER, label="Reprobados", edgecolor=CARD_BG, linewidth=1)
            ax.set_yticks(y); ax.set_yticklabels(names, fontsize=8)
            ax.set_xlabel("Estudiantes", fontsize=8)
            ax.legend(fontsize=8, facecolor=CARD2_BG, labelcolor=TEXT, edgecolor=BORDER, loc="lower right")
            for i,(ap,rep,total) in enumerate([(x[1],x[2],x[3]) for x in data_asigs]):
                pct = ap/total*100 if total else 0
                ax.text(total+0.2, i, f"{pct:.0f}%", va="center",
                         color=SUCCESS if pct>=70 else DANGER, fontsize=7)
            ax.set_title("Aprobados vs Reprobados por Materia", color=TEXT, fontsize=10)
            fig.tight_layout(pad=1.5)
            return fig
        _render_matplotlib(self._chart_inner, make_fig, "No hay matriculas registradas")

    def _r_ranking(self):
        self._set_title("Ranking de Estudiantes")
        def make_fig():
            import matplotlib.pyplot as plt
            d = self.ctrl.data
            promedios = []
            for e in d.estudiantes:
                notas = [m.nota for m in d.matriculas if m.estudiante.cedula==e.cedula]
                if notas: promedios.append((e.nombre[:16], sum(notas)/len(notas)))
            if not promedios: return None
            promedios.sort(key=lambda x: x[1], reverse=True)
            top = promedios[:15]
            names = [x[0] for x in top]; vals = [x[1] for x in top]
            colors_bar = [SUCCESS if v>=7 else (WARN if v>=5 else DANGER) for v in vals]
            fig, ax = plt.subplots(figsize=(9, max(4,len(top)*0.4)), facecolor=CARD_BG)
            _mpl_style(fig, [ax])
            bars = ax.barh(names[::-1], vals[::-1], color=colors_bar[::-1],
                           edgecolor=CARD_BG, linewidth=1.5)
            ax.axvline(7.0, color=WARN, linewidth=1.5, linestyle="--", alpha=0.8, label="Min. 7.0")
            ax.set_xlim(0,10)
            ax.set_xlabel("Promedio", fontsize=8)
            for bar, val in zip(bars, vals[::-1]):
                ax.text(bar.get_width()+0.1, bar.get_y()+bar.get_height()/2,
                         f"{val:.2f}", va="center", color=TEXT, fontsize=8)
            ax.legend(fontsize=8, facecolor=CARD2_BG, labelcolor=TEXT, edgecolor=BORDER)
            ax.set_title("Top 15 Estudiantes por Promedio", color=TEXT, fontsize=10)
            fig.tight_layout(pad=1.5)
            return fig
        _render_matplotlib(self._chart_inner, make_fig, "No hay notas registradas")

    def _r_por_carrera(self):
        self._set_title("Promedio y Tasas por Carrera")
        def make_fig():
            import matplotlib.pyplot as plt
            rows = self.ctrl.data.stats_por_carrera()
            nombres_c = {c.codigo: c.nombre[:12] for c in self.ctrl.data.carreras}
            rows = [r for r in rows if r["total_mat"] and r["total_mat"]>0]
            if not rows: return None
            fig, axes = plt.subplots(1, 2, figsize=(9,4), facecolor=CARD_BG)
            _mpl_style(fig, axes)
            labels    = [nombres_c.get(r["carrera"],r["carrera"][:12]) for r in rows]
            promedios = [r["promedio"] or 0 for r in rows]
            tasas     = [(r["aprobados"]/r["total_mat"]*100) if r["total_mat"] else 0 for r in rows]
            bars1 = axes[0].bar(labels, promedios,
                color=[SUCCESS if p>=7 else DANGER for p in promedios],
                edgecolor=CARD_BG, linewidth=1.5)
            axes[0].axhline(7.0, color=WARN, linewidth=1.5, linestyle="--", alpha=0.8)
            axes[0].set_ylim(0,10)
            for bar, val in zip(bars1, promedios):
                axes[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                              f"{val:.1f}", ha="center", color=TEXT, fontsize=8)
            axes[0].set_title("Promedio por Carrera", color=TEXT, fontsize=9)
            axes[0].tick_params(axis="x", labelsize=7, rotation=15)
            bars2 = axes[1].bar(labels, tasas,
                color=[SUCCESS if t>=70 else (WARN if t>=50 else DANGER) for t in tasas],
                edgecolor=CARD_BG, linewidth=1.5)
            axes[1].set_ylim(0,105)
            for bar, val in zip(bars2, tasas):
                axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                              f"{val:.0f}%", ha="center", color=TEXT, fontsize=8)
            axes[1].set_title("Tasa de Aprobacion (%)", color=TEXT, fontsize=9)
            axes[1].tick_params(axis="x", labelsize=7, rotation=15)
            fig.tight_layout(pad=1.5)
            return fig
        _render_matplotlib(self._chart_inner, make_fig, "No hay datos por carrera")

    def _r_prom_est(self):
        self._set_title("Promedio por Estudiante")
        if not self.ctrl.data.estudiantes:
            Info(self,"Aviso","No hay estudiantes registrados."); return
        opts = [f"{e.cedula} - {e.nombre}" for e in self.ctrl.data.estudiantes]
        win  = ctk.CTkToplevel(self)
        win.title("Seleccionar Estudiante")
        win.geometry("380x160"); win.configure(fg_color=BG); win.grab_set()
        win.grid_columnconfigure(0, weight=1)
        cb = _combo_widget(win, opts, "(seleccionar estudiante)", 340, 36)
        cb.pack(padx=20, pady=20)
        def go():
            sel = cb.get()
            if " - " in sel:
                ced = sel.split(" - ")[0]; win.destroy()
                self._render_promedio_est(ced)
        ctk.CTkButton(win, text="Ver Grafica", height=36, fg_color=ACCENT,
                      hover_color=ACCENT2, command=go).pack()

    def _render_promedio_est(self, cedula):
        e = next((x for x in self.ctrl.data.estudiantes if x.cedula==cedula),None)
        if not e: return
        self._set_title(f"Notas de {e.nombre}")
        def make_fig():
            import matplotlib.pyplot as plt
            mats = [m for m in self.ctrl.data.matriculas if m.estudiante.cedula==cedula]
            if not mats: return None
            nombres = [m.asignatura.nombre[:14] for m in mats]
            notas   = [m.nota for m in mats]
            colors_bar = [SUCCESS if n>=7 else (WARN if n>=5 else DANGER) for n in notas]
            fig, axes = plt.subplots(1, 2, figsize=(9,4), facecolor=CARD_BG)
            _mpl_style(fig, axes)
            axes[0].barh(nombres, notas, color=colors_bar, edgecolor=CARD_BG, linewidth=1.5)
            axes[0].axvline(7.0, color=WARN, linewidth=1.5, linestyle="--", alpha=0.8)
            axes[0].set_xlim(0,10)
            for i,(nom,nota) in enumerate(zip(nombres,notas)):
                axes[0].text(nota+0.1, i, f"{nota:.1f}", va="center", color=TEXT, fontsize=8)
            axes[0].set_title(f"Notas de {e.nombre[:20]}", color=TEXT, fontsize=9)
            ap  = sum(1 for n in notas if n>=7)
            rep = len(notas)-ap
            slices = [ap,rep] if rep>0 else [ap]
            labels = ["Aprobadas","Reprobadas"][:1 if rep==0 else 2]
            colors = [SUCCESS,DANGER][:1 if rep==0 else 2]
            axes[1].pie(slices, labels=labels, colors=colors, autopct="%1.1f%%",
                        startangle=90, textprops={"color":TEXT,"fontsize":9},
                        wedgeprops={"edgecolor":CARD_BG,"linewidth":2})
            axes[1].set_title("Estado de Materias", color=TEXT, fontsize=9)
            fig.tight_layout(pad=1.5)
            return fig
        _render_matplotlib(self._chart_inner, make_fig)

    def _pdf_matricula(self):
        cedula = self.cedula_fija
        if not cedula:
            if not self.ctrl.data.estudiantes:
                Info(self,"Aviso","No hay estudiantes."); return
            opts = [f"{e.cedula} - {e.nombre}" for e in self.ctrl.data.estudiantes]
            win  = ctk.CTkToplevel(self)
            win.title("Seleccionar Estudiante")
            win.geometry("380x140"); win.configure(fg_color=BG); win.grab_set()
            cb = _combo_widget(win, opts, "(seleccionar estudiante)", 340, 36)
            cb.pack(padx=20, pady=20)
            def go():
                sel = cb.get()
                if " - " in sel:
                    ced = sel.split(" - ")[0]; win.destroy(); self._hacer_pdf(ced)
            ctk.CTkButton(win, text="Generar PDF", height=36, fg_color=ACCENT,
                          hover_color=ACCENT2, command=go).pack()
        else:
            self._hacer_pdf(cedula)

    def _hacer_pdf(self, cedula):
        ruta = filedialog.asksaveasfilename(
            parent=self, defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")],
            initialfile=f"matricula_{cedula}.pdf")
        if ruta:
            ok, msg = self.ctrl.generar_pdf_matricula(cedula, ruta)
            Info(self,"PDF",msg)

    def _excel_asig(self):
        if not self.ctrl.data.asignaturas:
            Info(self,"Aviso","No hay asignaturas registradas."); return
        cedula_doc = self.ctrl.cedula_activa() if self.ctrl.es_docente() else None
        asigs = ([a for a in self.ctrl.data.asignaturas if a.docente==cedula_doc]
                 if cedula_doc else self.ctrl.data.asignaturas)
        if not asigs:
            Info(self,"Aviso","No tienes asignaturas asignadas."); return
        opts = [f"{a.codigo} - {a.nombre}" for a in asigs]
        win  = ctk.CTkToplevel(self)
        win.title("Seleccionar Asignatura")
        win.geometry("400x150"); win.configure(fg_color=BG); win.grab_set()
        win.grid_columnconfigure(0, weight=1)
        cb = _combo_widget(win, opts, opts[0] if opts else "(ninguna)", 360, 36)
        cb.pack(padx=20, pady=20)
        if opts: cb.set(opts[0])
        def go():
            sel = cb.get()
            if " - " in sel:
                cod = sel.split(" - ")[0]; win.destroy()
                ruta = filedialog.asksaveasfilename(
                    parent=self, defaultextension=".xlsx",
                    filetypes=[("Excel","*.xlsx")],
                    initialfile=f"lista_{cod}.xlsx")
                if ruta:
                    ok, msg = self.ctrl.exportar_excel_curso(cod, ruta)
                    Info(self,"Excel",msg)
        ctk.CTkButton(win, text="Generar Excel", height=36,
                      fg_color=SUCCESS, hover_color="#3fb950", command=go).pack()


# =========================================================
# DASHBOARD DOCENTE
# =========================================================
class DashboardDocentePage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl; self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(24,4))
        ctk.CTkLabel(top, text="Kognos",
                     font=("Segoe UI",24,"bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(top, text="  Panel del Docente",
                     font=("Segoe UI",13), text_color=TEXT_MUTED).pack(side="left", pady=(7,0))
        self._sf = ctk.CTkFrame(self, fg_color="transparent")
        self._sf.grid(row=1, column=0, sticky="ew", padx=32, pady=(0,12))
        for i in range(4): self._sf.grid_columnconfigure(i, weight=1)
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0,24))
        bottom.grid_columnconfigure(0, weight=2)
        bottom.grid_columnconfigure(1, weight=3)
        bottom.grid_rowconfigure(0, weight=1)
        mat_f = ctk.CTkFrame(bottom, fg_color=CARD_BG, corner_radius=12)
        mat_f.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        mat_f.grid_columnconfigure(0, weight=1)
        mat_f.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(mat_f, text="Mis Materias",
                     font=FONT_H2, text_color=TEXT).grid(
            row=0, column=0, sticky="w", padx=20, pady=(14,6))
        self._mat_tree = ttk.Treeview(mat_f,
            columns=("codigo","nombre","ciclo","total","aprobados","prom"),
            show="headings")
        for col, w, lbl in [("codigo",70,"Codigo"),("nombre",150,"Materia"),
                             ("ciclo",50,"Ciclo"),("total",55,"Total"),
                             ("aprobados",80,"Aprobados"),("prom",70,"Prom.")]:
            self._mat_tree.heading(col, text=lbl)
            self._mat_tree.column(col, width=w, anchor="w" if col=="nombre" else "center")
        _tree_style(self._mat_tree)
        self._mat_tree.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0,8))
        sb = ctk.CTkScrollbar(mat_f, command=self._mat_tree.yview)
        sb.grid(row=1, column=1, sticky="ns", pady=8)
        self._mat_tree.configure(yscrollcommand=sb.set)
        self._chart_frame = ctk.CTkFrame(bottom, fg_color=CARD_BG, corner_radius=12)
        self._chart_frame.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(self._chart_frame, text="Aprobacion por Materia",
                     font=FONT_H2, text_color=TEXT).pack(anchor="w", padx=20, pady=(14,4))
        self._chart_inner = ctk.CTkFrame(self._chart_frame, fg_color="transparent")
        self._chart_inner.pack(fill="both", expand=True, padx=8, pady=(0,8))

    def refresh(self):
        cedula = self.ctrl.cedula_activa()
        if not cedula: return
        for row in self._mat_tree.get_children(): self._mat_tree.delete(row)
        for w in self._sf.winfo_children(): w.destroy()
        stats = self.ctrl.stats_docente(cedula)
        total_mat = sum(r["total"] for r in stats)
        total_ap  = sum(r["aprobados"] for r in stats)
        total_rep = sum(r["reprobados"] for r in stats)
        for i,(t,v,c) in enumerate([
            ("Mis Materias",len(stats),ACCENT),
            ("Estudiantes",total_mat,CYAN),
            ("Aprobados",total_ap,SUCCESS),
            ("Reprobados",total_rep,DANGER),
        ]): _stat_card(self._sf,t,v,c).grid(row=0,column=i,padx=4,sticky="ew")
        for r in stats:
            self._mat_tree.insert("","end",
                values=(r["codigo"],r["asig_nombre"],r["semestre"],
                        r["total"],r["aprobados"],
                        f"{r['promedio']:.2f}" if r["promedio"] else "---"))
        def make_fig():
            import matplotlib.pyplot as plt
            if not stats: return None
            nombres = [r["asig_nombre"][:14] for r in stats]
            ap_pct  = [(r["aprobados"]/r["total"]*100 if r["total"] else 0) for r in stats]
            fig, ax = plt.subplots(figsize=(6,max(3,len(nombres)*0.55)), facecolor=CARD_BG)
            _mpl_style(fig, [ax])
            colors_bar = [SUCCESS if p>=70 else (WARN if p>=50 else DANGER) for p in ap_pct]
            bars = ax.barh(nombres, ap_pct, color=colors_bar, edgecolor=CARD_BG, linewidth=1.5)
            ax.axvline(70, color=WARN, linewidth=1.5, linestyle="--", alpha=0.8, label="Meta 70%")
            ax.set_xlim(0,105)
            ax.set_xlabel("% Aprobados", fontsize=8)
            for bar, val in zip(bars, ap_pct):
                ax.text(bar.get_width()+1, bar.get_y()+bar.get_height()/2,
                         f"{val:.0f}%", va="center", color=TEXT, fontsize=8)
            ax.legend(fontsize=8, facecolor=CARD2_BG, labelcolor=TEXT, edgecolor=BORDER)
            ax.set_title("Tasa de Aprobacion por Materia", color=TEXT, fontsize=9)
            fig.tight_layout(pad=1.5)
            return fig
        _render_matplotlib(self._chart_inner, make_fig, "Sin datos aun")


# =========================================================
# NOTAS DOCENTE
# =========================================================
class NotasDocentePage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl; self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        _header(self,"Gestion de Notas","Selecciona tu materia y edita las notas").grid(
            row=0, column=0, sticky="w", padx=32, pady=(28,12))
        fcard = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10)
        fcard.grid(row=1, column=0, sticky="ew", padx=32, pady=(0,10))
        row1 = ctk.CTkFrame(fcard, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(12,4))
        self._cb_asig = _combo_widget(
            row1, ["(selecciona una materia)"], "(selecciona una materia)", 320, 36)
        self._cb_asig.pack(side="left", padx=(0,8))
        self._cb_estado = _combo_widget(
            row1, ["(todos)","Aprobado","Reprobado"], "(todos)", 140, 36)
        self._cb_estado.pack(side="left", padx=(0,8))
        ctk.CTkButton(row1, text="Ver", height=36, width=70,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self.refresh).pack(side="left", padx=4)
        ctk.CTkButton(row1, text="Excel", height=36, width=80,
                      fg_color=SUCCESS, hover_color="#3fb950",
                      command=self._excel).pack(side="right", padx=4)
        self._lbl_info = ctk.CTkLabel(fcard,
            text="Selecciona una materia y presiona 'Ver'",
            font=FONT_SMALL, text_color=WARN)
        self._lbl_info.pack(anchor="w", padx=16, pady=(0,10))
        tf, self._tree = _scrolled_tree(self,
            ("cedula","nombre","carrera","ciclo","nota","estado"),
            ("Cedula","Estudiante","Carrera","Ciclo","Nota","Estado"),
            (110,200,130,60,80,100))
        _tree_style(self._tree, {"Aprobado":SUCCESS,"Reprobado":DANGER})
        tf.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0,8))
        bbar = ctk.CTkFrame(self, fg_color="transparent")
        bbar.grid(row=3, column=0, sticky="w", padx=32, pady=(0,20))
        ctk.CTkButton(bbar, text="Editar Nota del Seleccionado", width=220, height=36,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      command=self._editar_nota).pack(side="left", padx=4)

    def refresh(self):
        cedula_doc = self.ctrl.cedula_activa()
        mis_asigs  = [a for a in self.ctrl.data.asignaturas if a.docente==cedula_doc]
        opts = [f"{a.codigo} - {a.nombre}" for a in mis_asigs]
        if opts:
            self._cb_asig.configure(values=opts)
            if self._cb_asig.get() not in opts: self._cb_asig.set(opts[0])
        else:
            self._cb_asig.configure(values=["(sin materias asignadas)"])
            self._cb_asig.set("(sin materias asignadas)")
            self._lbl_info.configure(text="No tienes materias asignadas. Contacta al administrador.")
            return
        for row in self._tree.get_children(): self._tree.delete(row)
        asig_sel   = self._cb_asig.get()
        estado_sel = self._cb_estado.get()
        if " - " not in asig_sel:
            self._lbl_info.configure(text="Selecciona una materia valida."); return
        cod = asig_sel.split(" - ")[0]
        nombres_c = {c.codigo: c.nombre for c in self.ctrl.data.carreras}
        count = 0
        for m in self.ctrl.data.matriculas:
            if m.asignatura.codigo!=cod: continue
            estado = m.estado()
            if estado_sel not in ("(todos)","") and estado!=estado_sel: continue
            nc  = nombres_c.get(m.estudiante.carrera, m.estudiante.carrera)
            tag = "Aprobado" if estado=="Aprobado" else "Reprobado"
            self._tree.insert("","end", iid=m.estudiante.cedula, tags=(tag,),
                values=(m.estudiante.cedula,m.estudiante.nombre,
                        nc,m.estudiante.semestre,f"{m.nota:.2f}",estado))
            count += 1
        self._lbl_info.configure(text=f"{count} estudiante(s) en esta materia")

    def _editar_nota(self):
        sel = self._tree.selection()
        if not sel:
            Info(self,"Aviso",
                 "Selecciona un estudiante de la lista.\n\n"
                 "1. Presiona 'Ver' para cargar estudiantes.\n"
                 "2. Haz clic en un estudiante.\n"
                 "3. Presiona 'Editar Nota'."); return
        ced      = str(sel[0])
        vals     = self._tree.item(ced)["values"]
        nota_act = float(str(vals[4]))
        asig_sel = self._cb_asig.get()
        if " - " not in asig_sel:
            Info(self,"Error","Selecciona una materia valida."); return
        cod = asig_sel.split(" - ")[0]
        DialogEditarNota(self, self.ctrl, ced, cod, nota_act, on_save=self.refresh)

    def _excel(self):
        asig_sel = self._cb_asig.get()
        if " - " not in asig_sel:
            Info(self,"Aviso","Primero selecciona una materia y presiona 'Ver'."); return
        cod = asig_sel.split(" - ")[0]
        ruta = filedialog.asksaveasfilename(
            parent=self, defaultextension=".xlsx",
            filetypes=[("Excel","*.xlsx")], initialfile=f"lista_{cod}.xlsx")
        if ruta:
            ok, msg = self.ctrl.exportar_excel_curso(cod, ruta)
            Info(self,"Excel",msg)


# =========================================================
# DASHBOARD ESTUDIANTE
# =========================================================
class DashboardEstudiantePage(ctk.CTkFrame):
    def __init__(self, parent, ctrl, **_):
        super().__init__(parent, fg_color=BG, corner_radius=0)
        self.ctrl = ctrl; self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=32, pady=(24,4))
        ctk.CTkLabel(top, text="Kognos",
                     font=("Segoe UI",24,"bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(top, text="  Mi Portal Estudiantil",
                     font=("Segoe UI",13), text_color=TEXT_MUTED).pack(side="left", pady=(7,0))
        self._sf = ctk.CTkFrame(self, fg_color="transparent")
        self._sf.grid(row=1, column=0, sticky="ew", padx=32, pady=(0,12))
        for i in range(5): self._sf.grid_columnconfigure(i, weight=1)
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0,24))
        bottom.grid_columnconfigure(0, weight=2)
        bottom.grid_columnconfigure(1, weight=3)
        bottom.grid_rowconfigure(0, weight=1)
        nf = ctk.CTkFrame(bottom, fg_color=CARD_BG, corner_radius=12)
        nf.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        nf.grid_columnconfigure(0, weight=1)
        nf.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(nf, text="Mis Materias", font=FONT_H2, text_color=TEXT).grid(
            row=0, column=0, sticky="w", padx=20, pady=(14,6))
        self._notas_tree = ttk.Treeview(nf,
            columns=("codigo","nombre","creditos","docente","nota","estado"),
            show="headings")
        for col, w, lbl in [("codigo",70,"Codigo"),("nombre",180,"Materia"),
                             ("creditos",55,"Cred."),("docente",140,"Docente"),
                             ("nota",70,"Nota"),("estado",90,"Estado")]:
            self._notas_tree.heading(col, text=lbl)
            self._notas_tree.column(col, width=w,
                anchor="w" if col in ("nombre","docente") else "center")
        _tree_style(self._notas_tree, {"Aprobado":SUCCESS,"Reprobado":DANGER})
        self._notas_tree.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0,8))
        sb = ctk.CTkScrollbar(nf, command=self._notas_tree.yview)
        sb.grid(row=1, column=1, sticky="ns", pady=8)
        self._notas_tree.configure(yscrollcommand=sb.set)
        self._chart_frame = ctk.CTkFrame(bottom, fg_color=CARD_BG, corner_radius=12)
        self._chart_frame.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(self._chart_frame, text="Mis Notas",
                     font=FONT_H2, text_color=TEXT).pack(anchor="w", padx=20, pady=(14,4))
        self._chart_inner = ctk.CTkFrame(self._chart_frame, fg_color="transparent")
        self._chart_inner.pack(fill="both", expand=True, padx=8, pady=(0,8))

    def refresh(self):
        cedula = self.ctrl.cedula_activa()
        if not cedula: return
        for row in self._notas_tree.get_children(): self._notas_tree.delete(row)
        for w in self._sf.winfo_children(): w.destroy()
        mats      = [m for m in self.ctrl.data.matriculas if m.estudiante.cedula==cedula]
        dic_doc   = {d.cedula: d.nombres for d in self.ctrl.data.docentes}
        total_cred= sum(m.asignatura.creditos for m in mats)
        total_pond= sum(m.nota*m.asignatura.creditos for m in mats)
        prom_pond = total_pond/total_cred if total_cred else 0
        prom_s    = sum(m.nota for m in mats)/len(mats) if mats else 0
        ap        = sum(1 for m in mats if m.nota>=7.0)
        rep       = len(mats)-ap
        for i,(t,v,c) in enumerate([
            ("Materias",len(mats),ACCENT),("Aprobadas",ap,SUCCESS),
            ("Reprobadas",rep,DANGER),(f"Prom.Simple",f"{prom_s:.2f}",CYAN),
            ("Prom.Pond.",f"{prom_pond:.2f}",WARN),
        ]): _stat_card(self._sf,t,v,c).grid(row=0,column=i,padx=4,sticky="ew")
        for m in sorted(mats, key=lambda x: x.nota, reverse=True):
            estado = m.estado()
            tag    = "Aprobado" if estado=="Aprobado" else "Reprobado"
            doc_n  = dic_doc.get(m.asignatura.docente,"---")
            self._notas_tree.insert("","end", tags=(tag,),
                values=(m.asignatura.codigo,m.asignatura.nombre,
                        m.asignatura.creditos,doc_n,f"{m.nota:.2f}",estado))
        def make_fig():
            import matplotlib.pyplot as plt
            if not mats: return None
            nombres = [m.asignatura.nombre[:12] for m in mats]
            notas   = [m.nota for m in mats]
            colors_bar = [SUCCESS if n>=7 else (WARN if n>=5 else DANGER) for n in notas]
            fig, axes = plt.subplots(1, 2, figsize=(6,3.5), facecolor=CARD_BG)
            _mpl_style(fig, axes)
            axes[0].barh(nombres, notas, color=colors_bar, edgecolor=CARD_BG, linewidth=1.5)
            axes[0].axvline(7.0, color=WARN, linewidth=1.5, linestyle="--", alpha=0.8)
            axes[0].set_xlim(0,10)
            for i,(nom,nota) in enumerate(zip(nombres,notas)):
                axes[0].text(nota+0.1, i, f"{nota:.1f}", va="center", color=TEXT, fontsize=8)
            axes[0].set_title("Notas por Materia", color=TEXT, fontsize=9)
            slices = [ap,rep] if rep>0 else [ap]
            labels = ["Aprobadas","Reprobadas"][:1 if rep==0 else 2]
            colors = [SUCCESS,DANGER][:1 if rep==0 else 2]
            if any(s>0 for s in slices):
                axes[1].pie(slices, labels=labels, colors=colors, autopct="%1.1f%%",
                            startangle=90, textprops={"color":TEXT,"fontsize":9},
                            wedgeprops={"edgecolor":CARD_BG,"linewidth":2})
            axes[1].set_title("Estado", color=TEXT, fontsize=9)
            fig.tight_layout(pad=1.5)
            return fig
        _render_matplotlib(self._chart_inner, make_fig, "Aun no tienes notas registradas")
