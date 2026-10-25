# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from platform import system
from os import getcwd
import os
from PyInstaller.utils.hooks import copy_metadata, collect_all, collect_data_files, collect_submodules
import tempfile
import importlib.metadata
import fakeredis

ROOT = Path(getcwd()).parent.parent.resolve()
ENGINE = ROOT / "src" / "Engine"
UI = ROOT / "src" / "UI"

datas = []
binaries = []
hiddenimports = []

lupa_datas, lupa_binaries, lupa_hiddenimports = collect_all('lupa')

fr_datas, fr_binaries, fr_hidden = collect_all('fakeredis')

fr_path = os.path.dirname(fakeredis.__file__)
json_path = os.path.join(fr_path, 'commands.json')

if os.path.exists(json_path):
    print(f"Manually forcing inclusion of: {json_path}")
    fr_datas.append((json_path, 'fakeredis'))
else:
    print(f"Warning: Could not find commands.json at {json_path}")

# Sentry: bundle ONLY the DSN (never the whole Engine/.env, which may hold other secrets).
# The DSN comes from the STREAMSTORM_SENTRY_DSN env var (e.g. a GitHub Actions secret) or
# from the git-ignored src/Engine/.env. It is read at runtime by Settings.py from sys._MEIPASS/.env.
def _find_sentry_dsn():
    dsn = os.environ.get("STREAMSTORM_SENTRY_DSN", "").strip()
    if dsn:
        return dsn

    env_file = ENGINE / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == "STREAMSTORM_SENTRY_DSN":
                return value.strip().strip('"').strip("'")

    return ""

sentry_dsn = _find_sentry_dsn()
sentry_datas = []

if sentry_dsn:
    sentry_env_dir = Path(tempfile.mkdtemp(prefix="streamstorm_sentry_"))
    sentry_env_file = sentry_env_dir / ".env"
    sentry_env_file.write_text(f"STREAMSTORM_SENTRY_DSN={sentry_dsn}\n", encoding="utf-8")
    sentry_datas.append((str(sentry_env_file), "."))
    print("Bundled Sentry DSN into the executable")
else:
    print("Warning: STREAMSTORM_SENTRY_DSN not found - this build will have Sentry disabled")

# Sentry auto-enabling integrations are imported dynamically, so PyInstaller cannot detect them
sentry_hidden = collect_submodules("sentry_sdk")

# Combine everything
datas = datas + lupa_datas + fr_datas + sentry_datas
binaries = binaries + lupa_binaries + fr_binaries
hiddenimports = hiddenimports + lupa_hiddenimports + fr_hidden + sentry_hidden

for dist in importlib.metadata.distributions():
    package_name = dist.metadata['Name']
    try:
        if package_name not in ['pip', 'setuptools', 'wheel']: 
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=[str(UI / "public" / "favicon.ico")],
    contents_directory="data",
)