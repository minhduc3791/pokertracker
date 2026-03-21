# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

block_cipher = None

project_root = Path(SPECFILE).parent

a = Analysis(
    ['src/gui.py'],
    pathex=[str(project_root / 'src')],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        ('icon.png', '.'),
    ],
    hiddenimports=[
        'psutil',
        'watchdog',
        'src.config',
        'src.database',
        'src.natural8_parser',
        'src.stats_engine',
        'src.process_detector',
        'src.file_watcher',
        'src.parser_base',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PokerTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
