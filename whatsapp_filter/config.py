# whatsapp_filter/config.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
import json

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


@dataclass
class AppConfig:
    input: str
    valid_output: str = "data/valid_numbers.txt"
    invalid_output: str = "data/invalid_numbers.txt"
    browser: str = "chrome"          # chrome | firefox | edge
    headless: bool = False
    delay: float = 2.0
    mode: str = "single"             # single | threaded | onedriver
    threads: int = 2
    chunk_size: int = 50
    driver_path: Optional[str] = None
    log_file: str = "run_log.txt"


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is not installed. Install with: pip install pyyaml")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_config_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return _load_yaml(path)
    if suffix == ".json":
        return _load_json(path)
    raise ValueError(f"Unsupported config file format: {suffix}")


def merge_config(config_data: Dict[str, Any], cli_overrides: Dict[str, Any]) -> AppConfig:
    merged = dict(config_data)
    for key, value in cli_overrides.items():
        if value is not None:
            merged[key] = value

    if "input" not in merged or not merged["input"]:
        raise ValueError("Input file path is required (config 'input' or --input).")

    return AppConfig(**merged)