# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from platform import system
from os import getcwd
from PyInstaller.utils.hooks import copy_metadata, collect_all, collect_data_files
import importlib.metadata

ROOT = Path(getcwd()).parent.parent.resolve()
ENGINE = ROOT / "src" / "Engine"
UI = ROOT / "src" / "UI"

datas = []
binaries = []
hiddenimports = []

lupa_datas, lupa_binaries, lupa_hiddenimports = collect_all('lupa')
fakeredis_datas = collect_data_files('fakeredis')

datas = lupa_datas + fakeredis_datas
binaries += lupa_binaries
hiddenimports += lupa_hiddenimports

for dist in importlib.metadata.distributions():
    package_name = dist.metadata['Name']
    try:
        datas += copy_metadata(package_name)
    except Exception as e:
        print(f"Skipping metadata for {package_name}: {e}")

match system():
    case "Windows":
        file_name = "StreamStorm"
        print("🪟 Building for Windows")
    case "Darwin":
        file_name = "StreamStorm-mac"
        print("🍎 Building for macOS")
    case "Linux":
        file_name = "StreamStorm-linux"
        print("🐧 Building for Linux")
    case _:
        raise OSError(f"Unsupported OS: {system()}")

a = Analysis(
    [str(ENGINE / "main.py")],
    pathex=[str(ROOT)],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=file_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,                 # = --windowed
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,                # = --uac-admin
    icon=[str(UI / "public" / "favicon.ico")],   # = --icon
    contents_directory="data",     # = --contents-directory=data
)