"""
config_loader.py
Loads all YAML configuration files and environment variables.
Edit the files in config/ to customise behaviour — no code changes needed.
"""
from pathlib import Path
import yaml
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


def load_all() -> dict:
    """Return a single dict containing all config and env vars."""
    load_dotenv(BASE_DIR / ".env")
    return {
        "topics": _load_yaml("config/topics.yaml"),
        "brand_kit": _load_yaml("config/brand_kit.yaml"),
        "sources": _load_yaml("config/sources.yaml"),
        "anthropic_model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        "notion_api_key": os.getenv("NOTION_API_KEY", ""),
        "notion_page_id": os.getenv("NOTION_PAGE_ID", ""),
        "newsapi_key": os.getenv("NEWSAPI_KEY", ""),
    }


def _load_yaml(relative_path: str) -> dict:
    path = BASE_DIR / relative_path
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
