"""Script to generate Windows setup file using Inno Setup."""

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from subprocess import call  # noqa: E402
from os import chdir  # noqa: E402
from shutil import which  # noqa: E402
from logging import basicConfig, INFO, info as log_info  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")


def generate_setup_file_windows() -> None:
    """Generate Windows setup file using Inno Setup Compiler."""
    log_info("Generating setup file using Inno Setup...")
    
    if not which("ISCC"):
        log_info("Inno Setup Compiler (ISCC) not found!")
        
        raise EnvironmentError("Inno Setup Compiler (ISCC) not found. Install or add it to PATH.")

    chdir(ROOT / "build" / "INNO Setup")
    
    log_info("Running 'ISCC create_setup.iss'")
    call("ISCC create_setup.iss", shell=True)
    
    log_info("Setup file generation completed successfully.")


def main() -> None:
    """Main entry point."""
    generate_setup_file_windows()
    log_info("Generate setup file process completed.")


if __name__ == "__main__":
    main()
