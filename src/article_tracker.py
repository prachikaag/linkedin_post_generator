"""
Article Tracker
---------------
Persists a record of every article URL that has been used as a source in a
generated post. On each pipeline run the tracker filters out already-used
articles so the same story never gets written about twice.

Storage: data/processed_articles.json
  {
    "processed": [
      {"url": "https://...", "title": "...", "used_at": "2026-05-06T12:00:00"}
    ]
  }

Edit the JSON file directly if you want to force-reuse an article
(e.g. delete its entry or clear the whole list for a fresh start).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .news_gatherer import Article

_DATA_DIR = Path(__file__).parent.parent / "data"
_TRACKER_FILE = _DATA_DIR / "processed_articles.json"


class ArticleTracker:
    def __init__(self):
        _DATA_DIR.mkdir(exist_ok=True)
        self._processed: dict[str, dict] = {}
        self._load()

    # ── Public API ─────────────────────────────────────────────────────────────

    def filter_new(self, articles: list) -> list:
        """Return only articles whose URL has not been used in a previous run."""
        return [a for a in articles if a.url not in self._processed]

    def mark_used(self, articles: list) -> None:
        """Record that these articles were used as sources in a generated post."""
        for a in articles:
            if a.url and a.url not in self._processed:
                self._processed[a.url] = {
                    "url": a.url,
                    "title": a.title,
                    "used_at": datetime.now(tz=timezone.utc).isoformat(),
                }
        self._save()

    def count(self) -> int:
        return len(self._processed)

    def clear(self) -> None:
        """Reset the tracker — all articles will be considered fresh on next run."""
        self._processed = {}
        self._save()

    # ── Internal ───────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not _TRACKER_FILE.exists():
            self._processed = {}
            return
        try:
            data = json.loads(_TRACKER_FILE.read_text(encoding="utf-8"))
            self._processed = {e["url"]: e for e in data.get("processed", []) if e.get("url")}
        except (json.JSONDecodeError, KeyError):
            self._processed = {}

    def _save(self) -> None:
        payload = {"processed": list(self._processed.values())}
        _TRACKER_FILE.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
