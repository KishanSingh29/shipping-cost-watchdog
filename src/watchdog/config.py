"""Configuration loading helpers."""
from pathlib import Path
from typing import Any
import yaml


def load_config(path: str | Path = "config.yaml") -> dict[str, Any]:
    """Load YAML configuration and return its mapping."""
    with Path(path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a YAML mapping")
    return config
