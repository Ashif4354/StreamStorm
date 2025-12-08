"""Script to generate executable using PyInstaller."""

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from subprocess import call  # noqa: E402
from os import chdir  # noqa: E402
from shutil import move, rmtree  # noqa: E402
from platform import system  # noqa: E402
from logging import basicConfig, INFO, info as log_info  # noqa: E402
from json import load # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")

OS: str = system()

def check_engine_env():
    """Check if the Engine environment is set to production before building."""
    
    from src.Engine.StreamStorm.config.config import CONFIG  # noqa: E402
    
    log_info("Checking environment configuration...")
    
    if CONFIG["ENV"] in ("development", "test"):
        raise ValueError(
            "Environment is not set to 'production' in Engine/config/config.py. "
            "Change it to 'production' before building the release."
        )
        
    new_version: str = load(open(str(ROOT / "project.json")))["version"]
        
    if CONFIG["VERSION"] != new_version:
        raise ValueError(
            "Version in Engine/config/config.py is not the same as the new version. "
            "Change it to the new version before building the release."
        )
    
    log_info(f"Environment configuration check passed. ENV is set to '{CONFIG['ENV']}'.")


def generate_executable() -> None:
    """Generate executable using PyInstaller."""
    log_info("Generating executable...")
    
    chdir(ROOT / "src" / "Engine")
    
    log_info("Running 'uv sync' in Engine directory")
    
    call("uv sync", shell=True)
    
    build_dir: Path = ROOT / "build"    
    # chdir(build_dir)
    
    spec_file: Path = build_dir / "pyinstaller" / "StreamStorm.spec"
    
    check_engine_env()

    build_command: str = ([
        "uv", "run",
        "pyinstaller",
        str(spec_file),
        "--noconfirm",
        "--clean",
        "--distpath", str(build_dir / "dist")
    ])

    log_info(f"Running build command: {' '.join(build_command)}")
    call(build_command)

    dist_dir: Path = ROOT / "build" / "dist"
    
    if OS == "Windows":
        executable_path: Path = dist_dir / "StreamStorm.exe"
        output_dir: Path = ROOT / "export" / "windows"
        target_path: Path = output_dir / "StreamStorm.exe"
        
    elif OS == "Linux":
        executable_path: Path = dist_dir / "StreamStorm-linux"
        output_dir: Path = ROOT / "export" / "linux" / "opt" / "StreamStorm"
        target_path: Path = output_dir / "StreamStorm-linux"
        
    elif OS == "Darwin":
        executable_path: Path = dist_dir / "StreamStorm-mac"
        output_dir: Path = ROOT / "export" / "mac"
        target_path = output_dir / "StreamStorm-mac"
        
    else:
        raise OSError(f"Unsupported OS: {OS}")

    if executable_path.exists():
        log_info(f"Moving {executable_path} to {output_dir}")
        
        if target_path.exists():
            log_info(f"Removing existing {target_path}")
            
            target_path.unlink()
            
        move(str(executable_path), str(output_dir))
        
    else:
        log_info("Built executable not found!")
        raise FileNotFoundError("Built executable not found")
    
    inner_build_dir: Path = ROOT / "build" / "build"
    
    log_info(f"Cleaning up {dist_dir} and {inner_build_dir}")
    rmtree(dist_dir, ignore_errors=True)
    rmtree(inner_build_dir, ignore_errors=True)
    
    log_info("Executable generation completed successfully.")


def main() -> None:
    """Main entry point."""
    
    generate_executable()
    log_info("Generate executable process completed.")


if __name__ == "__main__":
    main()
