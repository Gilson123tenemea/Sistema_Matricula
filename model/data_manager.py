# -*- coding: utf-8 -*-
"""
model/data_manager.py — Persistencia SQLite.
Horarios: tabla con bloques serializados como string.
"""
import sqlite3
import os

from utils.constants import ARCHIVO_DATOS, NOTA_MINIMA_APROBACION
from model.estudiante import Estudiante
from model.docente    import Docente
from model.carrera    import Carrera
from model.asignatura import Asignatura
from model.matricula  import Matricula
from model.usuario    import Usuario
from model.horario    import Horario, BloqueHorario


class DataManager:
    def __init__(self):
        self.estudiantes: list = []
        self.docentes:    list = []
        self.carreras:    list = []
        self.asignaturas: list = []
        self.matriculas:  list = []
        self.usuarios:    list = []
        self.horarios:    list = []   # list[Horario]

        os.makedirs("data", exist_ok=True)
        self._con = sqlite3.connect(ARCHIVO_DATOS)
        self._con.row_factory = sqlite3.Row
        self._con.execute("PRAGMA foreign_keys = ON")
        self._crear_tablas()

    # ── DDL ───────────────────────────────────────
    def _crear_tablas(self):
        with self._con:
            self._con.executescript("""
                CREATE TABLE IF NOT EXISTS carreras (
                    codigo      TEXT PRIMARY KEY,
                    nombre      TEXT NOT NULL,
                    num_ciclos  INTEGER NOT NULL DEFAULT 8,
                    descripcion TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS docentes (
                    cedula       TEXT PRIMARY KEY,
                    nombres      TEXT NOT NULL,
                    titulo       TEXT NOT NULL,
                    email        TEXT NOT NULL,
                    especialidad TEXT NOT NULL,
                    telefono     TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS estudiantes (
                    cedula   TEXT PRIMARY KEY,
                    nombre   TEXT NOT NULL,
                    edad     INTEGER NOT NULL,
                    carrera  TEXT NOT NULL,
                    email    TEXT NOT NULL,
                    semestre INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS horarios (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    bloques TEXT NOT NULL DEFAULT '',
                    aula    TEXT NOT NULL DEFAULT 'Por asignar'
                );
                CREATE TABLE IF NOT EXISTS asignaturas (
                    codigo           TEXT PRIMARY KEY,
                    nombre           TEXT NOT NULL,
                    docente          TEXT NOT NULL DEFAULT '',
                    creditos         INTEGER NOT NULL,
                    cupo_maximo      INTEGER NOT NULL DEFAULT 30,
                    semestre         INTEGER NOT NULL DEFAULT 1,
                    prerequisito     TEXT,
                    carrera          TEXT NOT NULL DEFAULT '',
                    horario_id       INTEGER,
                    horas_semanales  INTEGER NOT NULL DEFAULT 4
                );
                CREATE TABLE IF NOT EXISTS matriculas (
                    cedula  TEXT NOT NULL,
                    codigo  TEXT NOT NULL,
                    nota    REAL NOT NULL DEFAULT 0,
                    periodo TEXT NOT NULL DEFAULT '2026-A',
                    PRIMARY KEY (cedula, codigo)
                );
                CREATE TABLE IF NOT EXISTS usuarios (
                    username         TEXT PRIMARY KEY,
                    password_hash    TEXT NOT NULL,
                    rol              TEXT NOT NULL,
                    cedula_vinculada TEXT
                );
                CREATE TABLE IF NOT EXISTS historial (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    cedula      TEXT NOT NULL,
                    codigo      TEXT NOT NULL,
                    nombre_asig TEXT NOT NULL,
                    nota        REAL NOT NULL,
                    periodo     TEXT NOT NULL,
                    creditos    INTEGER NOT NULL DEFAULT 3,
                    UNIQUE(cedula, codigo, periodo)
                );
            """)
        self._migrar_tablas()
        self._insertar_admin_default()

    def _migrar_tablas(self):
        def add_col(table, col, definition):
            cur = self._con.execute(f"PRAGMA table_info({table})")
            cols = [r["name"] for r in cur.fetchall()]
            if col not in cols:
                with self._con:
                    self._con.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")

        add_col("asignaturas", "carrera", "TEXT NOT NULL DEFAULT ''")
        add_col("asignaturas", "horario_id", "INTEGER")
        add_col("asignaturas", "horas_semanales", "INTEGER NOT NULL DEFAULT 4")

        # ── Migrar tabla horarios al nuevo esquema (bloques en lugar de dia/hora_inicio/hora_fin)
        cur = self._con.execute("PRAGMA table_info(horarios)")
        hcols = [r["name"] for r in cur.fetchall()]

        if "dia" in hcols:
            # Tabla vieja: tiene columnas dia, hora_inicio, hora_fin con NOT NULL
            # Leer datos existentes antes de recrear
            try:
                old_rows = self._con.execute(
                    "SELECT id, dia, hora_inicio, hora_fin FROM horarios").fetchall()
            except Exception:
                old_rows = []
            # Recrear tabla con el nuevo esquema
            with self._con:
                self._con.executescript("""
                    DROP TABLE IF EXISTS horarios_old;
                    ALTER TABLE horarios RENAME TO horarios_old;
                    CREATE TABLE horarios (
                        id      INTEGER PRIMARY KEY AUTOINCREMENT,
                        bloques TEXT NOT NULL DEFAULT '',
                        aula    TEXT NOT NULL DEFAULT 'Por asignar'
                    );
                """)
                # Migrar datos viejos: cada fila vieja → un horario con un bloque
                for r in old_rows:
                    bloque_str = f"{r['dia']}|{r['hora_inicio']}|{r['hora_fin']}"
                    self._con.execute(
                        "INSERT INTO horarios(id, bloques, aula) VALUES (?,?,?)",
                        (r['id'], bloque_str, 'Por asignar'))
                self._con.execute("DROP TABLE IF EXISTS horarios_old")

        # ── Migrar cedula_estudiante → cedula_vinculada
        cur = self._con.execute("PRAGMA table_info(usuarios)")
        ucols = [r["name"] for r in cur.fetchall()]
        if "cedula_vinculada" not in ucols:
            with self._con:
                self._con.execute("ALTER TABLE usuarios ADD COLUMN cedula_vinculada TEXT")
                if "cedula_estudiante" in ucols:
                    self._con.execute(
                        "UPDATE usuarios SET cedula_vinculada=cedula_estudiante "
                        "WHERE cedula_vinculada IS NULL")

    def _insertar_admin_default(self):
        cur = self._con.execute("SELECT 1 FROM usuarios WHERE username='admin'")
        if not cur.fetchone():
            ph = Usuario.hash_password("admin123")
            # Detect which column name exists (old: cedula_estudiante, new: cedula_vinculada)
            col_info = self._con.execute("PRAGMA table_info(usuarios)").fetchall()
            col_names = [r[1] for r in col_info]
            if "cedula_vinculada" in col_names:
                sql = "INSERT INTO usuarios(username,password_hash,rol,cedula_vinculada) VALUES (?,?,?,?)"
            else:
                sql = "INSERT INTO usuarios(username,password_hash,rol) VALUES (?,?,?)"
                with self._con:
                    self._con.execute(sql, ("admin", ph, "admin"))
                return
            with self._con:
                self._con.execute(sql, ("admin", ph, "admin", None))

    # ── CARGA ─────────────────────────────────────
    def cargar(self):
        cur = self._con.cursor()
        for row in cur.execute("SELECT * FROM carreras"):
            self.carreras.append(Carrera(row["codigo"], row["nombre"],
                                         row["num_ciclos"], row["descripcion"]))
        for row in cur.execute("SELECT * FROM docentes"):
            self.docentes.append(Docente(row["cedula"], row["nombres"], row["titulo"],
                                          row["email"], row["especialidad"], row["telefono"]))
        dic_est = {}
        for row in cur.execute("SELECT * FROM estudiantes"):
            e = Estudiante(row["cedula"], row["nombre"], row["edad"],
                           row["carrera"], row["email"], row["semestre"])
            self.estudiantes.append(e); dic_est[e.cedula] = e

        # Horarios nuevos (bloques serializados)
        self._horarios_dict = {}
        for row in cur.execute("SELECT * FROM horarios"):
            keys = row.keys()
            if "bloques" in keys:
                bloques = Horario.bloques_from_str(row["bloques"])
            else:
                bloques = []
            aula = row["aula"] if "aula" in keys else "Por asignar"
            h = Horario(row["id"], bloques, aula)
            self.horarios.append(h)
            self._horarios_dict[h.id] = h

        dic_asig = {}
        for row in cur.execute("SELECT * FROM asignaturas"):
            keys = row.keys()
            carrera = row["carrera"] if "carrera" in keys else ""
            hid     = row["horario_id"] if "horario_id" in keys else None
            hs      = row["horas_semanales"] if "horas_semanales" in keys else row["creditos"]
            a = Asignatura(row["codigo"], row["nombre"], row["docente"],
                           row["creditos"], row["cupo_maximo"],
                           row["semestre"], row["prerequisito"],
                           carrera, hid, hs)
            self.asignaturas.append(a); dic_asig[a.codigo] = a

        for row in cur.execute("SELECT * FROM matriculas"):
            e = dic_est.get(row["cedula"]); a = dic_asig.get(row["codigo"])
            if e and a:
                self.matriculas.append(Matricula(e, a, row["nota"], row["periodo"]))

        for row in cur.execute("SELECT * FROM usuarios"):
            keys = row.keys()
            cv = row["cedula_vinculada"] if "cedula_vinculada" in keys else None
            if not cv and "cedula_estudiante" in keys:
                cv = row["cedula_estudiante"]
            self.usuarios.append(Usuario(row["username"], row["password_hash"], row["rol"], cv))

    # ── GUARDADO ──────────────────────────────────
    def guardar(self):
        with self._con:
            self._con.execute("PRAGMA foreign_keys = OFF")

            self._con.execute("DELETE FROM carreras")
            self._con.executemany("INSERT INTO carreras VALUES (?,?,?,?)",
                [(c.codigo, c.nombre, c.num_ciclos, c.descripcion) for c in self.carreras])

            self._con.execute("DELETE FROM docentes")
            self._con.executemany("INSERT INTO docentes VALUES (?,?,?,?,?,?)",
                [(d.cedula, d.nombres, d.titulo, d.email, d.especialidad, d.telefono)
                 for d in self.docentes])

            self._con.execute("DELETE FROM estudiantes")
            self._con.executemany("INSERT INTO estudiantes VALUES (?,?,?,?,?,?)",
                [(e.cedula, e.nombre, e.edad, e.carrera, e.email, e.semestre)
                 for e in self.estudiantes])

            self._con.execute("DELETE FROM horarios")
            for h in self.horarios:
                if h.id:
                    self._con.execute(
                        "INSERT INTO horarios(id,bloques,aula) VALUES (?,?,?)",
                        (h.id, h.bloques_str(), h.aula))
                else:
                    self._con.execute(
                        "INSERT INTO horarios(bloques,aula) VALUES (?,?)",
                        (h.bloques_str(), h.aula))

            self._con.execute("DELETE FROM asignaturas")
            self._con.executemany(
                "INSERT INTO asignaturas VALUES (?,?,?,?,?,?,?,?,?,?)",
                [(a.codigo, a.nombre, a.docente, a.creditos, a.cupo_maximo,
                  a.semestre, a.prerequisito, a.carrera, a.horario_id,
                  a.horas_semanales) for a in self.asignaturas])

            self._con.execute("DELETE FROM matriculas")
            self._con.executemany("INSERT INTO matriculas VALUES (?,?,?,?)",
                [(m.estudiante.cedula, m.asignatura.codigo, m.nota, m.periodo)
                 for m in self.matriculas])

            self._con.execute("DELETE FROM usuarios")
            self._con.executemany(
                "INSERT INTO usuarios(username,password_hash,rol,cedula_vinculada) VALUES (?,?,?,?)",
                [(u.username, u.password_hash, u.rol, u.cedula_vinculada)
                 for u in self.usuarios])

            self._con.execute("PRAGMA foreign_keys = ON")

    def horario_by_id(self, hid: int):
        return next((h for h in self.horarios if h.id == hid), None)

    def insertar_horario(self, bloques_str: str, aula: str) -> int:
        with self._con:
            cur = self._con.execute(
                "INSERT INTO horarios(bloques,aula) VALUES (?,?)", (bloques_str, aula))
        return cur.lastrowid

    # ── QUERIES SQL ───────────────────────────────
    def query_matriculas_join(self, filtro_carrera="", filtro_semestre="",
                              filtro_estado="", filtro_docente="", filtro_materia=""):
        sql = """
            SELECT e.cedula, e.nombre, e.carrera, e.semestre,
                   a.codigo, a.nombre AS asig_nombre, a.creditos,
                   a.docente AS docente_cedula, m.nota, m.periodo,
                   CASE WHEN m.nota >= ? THEN 'Aprobado' ELSE 'Reprobado' END AS estado
            FROM matriculas m
            JOIN estudiantes e ON m.cedula = e.cedula
            JOIN asignaturas a ON m.codigo = a.codigo
            WHERE 1=1
        """
        params = [NOTA_MINIMA_APROBACION]
        if filtro_carrera:
            sql += " AND e.carrera = ?"; params.append(filtro_carrera)
        if filtro_semestre:
            sql += " AND a.semestre = ?"; params.append(int(filtro_semestre))
        if filtro_estado == "Aprobado":
            sql += f" AND m.nota >= {NOTA_MINIMA_APROBACION}"
        elif filtro_estado == "Reprobado":
            sql += f" AND m.nota < {NOTA_MINIMA_APROBACION}"
        if filtro_docente:
            sql += " AND a.docente = ?"; params.append(filtro_docente)
        if filtro_materia:
            sql += " AND a.codigo = ?"; params.append(filtro_materia)
        return self._con.execute(sql, params).fetchall()

    def query_historial(self, cedula: str):
        return self._con.execute(
            "SELECT * FROM historial WHERE cedula=? ORDER BY periodo", (cedula,)).fetchall()

    def guardar_historial_row(self, cedula, codigo, nombre_asig, nota, periodo, creditos):
        with self._con:
            self._con.execute(
                "INSERT OR REPLACE INTO historial(cedula,codigo,nombre_asig,nota,periodo,creditos)"
                " VALUES (?,?,?,?,?,?)",
                (cedula, codigo, nombre_asig, nota, periodo, creditos))

    def query_cupos_usados(self, codigo_asig: str) -> int:
        row = self._con.execute(
            "SELECT COUNT(*) AS cnt FROM matriculas WHERE codigo=?", (codigo_asig,)).fetchone()
        return row["cnt"] if row else 0

    def estadisticas_sql(self):
        return self._con.execute("""
            SELECT COUNT(DISTINCT m.cedula) AS estudiantes_con_notas,
                   COUNT(*) AS total_matriculas,
                   ROUND(AVG(m.nota),2) AS promedio,
                   MAX(m.nota) AS max_nota, MIN(m.nota) AS min_nota,
                   SUM(CASE WHEN m.nota >= ? THEN 1 ELSE 0 END) AS aprobados,
                   SUM(CASE WHEN m.nota < ? THEN 1 ELSE 0 END) AS reprobados
            FROM matriculas m
        """, (NOTA_MINIMA_APROBACION, NOTA_MINIMA_APROBACION)).fetchone()

    def stats_por_carrera(self):
        return self._con.execute("""
            SELECT e.carrera, COUNT(DISTINCT e.cedula) AS total_est,
                   COUNT(m.cedula) AS total_mat, ROUND(AVG(m.nota),2) AS promedio,
                   SUM(CASE WHEN m.nota >= ? THEN 1 ELSE 0 END) AS aprobados,
                   SUM(CASE WHEN m.nota < ? THEN 1 ELSE 0 END) AS reprobados
            FROM estudiantes e LEFT JOIN matriculas m ON e.cedula=m.cedula
            GROUP BY e.carrera
        """, (NOTA_MINIMA_APROBACION, NOTA_MINIMA_APROBACION)).fetchall()

    def stats_docente(self, cedula_docente: str):
        return self._con.execute("""
            SELECT a.codigo, a.nombre AS asig_nombre, a.semestre, a.carrera,
                   COUNT(m.cedula) AS total,
                   SUM(CASE WHEN m.nota >= ? THEN 1 ELSE 0 END) AS aprobados,
                   SUM(CASE WHEN m.nota < ? THEN 1 ELSE 0 END) AS reprobados,
                   ROUND(AVG(m.nota),2) AS promedio
            FROM asignaturas a LEFT JOIN matriculas m ON a.codigo=m.codigo
            WHERE a.docente=?
            GROUP BY a.codigo
        """, (NOTA_MINIMA_APROBACION, NOTA_MINIMA_APROBACION, cedula_docente)).fetchall()
