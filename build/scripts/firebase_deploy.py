"""Script to deploy to Firebase."""

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from subprocess import call  # noqa: E402
from os import chdir  # noqa: E402
from logging import basicConfig, INFO, info as log_info  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")


def firebase_deploy() -> None:
    """Deploy to Firebase."""
    log_info("Deploying to Firebase...")
    call(str(ROOT / "src" / "functions" / "venv" / "Scripts" / "activate.bat"), shell=True)
    chdir(ROOT / "src")
    
    log_info("Running 'firebase deploy'")
    call("firebase deploy", shell=True)
    
    log_info("Firebase deployment completed successfully.")


def main() -> None:
    """Main entry point."""
    firebase_deploy()
    log_info("Firebase deploy process completed.")


if __name__ == "__main__":
    main()
