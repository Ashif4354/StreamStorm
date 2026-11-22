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


def parse_semver(version: str) -> list[int]:
    """Parse X.Y.Z into ints, raising ValueError on anything else."""
    parts = [int(x) for x in version.strip().split(".")]
    if len(parts) != 3:
        raise ValueError(f"'{version}' is not a valid X.Y.Z version.")
    return parts


def parse_published_version(version: object) -> list[int]:
    """Parse a version stored by dgupdater, treating the unpublished placeholder as 0.0.0."""
    if not isinstance(version, str) or not version.strip() or " " in version.strip():
        return [0, 0, 0]
    return parse_semver(version)


def get_local_dgupdater_version() -> list[int]:
    """Read the version recorded in the local dgupdaterconf.json (cwd must be export/windows)."""
    return parse_published_version(json.loads(Path("dgupdaterconf.json").read_text(encoding="utf-8")).get("version"))


def get_database_version(app_name: str) -> list[int] | None:
    """Read the currently published version from the updater database, or None if nothing is published yet."""
    from pymongo import MongoClient

    config_file = Path(user_data_dir("dgupdater", "DarkGlance")) / "dgupdaterconf.json"
    connection_string = json.loads(config_file.read_text(encoding="utf-8"))["mongodbstrds"][app_name]

    with MongoClient(connection_string, serverSelectionTimeoutMS=30000) as client:
        config = client["DGUPDATER"][app_name].find_one({"_id": f"{app_name}_config"}, {"version": 1})

    if config is None:
        return None
    return parse_published_version(config.get("version"))


def ensure_version_is_newer(new_version: str) -> None:
    """Refuse to publish a version older than what is already published."""
    new = parse_semver(new_version)
    conf = json.loads(Path("dgupdaterconf.json").read_text(encoding="utf-8"))

    local = get_local_dgupdater_version()
    if new < local:
        raise SystemExit(
            f"Refusing to publish {new_version}: it is lower than the version in dgupdaterconf.json "
            f"({'.'.join(map(str, local))})."
        )

    try:
        published = get_database_version(conf["app_name"])
    except Exception as e:
        raise SystemExit(f"Refusing to publish: could not verify the currently published version ({e!r}).") from e

    if published is not None and new < published:
        raise SystemExit(
            f"Refusing to publish {new_version}: the updater database already has "
            f"{'.'.join(map(str, published))}. Publishing would downgrade it."
        )
    if published is not None and new == published:
        log_warning(f"Version {new_version} is already published; republishing the same version.")

    log_info(f"Version check passed: {new_version} > local {local} and published {published}.")


def dgupdater_commit_and_publish(new_version: str) -> None:
    """Commit and publish using dgupdater without relying on fragile prompt stdin piping."""
    if new_version.lower().startswith("v"):
        new_version = new_version[1:]

    ensure_dgupdater_credentials()

    log_info(f"Committing and publishing with dgupdater for version {new_version}")

    chdir(ROOT / "export" / "windows")

    ensure_version_is_newer(new_version)

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

    publish_cmd = f"{get_dgupdater_command()} publish"
    log_info(f"Running command: {publish_cmd}")
    run(publish_cmd, shell=True, check=True)

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
