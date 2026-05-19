import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Article:
    title: str
    url: str
    summary: str
    published: Optional[datetime]
    source_name: str
    relevance_score: int = 0
    matched_keywords: list = field(default_factory=list)
    matched_companies: list = field(default_factory=list)
    matched_categories: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "published": self.published.isoformat() if self.published else None,
            "source_name": self.source_name,
            "relevance_score": self.relevance_score,
            "matched_keywords": self.matched_keywords,
            "matched_companies": self.matched_companies,
            "matched_categories": self.matched_categories,
        }


class NewsGatherer:
    """
    Fetches current AI news via Claude WebSearch.

    Builds targeted search queries dynamically from config/topics.yaml, runs
    each query, deduplicates the results, and scores every article by
    keyword relevance. Falls back gracefully if the CLI is unavailable.
    """

    def __init__(self, sources_config: dict, topics_config: dict):
        self.sources_config = sources_config
        self.topics_config = topics_config
        freshness = topics_config.get("freshness", {})
        self.min_score = freshness.get("min_relevance_score", 2)
        self.max_articles = freshness.get("max_articles_per_run", 25)

    def fetch_all(self) -> list["Article"]:
        if not shutil.which("claude"):
            print("  [error] `claude` CLI not found. Install Claude Code to enable news fetching.")
            return []

        queries = self._build_queries()
        all_articles: list[Article] = []
        seen_urls: set[str] = set()
        seen_titles: set[str] = set()

        for i, query in enumerate(queries, 1):
            print(f"  Searching ({i}/{len(queries)}): {query[:60]}...")
            for a in self._run_search(query):
                norm = re.sub(r"[^a-z0-9]", "", a.title.lower())[:60]
                if a.url in seen_urls or norm in seen_titles:
                    continue
                seen_urls.add(a.url)
                seen_titles.add(norm)
                all_articles.append(a)

        scored = [self._score_article(a) for a in all_articles]
        scored = [a for a in scored if a.relevance_score >= self.min_score]
        scored.sort(key=lambda a: a.relevance_score, reverse=True)
        return scored[: self.max_articles]

    # ── Query construction ─────────────────────────────────────────────────────

    def _build_queries(self) -> list[str]:
        """Build targeted search queries from topics config — at most 6 queries."""
        queries: list[str] = []

        # 1. Top AI companies grouped — high-signal queries
        companies_to_track = self.topics_config.get("companies_to_track", {})
        ai_labs = companies_to_track.get("ai_labs", [])
        big_tech = companies_to_track.get("big_tech", [])
        ai_builders = companies_to_track.get("ai_builders", [])

        if ai_labs:
            names = " OR ".join(c["name"] for c in ai_labs[:6])
            queries.append(f"({names}) new feature launch announcement 2026")

        if big_tech:
            names = " OR ".join(c["name"] for c in big_tech[:4])
            queries.append(f"({names}) AI announcement 2026")

        if ai_builders:
            names = " OR ".join(c["name"] for c in ai_builders[:5])
            queries.append(f"({names}) AI news 2026")

        # 2. Topic category queries
        categories = self.topics_config.get("topic_categories", [])
        for cat in categories[:2]:
            kws = cat.get("keywords", [])[:3]
            if kws:
                queries.append(" ".join(kws) + " 2026")

        # 3. Always include a funding / startup query
        queries.append("AI startup funding raised million billion 2026")

        return queries[:6]

    # ── WebSearch via claude CLI ───────────────────────────────────────────────

    def _run_search(self, query: str) -> list["Article"]:
        prompt = f"""Use WebSearch to search for: {query}

Return ONLY a valid JSON array of the top 5 results. No markdown fences, no explanation.
Each item must have exactly these fields:
{{
  "title": "article headline",
  "url": "https://full-article-url",
  "summary": "1-2 sentence description of the article",
  "source_name": "Publication Name",
  "published": "YYYY-MM-DD or leave empty string if unknown"
}}

Return the raw JSON array starting with [ and ending with ].
"""
        try:
            result = subprocess.run(
                [
                    "claude", "-p",
                    "--model", "claude-haiku-4-5",
                    "--allowedTools", "WebSearch",
                    "--no-session-persistence",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=60,
                cwd="/tmp",
            )
        except subprocess.TimeoutExpired:
            print(f"  [skip] Search timed out: {query[:40]}")
            return []
        except Exception as exc:
            print(f"  [skip] Search error: {exc}")
            return []

        if result.returncode != 0 or not result.stdout.strip():
            return []

        return _parse_search_json(result.stdout)

    # ── Relevance scoring ──────────────────────────────────────────────────────

    def _score_article(self, article: "Article") -> "Article":
        text = (article.title + " " + article.summary).lower()
        score = 0
        matched_companies: list[str] = []
        matched_keywords: list[str] = []
        matched_categories: list[str] = []

        for company_list in self.topics_config.get("companies_to_track", {}).values():
            for company in company_list:
                for kw in company.get("keywords", []):
                    if kw.lower() in text:
                        score += 3
                        cname = company["name"]
                        if cname not in matched_companies:
                            matched_companies.append(cname)
                        if kw not in matched_keywords:
                            matched_keywords.append(kw)

        for category in self.topics_config.get("topic_categories", []):
            for kw in category.get("keywords", []):
                if kw.lower() in text:
                    score += 1
                    cname = category["name"]
                    if cname not in matched_categories:
                        matched_categories.append(cname)

        article.relevance_score = score
        article.matched_companies = matched_companies
        article.matched_keywords = matched_keywords
        article.matched_categories = matched_categories
        return article


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_search_json(text: str) -> list["Article"]:
    """Extract a JSON array of articles from Claude's raw output."""
    # Strip markdown fences
    text = re.sub(r"```[a-z]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```", "", text)

    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        return []

    try:
        items = json.loads(match.group(0))
    except (json.JSONDecodeError, TypeError):
        return []

    articles: list[Article] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        if not title or not url or not url.startswith("http"):
            continue

        pub_str = str(item.get("published", "") or "").strip()
        published: Optional[datetime] = None
        if pub_str:
            try:
                from dateutil import parser as dateparser
                published = dateparser.parse(pub_str)
                if published and published.tzinfo is None:
                    published = published.replace(tzinfo=timezone.utc)
            except Exception:
                pass

        articles.append(
            Article(
                title=title,
                url=url,
                summary=str(item.get("summary", "") or "")[:800],
                published=published,
                source_name=str(item.get("source_name", "Web") or "Web"),
            )
        )

    return articles
