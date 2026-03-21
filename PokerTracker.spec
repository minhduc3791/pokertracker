# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

block_cipher = None

script_dir = Path(os.path.dirname(os.path.abspath(SPECFILE)))
project_root = script_dir.parent

a = Analysis(
    [str(project_root / 'src' / 'gui.py')],
    pathex=[str(project_root / 'src')],
    binaries=[],
    datas=[
        (str(project_root / 'icon.ico'), '.'),
        (str(project_root / 'icon.png'), '.'),
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
    icon=str(project_root / 'icon.ico'),
)
