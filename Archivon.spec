# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

datas = [
    ('archivon_py', 'archivon_py'),
    ('assets', 'assets')
]
binaries = []
hiddenimports = [
    'PyQt6.QtSvg',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'google.generativeai',
    'google.ai.generativelanguage',
    'google.api_core',
    'google.protobuf',
    'grpc',
    'pymupdf',
    'fitz',
    'gdown',
    'requests',
    'dotenv'
]

# Coleta dinâmica completa para evitar crashes no executável standalone
for pkg in ['google.generativeai', 'google.ai.generativelanguage', 'google.api_core', 'pymupdf', 'fitz', 'gdown']:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
    except Exception:
        pass

a = Analysis(
    ['archivon_py/main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

icon_path = None
if sys.platform == 'darwin' and os.path.exists('assets/icon.icns'):
    icon_path = ['assets/icon.icns']
elif (sys.platform.startswith('win') or os.name == 'nt') and os.path.exists('assets/icon.ico'):
    icon_path = ['assets/icon.ico']

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Archivon',
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
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Archivon',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Archivon.app',
        icon='assets/icon.icns' if os.path.exists('assets/icon.icns') else None,
        bundle_identifier='com.archivon.app',
    )
