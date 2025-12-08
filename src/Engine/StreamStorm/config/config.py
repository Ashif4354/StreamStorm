from platform import system

from pathlib import Path
ROOT: Path = Path(__file__).parent.parent.parent.parent.parent.resolve()


CONFIG: dict = {
    "ENV": "production", # Valid values: ["development", "production", "test"]
    "VERSION": "3.5.2",
    "ROOT": ROOT,
    "OS": system(),
}

__all__: list[str] = ["CONFIG"]