# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
from pathlib import Path

a = Analysis(
    ['main_window.py'],
    pathex=[],
    binaries=[],
    datas=[('locales', 'locales'), ('filters', 'filters')],
    hiddenimports=[],
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PandocGUI',
)

# ビルド後にfiltersとlocalesを_internalの外に移動
dist_dir = Path('dist/PandocGUI')
internal_dir = dist_dir / '_internal'

for folder in ['filters', 'locales']:
    src = internal_dir / folder
    dst = dist_dir / folder
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.move(str(src), str(dst))
        print(f'Moved {folder} from _internal to root')
