"""
Post Tracker
------------
Keeps a JSON cache of article URLs that have already been used to generate posts.
Prevents the same news item from appearing in every run.

Cache file: posts/seen_articles.json
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


_CACHE_FILENAME = "seen_articles.json"
# Articles are considered "seen" for this many days — older entries are pruned
_MAX_AGE_DAYS = 14


class PostTracker:
    def __init__(self, posts_dir: Path):
        self.cache_path = posts_dir / _CACHE_FILENAME
        self._cache: dict[str, str] = {}  # url → ISO timestamp when seen
        self._load()

    # ── Public API ─────────────────────────────────────────────────────────────

    def is_seen(self, url: str) -> bool:
        """Return True if this URL has already been used in a post this cycle."""
        return url in self._cache

    def mark_seen(self, urls: list[str]) -> None:
        """Record these URLs as used. Call after a post is successfully generated."""
        now = datetime.now(tz=timezone.utc).isoformat()
        for url in urls:
            if url:
                self._cache[url] = now
        self._save()

    def filter_unseen(self, articles: list) -> list:
        """Return only articles whose URL has not been seen before."""
        return [a for a in articles if not self.is_seen(a.url)]

    def seen_count(self) -> int:
        return len(self._cache)

    def reset(self) -> None:
        """Clear the cache — useful if you want to regenerate posts from old news."""
        self._cache = {}
        self._save()

    # ── Internal ───────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self.cache_path.exists():
            return
        try:
            raw = json.loads(self.cache_path.read_text(encoding="utf-8"))
            self._cache = {k: v for k, v in raw.items() if isinstance(k, str)}
            self._prune()
        except (json.JSONDecodeError, OSError):
            self._cache = {}

    def _save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(self._cache, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _prune(self) -> None:
        """Remove entries older than _MAX_AGE_DAYS to keep the file tidy."""
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=_MAX_AGE_DAYS)
        to_remove = []
        for url, ts in self._cache.items():
            try:
                seen_at = datetime.fromisoformat(ts)
                if seen_at < cutoff:
                    to_remove.append(url)
            except (ValueError, TypeError):
                to_remove.append(url)
        for url in to_remove:
            del self._cache[url]
