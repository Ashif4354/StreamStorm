from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from subprocess import run, CompletedProcess  # noqa: E402
from json import loads  # noqa: E402
from shutil import move, rmtree, which   # noqa: E402
from logging import basicConfig, INFO, info as log_info  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")

def check_gh_available():
    if not which("gh"):
        raise RuntimeError("GitHub CLI (gh) is not installed or not found in PATH. Please install it to proceed.")

def get_latest_run_id() -> str:
    
    log_info("Getting latest run id...")
    
    cmd: list[str] = [
        "gh", "run", "list",
        "--workflow", "cross-os-build.yml",
        "--repo", "Ashif4354/StreamStorm",
        "--limit", "1",
        "--json", "databaseId"
    ]

    result: CompletedProcess[str] = run(cmd, capture_output=True, text=True, check=True)
    
    if data := loads(result.stdout):
        log_info("Latest run id: %s", data[0]["databaseId"])
        return data[0]["databaseId"]
    
    else:
        raise RuntimeError("Bruh, No runs found")


def download_run_artifacts(run_id, streamstorm_deb: Path, streamstorm_tar: Path) -> None:
    
    log_info("Downloading artifacts...")
    
    if streamstorm_deb.exists():
        streamstorm_deb.unlink()
    if streamstorm_tar.exists():
        streamstorm_tar.unlink()
    
    cmd: list[str] = [
        "gh", "run", "download",
        str(run_id),
        "--repo", "Ashif4354/StreamStorm",
        "--dir", "./linux-builds"
    ]

    run(cmd, check=True)
    log_info("Artifacts downloaded")
    
    
def move_artifacts(streamstorm_deb: Path, streamstorm_tar: Path) -> None:
    
    deb_destination: Path = ROOT / "export" / "installers" / "streamstorm.deb"
    tar_destination: Path = ROOT / "export" / "installers" / "streamstorm.tar.gz"
    
    if deb_destination.exists():
        deb_destination.unlink()
    if tar_destination.exists():
        tar_destination.unlink()
    
    move(str(streamstorm_deb), str(ROOT / "export" / "installers" / "streamstorm.deb"))
    move(str(streamstorm_tar), str(ROOT / "export" / "installers" / "streamstorm.tar.gz"))
    
    rmtree(str(ROOT / "linux-builds"))


def main() -> None:
    
    check_gh_available()
    
    streamstorm_deb: Path = ROOT / "linux-builds" / "streamstorm-deb" / "streamstorm.deb"
    streamstorm_tar: Path = ROOT / "linux-builds" / "streamstorm-tar" / "streamstorm.tar.gz"
    
    run_id: str = get_latest_run_id()
    
    download_run_artifacts(run_id, streamstorm_deb, streamstorm_tar)
    
    move_artifacts(streamstorm_deb, streamstorm_tar)

if __name__ == "__main__":
    main()
    
