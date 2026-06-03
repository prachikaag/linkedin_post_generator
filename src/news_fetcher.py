"""
news_fetcher.py
Fetches AI news from RSS feeds defined in config/sources.yaml,
scores each article for relevance using keywords from config/topics.yaml,
deduplicates, and returns a ranked list of article dicts.

To add a new source: edit config/sources.yaml — no code change needed.
To change scoring weights or freshness: edit config/topics.yaml.
"""
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import httpx

_HEADERS = {"User-Agent": "LinkedInPostGenerator/1.0 (+https://github.com)"}


# ── Public entry point ────────────────────────────────────────────────────────

def fetch_articles(config: dict) -> list[dict]:
    """
    Fetch, score, deduplicate, and return the top articles.
    Returns a list of article dicts sorted by relevance_score descending.
    """
    sources = config["sources"]
    topics = config["topics"]
    freshness = topics.get("freshness", {})
    max_age_hours = freshness.get("max_article_age_hours", 48)
    min_score = freshness.get("min_relevance_score", 2)
    max_articles = freshness.get("max_articles_per_run", 25)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    feeds = _collect_feeds(sources)
    company_kw, category_kw = _build_keyword_maps(topics)

    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    articles: list[dict] = []

    for feed in feeds:
        try:
            entries = _fetch_feed(feed["url"])
            for entry in entries:
                article = _parse_entry(entry, feed["name"])
                if not article:
                    continue
                if _is_stale(article["published"], cutoff):
                    continue
                if _is_duplicate(article, seen_urls, seen_titles):
                    continue
                scored = _score(article, company_kw, category_kw)
                if scored["relevance_score"] >= min_score:
                    seen_urls.add(article["url"])
                    seen_titles.add(_norm_title(article["title"]))
                    articles.append(scored)
        except Exception:
            continue  # skip broken feeds silently

    articles.sort(key=lambda a: a["relevance_score"], reverse=True)
    return articles[:max_articles]


# ── Feed collection ───────────────────────────────────────────────────────────

def _collect_feeds(sources: dict) -> list[dict]:
    """Collect all enabled feeds sorted high → medium → low priority."""
    order = {"high": 0, "medium": 1, "low": 2}
    feeds = []
    for category in sources.get("rss_feeds", {}).values():
        for feed in category:
            if feed.get("enabled", True):
                feeds.append(feed)
    feeds.sort(key=lambda f: order.get(f.get("priority", "low"), 3))
    return feeds


# ── Keyword maps ──────────────────────────────────────────────────────────────

def _build_keyword_maps(topics: dict) -> tuple[dict, dict]:
    """Build lowercased keyword → name lookup maps."""
    company_kw: dict[str, str] = {}
    for group in topics.get("companies_to_track", {}).values():
        for company in group:
            for kw in company.get("keywords", []):
                company_kw[kw.lower()] = company["name"]

    category_kw: dict[str, str] = {}
    for cat in topics.get("topic_categories", []):
        for kw in cat.get("keywords", []):
            category_kw[kw.lower()] = cat["name"]

    return company_kw, category_kw


# ── Fetching ──────────────────────────────────────────────────────────────────

def _fetch_feed(url: str) -> list:
    """Fetch an RSS/Atom feed URL and return its entries."""
    try:
        resp = httpx.get(url, timeout=15, follow_redirects=True, headers=_HEADERS)
        resp.raise_for_status()
        parsed = feedparser.parse(resp.text)
    except Exception:
        # Fallback: let feedparser fetch directly
        parsed = feedparser.parse(url)
    return parsed.entries or []


# ── Parsing ───────────────────────────────────────────────────────────────────

def _parse_entry(entry, source_name: str) -> dict | None:
    """Extract normalised fields from a feedparser entry."""
    title = _strip_html(getattr(entry, "title", "")).strip()
    if not title:
        return None

    url = _best_url(entry)
    if not url:
        return None

    summary = _strip_html(
        getattr(entry, "summary", "")
        or getattr(entry, "description", "")
        or _get_content(entry)
    )[:800]

    published = _parse_date(entry)

    return {
        "title": title,
        "url": url,
        "summary": summary,
        "published": published.isoformat() if published else None,
        "source_name": source_name,
    }


def _best_url(entry) -> str | None:
    """Return the best permalink URL from an entry."""
    candidates = [
        getattr(entry, "link", ""),
        getattr(entry, "id", ""),
    ]
    for c in candidates:
        if c and c.startswith("http"):
            return c
    return None


def _get_content(entry) -> str:
    """Extract raw content string from entry.content list if present."""
    content = getattr(entry, "content", [])
    if content and isinstance(content, list):
        return content[0].get("value", "")
    return ""


def _parse_date(entry) -> datetime | None:
    """Parse published/updated date from feedparser entry."""
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                ts = time.mktime(val)
                return datetime.fromtimestamp(ts, tz=timezone.utc)
            except Exception:
                pass
    return None


# ── Scoring ───────────────────────────────────────────────────────────────────

def _score(article: dict, company_kw: dict, category_kw: dict) -> dict:
    """Score an article by keyword relevance. Company match = +3, category = +1."""
    text = (article["title"] + " " + article["summary"]).lower()
    score = 0
    matched_companies: list[str] = []
    matched_keywords: list[str] = []
    matched_categories: list[str] = []

    for kw, company in company_kw.items():
        if kw in text:
            score += 3
            if company not in matched_companies:
                matched_companies.append(company)
            matched_keywords.append(kw)

    for kw, category in category_kw.items():
        if kw in text:
            score += 1
            if category not in matched_categories:
                matched_categories.append(category)

    return {
        **article,
        "relevance_score": score,
        "matched_companies": matched_companies,
        "matched_keywords": matched_keywords,
        "matched_categories": matched_categories,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _is_stale(published_iso: str | None, cutoff: datetime) -> bool:
    if not published_iso:
        return True
    try:
        dt = datetime.fromisoformat(published_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt < cutoff
    except Exception:
        return True


def _is_duplicate(article: dict, seen_urls: set, seen_titles: set) -> bool:
    if article["url"] in seen_urls:
        return True
    return _norm_title(article["title"]) in seen_titles


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())[:60]


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()
