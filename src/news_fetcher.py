"""
News fetcher: pulls articles from RSS feeds and NewsAPI,
filters by topics, and deduplicates against seen history.
"""

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import feedparser
import requests
import yaml

DATA_DIR = Path(__file__).parent.parent / "data"
SEEN_FILE = DATA_DIR / "seen_articles.json"


def _load_config(name: str) -> dict:
    config_path = Path(__file__).parent.parent / "config" / name
    with open(config_path) as f:
        return yaml.safe_load(f)


def _load_seen() -> set[str]:
    if SEEN_FILE.exists():
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def _save_seen(seen: set[str]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen), f, indent=2)


def _article_matches_topics(text: str, topics_cfg: dict, sources_cfg: dict) -> tuple[bool, list[str]]:
    """Return (matches, matched_categories) for article text."""
    text_lower = text.lower()
    exclude = [kw.lower() for kw in topics_cfg.get("exclude_keywords", [])]
    if any(kw in text_lower for kw in exclude):
        return False, []

    matched = []

    # Check AI companies
    for company in topics_cfg.get("ai_companies", []):
        kws = [k.lower() for k in company.get("keywords", [])]
        if any(kw in text_lower for kw in kws):
            matched.append(f"company:{company['name']}")

    # Check big tech
    for co in topics_cfg.get("big_tech", []):
        kws = [k.lower() for k in co.get("keywords", [])]
        if any(kw in text_lower for kw in kws):
            matched.append(f"bigtech:{co['company']}")

    # Check categories
    for cat in topics_cfg.get("categories", []):
        kws = [k.lower() for k in cat.get("keywords", [])]
        if any(kw in text_lower for kw in kws):
            matched.append(f"category:{cat['id']}")

    # Priority keywords bump all articles
    priority = [kw.lower() for kw in topics_cfg.get("priority_keywords", [])]
    if any(kw in text_lower for kw in priority):
        matched.append("priority")

    return bool(matched), matched


def _parse_date(entry: Any) -> datetime | None:
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "")


def fetch_rss_articles(sources_cfg: dict, topics_cfg: dict, max_age_days: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    articles = []
    feeds = sources_cfg.get("rss_feeds", []) + [
        {"name": q["query"], "url": q["url"], "category": "google_news", "priority": "medium"}
        for q in sources_cfg.get("google_news_queries", [])
    ]

    for feed_cfg in feeds:
        url = feed_cfg["url"]
        try:
            parsed = feedparser.parse(url)
        except Exception as e:
            print(f"  [warn] RSS parse error {url}: {e}")
            continue

        count = 0
        max_per = sources_cfg.get("fetch_settings", {}).get("max_articles_per_source", 10)

        for entry in parsed.entries:
            if count >= max_per:
                break

            pub_date = _parse_date(entry)
            if pub_date and pub_date < cutoff:
                continue

            title = _strip_html(getattr(entry, "title", ""))
            summary = _strip_html(getattr(entry, "summary", ""))
            link = getattr(entry, "link", "")
            combined = f"{title} {summary}"

            matches, matched_cats = _article_matches_topics(combined, topics_cfg, sources_cfg)
            if not matches:
                continue

            articles.append({
                "title": title,
                "summary": summary[:500],
                "url": link,
                "source": feed_cfg["name"],
                "source_priority": feed_cfg.get("priority", "medium"),
                "published": pub_date.isoformat() if pub_date else None,
                "matched_categories": matched_cats,
            })
            count += 1

    return articles


def fetch_newsapi_articles(sources_cfg: dict, topics_cfg: dict, max_age_days: int) -> list[dict]:
    api_key = os.getenv("NEWSAPI_KEY", "")
    cfg = sources_cfg.get("newsapi", {})
    if not cfg.get("enabled") or not api_key:
        return []

    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).strftime("%Y-%m-%d")
    articles = []

    for query in cfg.get("queries", []):
        params = {
            "q": query,
            "apiKey": api_key,
            "language": cfg.get("language", "en"),
            "sortBy": cfg.get("sort_by", "publishedAt"),
            "pageSize": cfg.get("page_size", 20),
            "from": cutoff,
        }
        sources = cfg.get("sources", [])
        if sources:
            params["sources"] = ",".join(sources)

        try:
            resp = requests.get(
                "https://newsapi.org/v2/everything",
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  [warn] NewsAPI error for '{query}': {e}")
            continue

        for art in data.get("articles", []):
            title = art.get("title", "")
            description = art.get("description", "") or ""
            url = art.get("url", "")
            combined = f"{title} {description}"

            matches, matched_cats = _article_matches_topics(combined, topics_cfg, sources_cfg)
            if not matches:
                continue

            pub = art.get("publishedAt")
            articles.append({
                "title": title,
                "summary": description[:500],
                "url": url,
                "source": art.get("source", {}).get("name", "NewsAPI"),
                "source_priority": "medium",
                "published": pub,
                "matched_categories": matched_cats,
            })

        time.sleep(0.5)  # respect rate limits

    return articles


def deduplicate(articles: list[dict], seen: set[str]) -> tuple[list[dict], set[str]]:
    unique = []
    for art in articles:
        url = art.get("url", "")
        if not url:
            continue
        # normalise URL as key
        key = urlparse(url)._replace(query="", fragment="").geturl()
        if key not in seen:
            seen.add(key)
            unique.append(art)
    return unique, seen


def rank_articles(articles: list[dict]) -> list[dict]:
    priority_score = {"high": 3, "medium": 2, "low": 1}

    def score(a: dict) -> int:
        s = priority_score.get(a.get("source_priority", "medium"), 2)
        s += len(a.get("matched_categories", []))
        if "priority" in a.get("matched_categories", []):
            s += 5
        return s

    return sorted(articles, key=score, reverse=True)


def fetch_all(max_articles: int = 30, skip_seen: bool = True) -> list[dict]:
    sources_cfg = _load_config("sources.yaml")
    topics_cfg = _load_config("topics.yaml")
    settings = sources_cfg.get("fetch_settings", {})
    max_age = settings.get("max_article_age_days", 7)

    print("Fetching RSS feeds...")
    rss = fetch_rss_articles(sources_cfg, topics_cfg, max_age)
    print(f"  Found {len(rss)} matching RSS articles")

    print("Fetching NewsAPI articles...")
    napi = fetch_newsapi_articles(sources_cfg, topics_cfg, max_age)
    print(f"  Found {len(napi)} matching NewsAPI articles")

    all_articles = rss + napi

    seen = _load_seen() if skip_seen else set()
    unique, updated_seen = deduplicate(all_articles, seen)
    print(f"  {len(unique)} new articles after deduplication")

    ranked = rank_articles(unique)[:max_articles]

    if skip_seen:
        _save_seen(updated_seen)

    return ranked
