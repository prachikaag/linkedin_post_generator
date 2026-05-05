"""
Tracks which article URLs have already been turned into posts so that
re-running the pipeline on the same day doesn't produce duplicate drafts.

History is stored as a JSON file at posts/.post_history.json.
"""

import json
from datetime import datetime
from pathlib import Path

from .news_gatherer import Article


class PostHistory:
    def __init__(self, posts_dir: Path):
        self._file = posts_dir / ".post_history.json"
        self._data: dict = self._load()

    # ── Public API ─────────────────────────────────────────────────────────────

    def filter_new(self, articles: list[Article]) -> list[Article]:
        """Return only articles whose URL hasn't been used as a primary anchor yet."""
        processed = set(self._data.get("processed_urls", []))
        return [a for a in articles if a.url and a.url not in processed]

    def mark_done(self, articles: list[Article], filename: str) -> None:
        """Record all article URLs from a generated post so they're skipped next run."""
        processed = set(self._data.get("processed_urls", []))
        for a in articles:
            if a.url:
                processed.add(a.url)
        self._data["processed_urls"] = sorted(processed)
        self._data.setdefault("generated_posts", []).append(
            {
                "filename": filename,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "source_urls": [a.url for a in articles if a.url],
            }
        )
        self._save()

    def stats(self) -> dict:
        return {
            "processed_urls": len(self._data.get("processed_urls", [])),
            "generated_posts": len(self._data.get("generated_posts", [])),
        }

    # ── Internal ───────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if self._file.exists():
            try:
                return json.loads(self._file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {"processed_urls": [], "generated_posts": []}

    def _save(self) -> None:
        self._file.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
