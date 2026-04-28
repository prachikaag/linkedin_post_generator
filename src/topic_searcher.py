"""
TopicSearcher
-------------
Finds recent articles on a user-specified topic using Claude WebSearch MCP,
then assembles them into Article objects ready for post generation.

Used by the `write-post --topic` and `write-post --url` CLI commands so you
can generate a post on a specific subject without waiting for the full pipeline.
"""

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Optional

from .news_gatherer import Article, _strip_html


class TopicSearcher:
    """Search for recent articles on a specific topic using Claude WebSearch."""

    def __init__(self, topics_config: dict):
        self.topics_config = topics_config

    def search(self, topic: str, max_articles: int = 6) -> list[Article]:
        """
        Search for recent articles about `topic`.
        Returns a list of Article objects ready to pass into PostGenerator.

        Falls back to an empty list (with a clear message) if Claude CLI
        is unavailable and no API key is set.
        """
        if shutil.which("claude"):
            articles = self._search_via_claude(topic, max_articles)
            if articles:
                print(f"  [WebSearch] Found {len(articles)} article(s) on '{topic}'")
                return articles
            print(f"  [WebSearch] No results for '{topic}' — try a broader phrase")
            return []

        print(
            "  [skip] TopicSearcher requires the Claude CLI (claude command in PATH).\n"
            "  Run inside Claude Code or install the Claude CLI."
        )
        return []

    def search_from_url(self, url: str) -> list[Article]:
        """
        Fetch a specific article URL and find 3–5 related articles to build
        a multi-source cluster. This lets you paste in a single news link
        and get a fully-sourced post.
        """
        if not shutil.which("claude"):
            print("  [skip] TopicSearcher requires the Claude CLI.")
            return []

        return self._fetch_url_plus_related(url)

    # ── Claude WebSearch path ──────────────────────────────────────────────────

    def _search_via_claude(self, topic: str, max_articles: int) -> list[Article]:
        prompt = f"""Search the web for the most recent news and articles about: "{topic}"

Focus on articles published in the last 7 days. Prefer results from:
- Major tech news sites (TechCrunch, The Verge, VentureBeat, Wired, Ars Technica)
- AI company official blogs
- Business/finance news for funding stories

Use WebSearch to find {max_articles} distinct, relevant articles.

Return ONLY a JSON array. Each object must have exactly these fields:
- "title": article headline (string)
- "url": full article URL (string — copy exactly as returned by the search, do NOT modify)
- "summary": 2-3 sentence summary of the article (string)
- "published": ISO 8601 date if available, else "" (string)
- "source_name": publication name (string)

Rules:
- Include only articles that are directly relevant to "{topic}"
- Each article must have a unique URL
- Do NOT include duplicate articles or the same story from multiple outlets
- Return ONLY the raw JSON array starting with [ — no markdown fences, no explanation
"""

        result = subprocess.run(
            [
                "claude", "-p",
                "--model", "haiku",
                "--tools", "WebSearch",
                "--no-session-persistence",
            ],
            input=prompt,
            capture_output=True,
            text=True,
            cwd="/tmp",
            timeout=120,
        )

        if result.returncode != 0 or not result.stdout.strip():
            if result.stderr:
                print(f"  [warn] WebSearch: {result.stderr[:200]}")
            return []

        return _parse_search_results(result.stdout.strip())

    def _fetch_url_plus_related(self, url: str) -> list[Article]:
        prompt = f"""Fetch this article URL and then find 3-4 closely related recent articles on the same topic.

Primary URL to fetch: {url}

Steps:
1. Use WebFetch to retrieve the primary article at: {url}
2. Extract its title, main content summary, and publication date
3. Use WebSearch to find 3-4 other recent articles (last 7 days) about the same specific topic or development
4. Include the primary article as the first result

Return ONLY a JSON array. Each object must have exactly these fields:
- "title": article headline (string)
- "url": full article URL (string — copy exactly, do NOT modify)
- "summary": 2-3 sentence summary (string)
- "published": ISO 8601 date if available, else "" (string)
- "source_name": publication name (string)

The primary article (from {url}) MUST be first in the array.
Return ONLY the raw JSON array starting with [ — no markdown fences, no explanation.
"""

        result = subprocess.run(
            [
                "claude", "-p",
                "--model", "haiku",
                "--tools", "WebFetch,WebSearch",
                "--no-session-persistence",
            ],
            input=prompt,
            capture_output=True,
            text=True,
            cwd="/tmp",
            timeout=150,
        )

        if result.returncode != 0 or not result.stdout.strip():
            if result.stderr:
                print(f"  [warn] URL fetch: {result.stderr[:200]}")
            return []

        return _parse_search_results(result.stdout.strip())


# ── Parsing helper ─────────────────────────────────────────────────────────────

def _parse_search_results(raw: str) -> list[Article]:
    raw = raw.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)
    raw = raw.strip()

    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return []

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []

    articles: list[Article] = []
    seen_urls: set[str] = set()

    for item in data:
        if not isinstance(item, dict):
            continue
        title = _strip_html(str(item.get("title", "")).strip())
        url = str(item.get("url", "")).strip()
        if not title or not url or url in seen_urls or url.startswith("#"):
            continue
        seen_urls.add(url)

        published: Optional[datetime] = None
        raw_date = item.get("published", "")
        if raw_date:
            try:
                published = datetime.fromisoformat(
                    str(raw_date).replace("Z", "+00:00")
                )
            except (ValueError, AttributeError, TypeError):
                published = datetime.now(tz=timezone.utc)

        if not published:
            published = datetime.now(tz=timezone.utc)

        articles.append(
            Article(
                title=title,
                url=url,
                summary=_strip_html(str(item.get("summary", "")))[:800],
                published=published,
                source_name=str(item.get("source_name", "Web")),
            )
        )

    return articles
