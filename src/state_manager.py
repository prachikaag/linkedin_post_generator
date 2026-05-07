"""
Tracks which article URLs have already been processed so the pipeline never
generates duplicate posts across runs.  State is persisted as a simple JSON file
at data/processed_articles.json (created automatically; excluded from git).
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .news_gatherer import Article

_DEFAULT_STATE_FILE = Path(__file__).parent.parent / "data" / "processed_articles.json"
_EXPIRY_DAYS = 30


class StateManager:
    def __init__(self, state_file: Path | None = None):
        self.state_file = state_file or _DEFAULT_STATE_FILE
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state: dict[str, dict] = self._load()

    # ── Public API ─────────────────────────────────────────────────────────────

    def is_processed(self, url: str) -> bool:
        return bool(url) and url in self._state

    def mark_processed(self, url: str, title: str = "") -> None:
        if not url:
            return
        self._state[url] = {
            "title": title[:120],
            "processed_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        self._save()

    def mark_batch(self, articles: list) -> None:
        for a in articles:
            if a.url:
                self.mark_processed(a.url, a.title)

    def filter_new(self, articles: list) -> list:
        """Return only articles that have not been processed before."""
        return [a for a in articles if not self.is_processed(a.url)]

    def purge_expired(self) -> int:
        """Remove entries older than EXPIRY_DAYS. Returns count removed."""
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=_EXPIRY_DAYS)
        expired = [
            url
            for url, data in self._state.items()
            if _parse_dt(data.get("processed_at", "")) < cutoff
        ]
        for url in expired:
            del self._state[url]
        if expired:
            self._save()
        return len(expired)

    def stats(self) -> dict:
        return {"total_processed": len(self._state)}

    # ── Persistence ────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self) -> None:
        self.state_file.write_text(
            json.dumps(self._state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _parse_dt(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)
