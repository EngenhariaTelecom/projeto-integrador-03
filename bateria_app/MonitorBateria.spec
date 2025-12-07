# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import sys
import os

# Importações ocultas necessárias
hiddenimports = [
    "PIL.ImageTk",
    "PIL._imagingtk",
    "PIL._tkinter_finder",
]

# Dados incluídos
datas = [
    ('assets', 'assets'),
    ('baterias', 'baterias'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MonitorBateria',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MonitorBateria',
)