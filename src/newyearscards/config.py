from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency at runtime
    def load_dotenv(*_args, **_kwargs):  # type: ignore
        return False


DEFAULT_RAW_DIR = "data/raw"
DEFAULT_PROCESSED_DIR = "data/processed"
DEFAULT_TEMPLATES_PATH = "config/address_formats.yml"
DEFAULT_KEY_PATH = "keys/google-sheet-key.json"


@dataclass
class Paths:
    raw_base: Path
    processed_base: Path
    templates: Path
    key_path: Path

    def raw_dir(self, year: int) -> Path:
        return self.raw_base / str(year)

    def processed_dir(self, year: int) -> Path:
        return self.processed_base / str(year)


def load_paths() -> Paths:
    """Load base paths from .env with sensible defaults."""
    load_dotenv()

    raw_base = Path(os.getenv("RAW_DATA_DIR", DEFAULT_RAW_DIR))
    processed_base = Path(os.getenv("PROCESSED_DATA_DIR", DEFAULT_PROCESSED_DIR))
    templates = Path(os.getenv("ADDRESS_TEMPLATES", DEFAULT_TEMPLATES_PATH))
    key_path = Path(os.getenv("SERVICE_ACCOUNT_KEY", DEFAULT_KEY_PATH))

    return Paths(
        raw_base=raw_base,
        processed_base=processed_base,
        templates=templates,
        key_path=key_path,
    )


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
