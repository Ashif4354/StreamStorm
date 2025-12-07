"""Script to trigger the cross-os-build GitHub Actions workflow via repository dispatch."""

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.resolve()

from sys import path  # noqa: E402
path.insert(0, str(ROOT))

from subprocess import run, CompletedProcess  # noqa: E402
from shutil import which  # noqa: E402
from logging import basicConfig, INFO, info as log_info, error as log_error  # noqa: E402

basicConfig(level=INFO)

log_info(f"Root directory: {ROOT}")

REPO: str = "Ashif4354/StreamStorm"
EVENT_TYPE: str = "cross-os-build"


def check_gh_available() -> None:
    """Check if GitHub CLI is available."""
    if not which("gh"):
        raise RuntimeError("GitHub CLI (gh) is not installed or not found in PATH. Please install it to proceed.")
    log_info("GitHub CLI (gh) is available")


def check_gh_auth() -> None:
    """Check if user is authenticated with GitHub CLI."""
    log_info("Checking GitHub CLI authentication...")
    
    result: CompletedProcess[str] = run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        log_error("GitHub CLI is not authenticated. Please run 'gh auth login' first.")
        raise RuntimeError("GitHub CLI authentication required")
    
    log_info("GitHub CLI is authenticated")


def trigger_workflow() -> None:
    """Trigger the cross-os-build workflow via repository dispatch."""
    log_info(f"Triggering '{EVENT_TYPE}' workflow on {REPO}...")
    
    cmd: list[str] = [
        "gh", "api",
        "--method", "POST",
        f"/repos/{REPO}/dispatches",
        "-f", f"event_type={EVENT_TYPE}"
    ]
    
    result: CompletedProcess[str] = run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        log_error(f"Failed to trigger workflow: {result.stderr}")
        raise RuntimeError(f"Failed to trigger workflow: {result.stderr}")
    
    log_info("Workflow triggered successfully!")
    log_info(f"Check the Actions tab at: https://github.com/{REPO}/actions")


def main() -> None:
    """Main entry point."""
    check_gh_available()
    check_gh_auth()
    trigger_workflow()
    log_info("Cross-OS build workflow trigger completed.")


if __name__ == "__main__":
    main()
