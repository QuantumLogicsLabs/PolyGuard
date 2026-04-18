import yaml
from pathlib import Path
from typing import Any, Dict


def load_config(config_path: str) -> Dict[str, Any]:
    """Load a YAML config file and return as a dict."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_model_config() -> Dict[str, Any]:
    return load_config("configs/model_config.yaml")


def load_paths_config() -> Dict[str, Any]:
    return load_config("configs/paths.yaml")


def load_api_config() -> Dict[str, Any]:
    return load_config("configs/api_config.yaml")
