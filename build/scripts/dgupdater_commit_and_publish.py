"""Script to commit and publish using dgupdater."""

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path, argv  # noqa: E402
path.insert(0, str(ROOT))

import os  # noqa: E402
import json  # noqa: E402
from shutil import which  # noqa: E402
from subprocess import run  # noqa: E402
from os import chdir  # noqa: E402
from logging import basicConfig, INFO, info as log_info, warning as log_warning  # noqa: E402
from platformdirs import user_data_dir  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")


def ensure_dgupdater_credentials() -> None:
    """Ensure local dgupdater credentials file is set up from environment variables if present."""
    config_dir = Path(user_data_dir("dgupdater", "DarkGlance"))
    config_file = config_dir / "dgupdaterconf.json"

    if os.environ.get("DGUPDATER_CONFIG"):
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file.write_text(os.environ["DGUPDATER_CONFIG"].strip(), encoding="utf-8")
        log_info(f"Configured dgupdater config from DGUPDATER_CONFIG at {config_file}")
    elif os.environ.get("DGUPDATER_MONGODB_URI"):
        config_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "mongodbstrds": {
                "StreamStorm": os.environ["DGUPDATER_MONGODB_URI"].strip()
            }
        }
        config_file.write_text(json.dumps(data, indent=4), encoding="utf-8")
        log_info(f"Configured dgupdater config from DGUPDATER_MONGODB_URI at {config_file}")
    elif not config_file.exists():
        log_warning(
            f"dgupdater config not found at {config_file} and no DGUPDATER_CONFIG or DGUPDATER_MONGODB_URI set."
        )


def get_dgupdater_command() -> str:
    """Find dgupdater CLI command."""
    if which("dgupdater"):
        return "dgupdater"

    venv_exe = (
        ROOT
        / "src"
        / "Engine"
        / ".venv"
        / ("Scripts" if os.name == "nt" else "bin")
        / ("dgupdater.exe" if os.name == "nt" else "dgupdater")
    )
    if venv_exe.exists():
        return f'"{venv_exe}"'

    return "uv run --directory src/Engine dgupdater"


def dgupdater_commit_and_publish(new_version: str) -> None:
    """Commit and publish using dgupdater without relying on fragile prompt stdin piping."""
    if new_version.lower().startswith("v"):
        new_version = new_version[1:]

    ensure_dgupdater_credentials()

    log_info(f"Committing and publishing with dgupdater for version {new_version}")
    
    chdir(ROOT / "export" / "windows")

    try:
        from dgupdater.cli_commands.commit.func.check_configuration_files_exists import (
            check_configuration_files_exists,
        )
        from dgupdater.cli_commands.commit.func.update_version import update_version
        from dgupdater.cli_commands.commit.func.commit_changes import commit_changes
        from dgupdater.cli_commands.publish.func.publish_changes import publish_changes

        log_info("Validating configuration files exist...")
        check_configuration_files_exists()

        log_info(f"Updating dgupdater version to {new_version}...")
        update_version(new_version)

        log_info("Generating and committing release chunks...")
        commit_changes()

        log_info("Publishing release chunks to updater database...")
        publish_changes()

        log_info("dgupdater commit and publish completed successfully via direct API.")
        return
    except ImportError as e:
        log_warning(f"Could not import dgupdater internals directly: {e}. Falling back to CLI.")

    cmd = f"{get_dgupdater_command()} commit -v {new_version}"
    log_info(f"Running command: {cmd}")
    run(cmd, shell=True, check=True)
    log_info("dgupdater commit and publish completed successfully.")


def main() -> None:
    """Main entry point."""
    args = [arg for arg in argv[1:] if not arg.startswith("--")]

    if args and args[0].strip():
        new_version = args[0].strip()
    elif os.environ.get("NEW_VERSION"):
        new_version = os.environ["NEW_VERSION"].strip()
    elif os.environ.get("VERSION"):
        new_version = os.environ["VERSION"].strip()
    else:
        project_json_file = ROOT / "project.json"
        if project_json_file.exists():
            try:
                new_version = json.loads(project_json_file.read_text())["version"]
            except Exception:
                new_version = input("Enter the new version: ")
        else:
            new_version = input("Enter the new version: ")

    dgupdater_commit_and_publish(new_version)
    log_info("dgupdater commit and publish process completed.")


if __name__ == "__main__":
    main()
