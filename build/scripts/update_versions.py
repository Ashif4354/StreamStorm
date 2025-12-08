"""Script to update versions across all configuration files."""

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from tomlkit import TOMLDocument, parse, dumps  # noqa: E402
from json import dump, load  # noqa: E402
from re import sub  # noqa: E402
from logging import basicConfig, INFO, info as log_info  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")


def update_versions(new_version: str) -> None:
    """Update version numbers in all configuration files."""
    
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
    
    log_info("Version update completed successfully.")


def main() -> None:
    """Main entry point."""
    new_version: str = input("Enter the new version: ")
    update_versions(new_version)
    log_info("Update versions process completed.")


if __name__ == "__main__":
    main()
