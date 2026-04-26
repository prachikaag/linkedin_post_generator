"""
Tracks which article URLs have already been used to generate posts.
Prevents the same news item from producing duplicate drafts across runs.
History entries expire after EXPIRY_DAYS days so evergreen topics can resurface.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent / "data" / "article_history.json"
EXPIRY_DAYS = 14


class ArticleHistory:
    def __init__(self, filepath: Path = HISTORY_FILE):
        self.filepath = filepath
        self.filepath.parent.mkdir(exist_ok=True)
        self._data: dict[str, str] = self._load()

    def is_used(self, url: str) -> bool:
        """Return True if this URL was already used in a generated post."""
        return bool(url) and url.rstrip("/") in self._data

    def mark_used(self, urls: list[str]) -> None:
        """Record that these article URLs were used in a generated post."""
        now = datetime.now(tz=timezone.utc).isoformat()
        for url in urls:
            if url:
                self._data[url.rstrip("/")] = now
        self._save()

    def purge_expired(self) -> int:
        """Remove entries older than EXPIRY_DAYS. Returns count removed."""
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=EXPIRY_DAYS)
        before = len(self._data)
        self._data = {
            url: ts
            for url, ts in self._data.items()
            if datetime.fromisoformat(ts) >= cutoff
        }
        removed = before - len(self._data)
        if removed > 0:
            self._save()
        return removed

    def stats(self) -> dict:
        return {"tracked_urls": len(self._data), "expiry_days": EXPIRY_DAYS}

    def _load(self) -> dict[str, str]:
        if not self.filepath.exists():
            return {}
        try:
            return json.loads(self.filepath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self) -> None:
        self.filepath.write_text(
            json.dumps(self._data, indent=2, sort_keys=True), encoding="utf-8"
        )
