from subprocess import call, run
from os import chdir
from pathlib import Path
from shutil import move, rmtree, which
from tomlkit import TOMLDocument, parse, dumps
from json import dump, load
from re import sub
from logging import basicConfig, INFO, info as log_info

basicConfig(level=INFO)

ROOT: Path = Path(__file__).parent.resolve()
log_info(f"Root directory: {ROOT}")

def update_versions(new_version: str) -> None:

    log_info(f"Updating versions to {new_version}")
    
    # Engine/pyproject.toml
    pyproject_toml_path: Path = ROOT / "Engine" / "pyproject.toml"
    log_info(f"Updating {pyproject_toml_path}")
    
    with open(pyproject_toml_path, "r") as f:
        pyproject_data: TOMLDocument = parse(f.read())        
        
    pyproject_data["project"]["version"] = new_version
    with open(pyproject_toml_path, "w") as f:
        f.write(dumps(pyproject_data))

    # UI/package.json
    package_json_path: Path = ROOT / "UI" / "package.json"
    log_info(f"Updating {package_json_path}")
    
    with open(package_json_path, "r") as f:
        package_data: dict = load(f)
        
    package_data["version"] = new_version
    
    with open(package_json_path, "w") as f:
        dump(package_data, f, indent=4)

    # Site/package.json
    site_package_json_path: Path = ROOT / "Site" / "package.json"
    log_info(f"Updating {site_package_json_path}")
    
    with open(site_package_json_path, "r") as f:
        site_data: dict = load(f)
        
    site_data["version"] = new_version
    
    with open(site_package_json_path, "w") as f:
        dump(site_data, f, indent=4)

    # INNO Setup / create_setup.iss
    create_setup_iss: Path = ROOT / "INNO Setup" / "create_setup.iss"
    
    log_info(f"Updating {create_setup_iss}")
    text: str = create_setup_iss.read_text(encoding="utf-8")
    text = sub(r'#define MyAppVersion\s+".*"', f'#define MyAppVersion "{new_version}"', text)
    create_setup_iss.write_text(text, encoding="utf-8")


def generate_exe() -> None:
    log_info("Generating executable...")
    
    chdir(ROOT / "Engine")
    
    log_info("Running 'uv sync' in Engine directory")
    
    call("uv sync", shell=True)
    chdir(ROOT)

    build_command: str = ([
        "pyinstaller",
        "StreamStorm.spec",
        "--noconfirm",
        "--clean"
    ])

    log_info(f"Running build command: {' '.join(build_command)}")
    call(build_command)

    dist_dir: Path = ROOT / "dist"
    exe_path: Path = dist_dir / "StreamStorm.exe"
    output_dir: Path = ROOT / "output"

    target_path: Path = output_dir / "StreamStorm.exe"

    if exe_path.exists():
        log_info(f"Moving {exe_path} to {output_dir}")
        
        if target_path.exists():
            log_info(f"Removing existing {target_path}")
            
            target_path.unlink()
            
        move(str(exe_path), str(output_dir))
        
    else:
        log_info("Built .exe file not found!")
        raise FileNotFoundError("Built .exe file not found")

    build_dir: Path = ROOT / "build"
    
    log_info(f"Cleaning up {dist_dir} and {build_dir}")
    rmtree(dist_dir, ignore_errors=True)
    rmtree(build_dir, ignore_errors=True)
    
def generate_setup_file() -> None:
    log_info("Generating setup file using Inno Setup...")
    
    if not which("ISCC"):
        log_info("Inno Setup Compiler (ISCC) not found!")
        
        raise EnvironmentError("Inno Setup Compiler (ISCC) not found. Install or add it to PATH.")

    chdir(ROOT / "INNO Setup")
    
    log_info("Running 'ISCC create_setup.iss'")
    call("ISCC create_setup.iss", shell=True)
    
def build_SITE() -> None:
    log_info("Building Site...")
    
    chdir(ROOT / "Site")
    
    log_info("Running 'vite build' in Site directory")    
    call("vite build", shell=True)
    chdir(ROOT)

def build_UI() -> None:
    log_info("Building UI...")
    
    chdir(ROOT / "UI")
    
    log_info("Running 'vite build' in UI directory")
    call("vite build", shell=True)
    chdir(ROOT)

def firebase_deploy() -> None:
    log_info("Deploying to Firebase...")
    
    chdir(ROOT)
    
    log_info("Running 'firebase deploy'")
    call("firebase deploy", shell=True)

def dgupdater_commit_and_publish(new_version: str) -> None:
    log_info(f"Committing and publishing with dgupdater for version {new_version}")
    
    chdir(ROOT / "output")
    
    log_info(f"Running 'dgupdater commit -v {new_version}'")
    run(f"dgupdater commit -v {new_version}", shell=True, check=True)
    
    log_info("Running 'dgupdater publish'")
    call("dgupdater publish", shell=True)
    
def main() -> None:
    log_info("Starting build and release process...")
    
    new_version: str = input("Enter the new version: ")

    update_versions(new_version)
    generate_exe()
    generate_setup_file()
    build_SITE()
    build_UI()
    firebase_deploy()
    dgupdater_commit_and_publish(new_version)
    
    log_info("Build and release process completed.")


if __name__ == "__main__":
    main()