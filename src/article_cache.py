"""
Persistent cache of seen article URLs.

Prevents the same articles from being re-processed across pipeline runs.
Backed by a JSON file in the data/ directory.
"""

import json
from pathlib import Path


class ArticleCache:
    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self._seen: set[str] = self._load()

    def _load(self) -> set[str]:
        if self.cache_path.exists():
            try:
                data = json.loads(self.cache_path.read_text(encoding="utf-8"))
                return set(data.get("seen_urls", []))
            except Exception:
                return set()
        return set()

    def save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps({"seen_urls": sorted(self._seen)}, indent=2),
            encoding="utf-8",
        )

    def is_seen(self, url: str) -> bool:
        return bool(url) and url in self._seen

    def mark_seen(self, urls: list[str]) -> None:
        self._seen.update(u for u in urls if u)

    def filter_new(self, articles: list) -> list:
        return [a for a in articles if not self.is_seen(a.url)]

    def clear(self) -> None:
        self._seen.clear()
        if self.cache_path.exists():
            self.cache_path.unlink()

    @property
    def size(self) -> int:
        return len(self._seen)
