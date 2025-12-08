from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from subprocess import call, run  # noqa: E402
from os import chdir  # noqa: E402
from shutil import move, rmtree, which  # noqa: E402
from tomlkit import TOMLDocument, parse, dumps  # noqa: E402
from json import dump, load  # noqa: E402
from re import sub  # noqa: E402
from platform import system  # noqa: E402
from logging import basicConfig, INFO, info as log_info  # noqa: E402
from src.Engine.StreamStorm.config.config import CONFIG  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")

OS: str = system()

def check_engine_env(version: str):
    """Check if the Engine environment is set to production before building."""
    
    log_info("Checking environment configuration...")
    
    if CONFIG["ENV"] in ("development", "test"):
        raise ValueError(
            "Environment is not set to 'production' in Engine/config/config.py. "
            "Change it to 'production' before building the release."
        )
        
    if CONFIG["VERSION"] != version:
        raise ValueError(
            "Version in Engine/config/config.py is not the same as the new version. "
            "Change it to the new version before building the release."
        )
    
    log_info(f"Environment configuration check passed. ENV is set to '{CONFIG['ENV']}'.")
    

def update_versions(new_version: str) -> None:
    
    new_version_split: list[int] = [int(i) for i in new_version.split(".")]
    
    # project.json
    with open(ROOT / "project.json", "r") as f:
        project_data: dict = load(f)
        current_version: list[int] = [int(i) for i in project_data["version"].split(".")]

        if new_version_split <= current_version:
            raise ValueError("New version must be greater than current version.")

        project_data["version"] = new_version
        
        with open(ROOT / "project.json", "w") as f:
            dump(project_data, f, indent=4)


    log_info(f"Updating versions to {new_version}")
    
    # Engine/pyproject.toml
    pyproject_toml_path: Path = ROOT / "src" / "Engine" / "pyproject.toml"
    log_info(f"Updating {pyproject_toml_path}")
    
    with open(pyproject_toml_path, "r") as f:
        pyproject_data: TOMLDocument = parse(f.read())
        
    pyproject_data["project"]["version"] = new_version
        
    with open(pyproject_toml_path, "w") as f:
        f.write(dumps(pyproject_data))
        
    
    # UI/package.json and SITE/package.json
    def update_package_json(file_path: Path, new_version: str) -> None:
        log_info(f"Updating {file_path}")
        with open(file_path, "r") as f:
            data: dict = load(f)
        data["version"] = new_version
        with open(file_path, "w") as f:
            dump(data, f, indent=4)

    update_package_json(ROOT / "src" / "UI" / "package.json", new_version)
    update_package_json(ROOT / "src" / "Site" / "package.json", new_version)


    # INNO Setup / create_setup.iss
    create_setup_iss: Path = ROOT / "build" /"INNO Setup" / "create_setup.iss"
    
    log_info(f"Updating {create_setup_iss}")
    
    text: str = create_setup_iss.read_text(encoding="utf-8")
    text = sub(r'#define MyAppVersion\s+".*"', f'#define MyAppVersion "{new_version}"', text)
    create_setup_iss.write_text(text, encoding="utf-8")
    
    # Linux build version
    control_file: Path = ROOT / "export" / "linux" / "DEBIAN" / "control"
    log_info(f"Updating {control_file}")
    
    text: str = control_file.read_text(encoding="utf-8")
    
    text = sub(r'^Version:\s*.*$', f'Version: {new_version}', text, flags=__import__("re").MULTILINE)

    control_file.write_text(text, encoding="utf-8")

def generate_executable() -> None:
    log_info("Generating executable...")
    
    chdir(ROOT / "src" / "Engine")
    
    log_info("Running 'uv sync' in Engine directory")
    
    call("uv sync", shell=True)
    
    build_dir: Path = ROOT / "build"    
    chdir(build_dir)
    
    spec_file: Path = build_dir / "pyinstaller" / "StreamStorm.spec"

    build_command: str = ([
        "pyinstaller",
        str(spec_file),
        "--noconfirm",
        "--clean"
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
    
       
def generate_setup_file_windows() -> None: 
    log_info("Generating setup file using Inno Setup...")
    
    if not which("ISCC"):
        log_info("Inno Setup Compiler (ISCC) not found!")
        
        raise EnvironmentError("Inno Setup Compiler (ISCC) not found. Install or add it to PATH.")

    chdir(ROOT / "build" / "INNO Setup")
    
    log_info("Running 'ISCC create_setup.iss'")
    call("ISCC create_setup.iss", shell=True)
    

def firebase_deploy() -> None:
    log_info("Deploying to Firebase...")
    call(str(ROOT / "src" / "functions" / "venv" / "Scripts" / "activate.bat"), shell=True)
    chdir(ROOT / "src")
    
    log_info("Running 'firebase deploy'")
    call("firebase deploy", shell=True)
    

def dgupdater_commit_and_publish(new_version: str) -> None:
    log_info(f"Committing and publishing with dgupdater for version {new_version}")
    
    chdir(ROOT / "export" / "windows")
    
    log_info(f"Running 'dgupdater commit -v {new_version}'")
    run(f"dgupdater commit -v {new_version}", shell=True, check=True)
    
    # log_info("Running 'dgupdater publish'")
    # call("dgupdater publish", shell=True)
    
    
def main() -> None:
    # log_info("Starting build and release process...")
    
    new_version: str = input("Enter the new version: ")
    
    # # Step 0: Check environment configuration
    check_engine_env(new_version)

    # # Step 1
    update_versions(new_version)

    # # Step 2
    generate_executable()
    
    # Step 3
    firebase_deploy()

    # Step 4
    dgupdater_commit_and_publish(new_version)
    
    # Step 5
    generate_setup_file_windows()  
    
    log_info("Build and release process completed.")


if __name__ == "__main__":
    main()