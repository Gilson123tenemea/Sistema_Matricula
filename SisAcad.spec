# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Usuario\\Desktop\\IA\\Sistema_Matricula-main\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Usuario\\Desktop\\IA\\Sistema_Matricula-main\\data', 'data'), ('C:\\Users\\Usuario\\Desktop\\IA\\Sistema_Matricula-main\\utils', 'utils'), ('C:\\Users\\Usuario\\Desktop\\IA\\Sistema_Matricula-main\\assets', 'assets'), ('C:\\Users\\Usuario\\Desktop\\IA\\Sistema_Matricula-main\\venv\\lib\\site-packages\\customtkinter', 'customtkinter')],
    hiddenimports=['customtkinter', 'PIL._tkinter_finder', 'reportlab.graphics.barcode', 'reportlab.graphics.barcode.code128', 'matplotlib.backends.backend_tkagg', 'openpyxl', 'openpyxl.cell._writer', 'sqlite3', 'model.data_manager', 'controller.controller', 'view.login_window', 'view.main_window', 'view.pages', 'view.dialogs', 'utils.constants', 'utils.styles', 'utils.validators', 'app_launcher'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SisAcad',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SisAcad',
)
