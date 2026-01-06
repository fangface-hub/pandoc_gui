# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('locales', 'locales'),
        ('filters', 'filters'),
        ('stylesheets', 'stylesheets'),
        ('help', 'help'),
        ('profiles', 'profiles'),
        ('mermaid', 'mermaid'),
        ('LICENSES', 'LICENSES')
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='PandocGUI',
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PandocGUI',
)

# ビルド後処理: filters/, locales/, stylesheets/, help/, profiles/, mermaid/ を _internal/ の外に移動
import shutil
import os
from pathlib import Path

dist_dir = Path('dist/PandocGUI')
internal_dir = dist_dir / '_internal'

for folder in ['filters', 'locales', 'stylesheets', 'help', 'profiles', 'mermaid', 'LICENSES']:
    src = internal_dir / folder
    dst = dist_dir / folder
    
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.move(str(src), str(dst))
        print(f'Moved {folder}/ to dist/PandocGUI/{folder}/')
