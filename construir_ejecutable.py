#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construir_ejecutable.py
========================
Genera el ejecutable de SisAcad v4.0 usando PyInstaller.

Uso:
    python construir_ejecutable.py              # carpeta dist/SisAcad/
    python construir_ejecutable.py --onefile    # un solo ejecutable
    python construir_ejecutable.py --limpiar    # solo limpia dist/ y build/

Requisitos previos:
    pip install pyinstaller customtkinter reportlab openpyxl matplotlib
"""

import sys
import os
import subprocess
import shutil
import argparse
import platform
from pathlib import Path

SO = platform.system()

_USE_COLOR = SO != "Windows" or "WT_SESSION" in os.environ
def _c(code, t): return f"\033[{code}m{t}\033[0m" if _USE_COLOR else t
OK   = lambda t: print(_c("32",   f"  ✔  {t}"))
WARN = lambda t: print(_c("33",   f"  ⚠  {t}"))
ERR  = lambda t: print(_c("31",   f"  ✘  {t}"))
INF  = lambda t: print(_c("36",   f"  →  {t}"))
HDR  = lambda t: print(_c("1;34", f"\n{'═'*55}\n  {t}\n{'═'*55}"))


# ─────────────────────────────────────────────────────────
ROOT = Path(__file__).parent          # raíz del proyecto
DIST = ROOT / "dist" / "SisAcad"
# ─────────────────────────────────────────────────────────


def verificar_pyinstaller():
    HDR("Verificando PyInstaller")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "show", "pyinstaller"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        INF("Instalando PyInstaller …")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller", "-q"],
            check=True
        )
        OK("PyInstaller instalado")
    else:
        version = [l for l in r.stdout.splitlines() if l.startswith("Version")]
        OK(f"PyInstaller ya disponible — {version[0] if version else ''}")


def limpiar():
    HDR("Limpiando artefactos anteriores")
    for d in [ROOT / "build", ROOT / "dist", ROOT / "__pycache__"]:
        if d.exists():
            shutil.rmtree(d)
            OK(f"Eliminado: {d}")
    spec_cache = ROOT / "SisAcad.spec"
    if spec_cache.exists() and spec_cache != ROOT / "sisacad.spec":
        spec_cache.unlink()
    OK("Limpieza completada")


def copiar_spec_si_no_existe():
    """Copia sisacad.spec a la raíz del proyecto si no está ya ahí."""
    destino = ROOT / "sisacad.spec"
    origen  = Path(__file__).parent / "sisacad.spec"
    if not destino.exists() and origen.exists() and origen != destino:
        shutil.copy(origen, destino)
        INF(f"sisacad.spec copiado a {destino}")


def construir(onefile: bool = False):
    HDR("Construyendo ejecutable")

    # Asegura que la carpeta assets/ exista (icono opcional)
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)

    # ── Recopila imports ocultos ──
    hidden = [
        "customtkinter",
        "PIL._tkinter_finder",
        "reportlab.graphics.barcode",
        "reportlab.graphics.barcode.code128",
        "matplotlib.backends.backend_tkagg",
        "openpyxl",
        "openpyxl.cell._writer",
        "sqlite3",
        "model.data_manager",
        "controller.controller",
        "view.login_window",
        "view.main_window",
        "view.pages",
        "view.dialogs",
        "utils.constants",
        "utils.styles",
        "utils.validators",
        "app_launcher",
    ]

    # ── Datos adicionales ──
    add_data_sep = ";" if SO == "Windows" else ":"
    add_datas = []
    for carpeta in ["data", "utils", "assets"]:
        p = ROOT / carpeta
        if p.exists():
            add_datas += ["--add-data", f"{p}{add_data_sep}{carpeta}"]

    # ── Añade datos de customtkinter ──
    try:
        import customtkinter
        ctk_path = Path(customtkinter.__file__).parent
        add_datas += ["--add-data", f"{ctk_path}{add_data_sep}customtkinter"]
        OK(f"customtkinter path: {ctk_path}")
    except ImportError:
        WARN("customtkinter no encontrado — instálalo antes de construir")

    # ── Icono ──
    icono_args = []
    icono = ROOT / "assets" / "icon.ico"
    if SO != "Darwin" and icono.exists():
        icono_args = ["--icon", str(icono)]
    elif SO == "Darwin":
        icono_icns = ROOT / "assets" / "icon.icns"
        if icono_icns.exists():
            icono_args = ["--icon", str(icono_icns)]

    # ── Comando PyInstaller ──
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "SisAcad",
        "--windowed",                # sin ventana de consola
        "--noconfirm",               # sobreescribe sin preguntar
        "--clean",
        "--distpath", str(ROOT / "dist"),
        "--workpath", str(ROOT / "build"),
        "--specpath", str(ROOT),
    ]

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    for h in hidden:
        cmd += ["--hidden-import", h]

    cmd += add_datas
    cmd += icono_args
    cmd.append(str(ROOT / "main.py"))

    INF("Ejecutando PyInstaller …")
    INF(f"Directorio de trabajo: {ROOT}")
    print()

    result = subprocess.run(cmd, cwd=str(ROOT))

    if result.returncode == 0:
        OK("Build completado con éxito")
    else:
        ERR("PyInstaller falló — revisa los mensajes anteriores")
        sys.exit(1)


def post_build(onefile: bool):
    HDR("Post-build")

    if onefile:
        exe_nombre = "SisAcad.exe" if SO == "Windows" else "SisAcad"
        exe_path = ROOT / "dist" / exe_nombre
    else:
        exe_nombre = "SisAcad.exe" if SO == "Windows" else "SisAcad"
        exe_path = ROOT / "dist" / "SisAcad" / exe_nombre

    if exe_path.exists():
        size = exe_path.stat().st_size / (1024 * 1024)
        OK(f"Ejecutable generado: {exe_path}")
        OK(f"Tamaño: {size:.1f} MB")
    else:
        WARN("No se encontró el ejecutable en la ruta esperada")
        WARN("Busca en la carpeta dist/")

    # Copia la carpeta data/ al dist si no está ya
    if not onefile:
        data_src = ROOT / "data"
        data_dst = ROOT / "dist" / "SisAcad" / "data"
        if data_src.exists() and not data_dst.exists():
            shutil.copytree(data_src, data_dst)
            OK(f"Carpeta data/ copiada a {data_dst}")

    print(_c("1;32", f"""
  ╔══════════════════════════════════════════════════╗
  ║  Build de SisAcad v4.0 finalizado                ║
  ╠══════════════════════════════════════════════════╣
  ║  Ubicación: dist/{'SisAcad/' if not onefile else ''}SisAcad{'.exe' if SO == 'Windows' else ''}
  ║  Para distribuir: comprime la carpeta dist/      ║
  ╚══════════════════════════════════════════════════╝
"""))


def main():
    parser = argparse.ArgumentParser(
        description="Construye el ejecutable de SisAcad con PyInstaller"
    )
    parser.add_argument("--onefile",  action="store_true",
                        help="Genera un solo archivo ejecutable (más lento al iniciar)")
    parser.add_argument("--limpiar",  action="store_true",
                        help="Solo limpia dist/ y build/ sin construir")
    args = parser.parse_args()

    print(_c("1;34", """
╔══════════════════════════════════════════════╗
║      Constructor de SisAcad v4.0             ║
║  TecAzuay — Generador de ejecutable          ║
╚══════════════════════════════════════════════╝"""))

    if args.limpiar:
        limpiar()
        return

    verificar_pyinstaller()
    limpiar()
    copiar_spec_si_no_existe()
    construir(onefile=args.onefile)
    post_build(onefile=args.onefile)


if __name__ == "__main__":
    main()