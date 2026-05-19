from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"


def load_yaml(filename: str) -> dict:
    path = CONFIG_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_topics() -> dict:
    return load_yaml("topics.yaml")


def load_brand_kit() -> dict:
    return load_yaml("brand_kit.yaml")


def load_sources() -> dict:
    return load_yaml("sources.yaml")
