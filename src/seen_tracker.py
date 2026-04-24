"""
Tracks which article URLs have already been used as post anchors.
Prevents the pipeline from regenerating posts for articles it has already processed.

Storage: data/seen_articles.json  (one URL → ISO timestamp per line)
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


class SeenTracker:
    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = data_dir / "seen_articles.json"
        self._seen: dict[str, str] = self._load()

    # ── Public API ─────────────────────────────────────────────────────────────

    def is_seen(self, url: str) -> bool:
        return bool(url) and url in self._seen

    def mark_seen(self, url: str) -> None:
        if url:
            self._seen[url] = datetime.now(timezone.utc).isoformat()
            self._save()

    def filter_unseen(self, articles: list) -> list:
        """Return only articles whose primary URL has not been processed before."""
        return [a for a in articles if not self.is_seen(a.url)]

    def cleanup_old(self, days: int = 30) -> int:
        """Remove entries older than `days`. Returns number of entries removed."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        before = len(self._seen)
        self._seen = {
            url: ts
            for url, ts in self._seen.items()
            if datetime.fromisoformat(ts) > cutoff
        }
        removed = before - len(self._seen)
        if removed:
            self._save()
        return removed

    @property
    def count(self) -> int:
        return len(self._seen)

    # ── Internal ───────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if self.filepath.exists():
            try:
                return json.loads(self.filepath.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save(self) -> None:
        self.filepath.write_text(
            json.dumps(self._seen, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
