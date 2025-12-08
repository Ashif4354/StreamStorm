"""Script to commit and publish using dgupdater."""

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from subprocess import run  # noqa: E402
from os import chdir  # noqa: E402
from logging import basicConfig, INFO, info as log_info  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")


def dgupdater_commit_and_publish(new_version: str) -> None:
    """Commit and publish using dgupdater."""
    log_info(f"Committing and publishing with dgupdater for version {new_version}")
    
    chdir(ROOT / "export" / "windows")
    
    log_info(f"Running 'dgupdater commit -v {new_version}'")
    run(f"dgupdater commit -v {new_version}", shell=True, check=True)
    
    # log_info("Running 'dgupdater publish'")
    # call("dgupdater publish", shell=True)
    
    log_info("dgupdater commit and publish completed successfully.")


def main() -> None:
    """Main entry point."""
    new_version: str = input("Enter the new version: ")
    dgupdater_commit_and_publish(new_version)
    log_info("dgupdater commit and publish process completed.")


if __name__ == "__main__":
    main()
