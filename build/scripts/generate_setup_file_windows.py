"""Script to generate Windows setup file using Inno Setup."""

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from subprocess import call  # noqa: E402
from os import chdir  # noqa: E402
from shutil import which, copy2  # noqa: E402
from logging import basicConfig, INFO, info as log_info  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")


def generate_setup_file_windows() -> None:
    """Generate Windows setup file using Inno Setup Compiler."""
    log_info("Generating setup file using Inno Setup...")
    
    iscc_bin = which("ISCC")
    if not iscc_bin:
        for p in [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe"
        ]:
            if Path(p).exists():
                iscc_bin = p
                break

    if not iscc_bin:
        log_info("Inno Setup Compiler (ISCC) not found!")
        raise EnvironmentError("Inno Setup Compiler (ISCC) not found. Install or add it to PATH.")

    chdir(ROOT / "build" / "INNO Setup")
    
    cmd = f'"{iscc_bin}" create_setup.iss'
    log_info(f"Running '{cmd}'")
    ret = call(cmd, shell=True)
    if ret != 0:
        raise RuntimeError(f"Inno Setup compilation failed with exit code {ret}")

    setup_file = ROOT / "export" / "installers" / "StreamStorm Setup.exe"
    setup_file_underscore = ROOT / "export" / "installers" / "StreamStorm_Setup.exe"

    if not setup_file.exists():
        raise FileNotFoundError(
            f"Expected Inno Setup installer not found at '{setup_file}'. Check Inno Setup build logs."
        )

    log_info(f"Creating copy {setup_file_underscore}")
    copy2(setup_file, setup_file_underscore)

    log_info("Setup file generation completed successfully.")


def main() -> None:
    """Main entry point."""
    generate_setup_file_windows()
    log_info("Generate setup file process completed.")


if __name__ == "__main__":
    main()
