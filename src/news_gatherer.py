import html
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
import requests


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
    def __init__(self, sources_config: dict, topics_config: dict):
        self.sources_config = sources_config
        self.topics_config = topics_config
        freshness = topics_config.get("freshness", {})
        self.max_age_hours = freshness.get("max_article_age_hours", 48)
        self.min_score = freshness.get("min_relevance_score", 2)
        self.max_articles = freshness.get("max_articles_per_run", 25)

    def fetch_all(self) -> list[Article]:
        articles = []
        feeds = self._collect_feeds()

        for feed_config in feeds:
            if not feed_config.get("enabled", True):
                continue
            try:
                fetched = self._fetch_rss(feed_config["url"], feed_config["name"])
                articles.extend(fetched)
            except Exception as exc:
                print(f"  [skip] {feed_config['name']}: {exc}")

        if self.sources_config.get("optional_apis", {}).get("newsapi", {}).get("enabled"):
            articles.extend(self._fetch_newsapi())

        articles = self._filter_by_freshness(articles)
        articles = self._score_articles(articles)
        articles = self._deduplicate(articles)
        articles = [a for a in articles if a.relevance_score >= self.min_score]
        articles.sort(key=lambda a: a.relevance_score, reverse=True)
        return articles[: self.max_articles]

    # ── Private helpers ────────────────────────────────────────────────────────

    def _collect_feeds(self) -> list[dict]:
        feeds = []
        for _category, feed_list in self.sources_config.get("rss_feeds", {}).items():
            feeds.extend(feed_list)
        # Sort high-priority feeds first so we get the best sources early
        priority_order = {"high": 0, "medium": 1, "low": 2}
        feeds.sort(key=lambda f: priority_order.get(f.get("priority", "medium"), 1))
        return feeds

    def _fetch_rss(self, url: str, source_name: str) -> list[Article]:
        feed = feedparser.parse(url, request_headers={"User-Agent": "LinkedInPostBot/1.0"})
        articles = []
        for entry in feed.entries:
            published = self._parse_date(entry)
            summary = _strip_html(entry.get("summary", entry.get("description", "")))
            article = Article(
                title=_strip_html(entry.get("title", "")),
                url=entry.get("link", ""),
                summary=summary[:800],
                published=published,
                source_name=source_name,
            )
            articles.append(article)
        return articles

    def _parse_date(self, entry) -> Optional[datetime]:
        for attr in ("published_parsed", "updated_parsed"):
            val = getattr(entry, attr, None)
            if val:
                try:
                    return datetime.fromtimestamp(time.mktime(val), tz=timezone.utc)
                except (OverflowError, OSError):
                    pass
        return None

    def _filter_by_freshness(self, articles: list[Article]) -> list[Article]:
        cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=self.max_age_hours)
        return [a for a in articles if a.published and a.published >= cutoff]

    def _score_articles(self, articles: list[Article]) -> list[Article]:
        # Build flat list: (keyword_lower, company_name)
        company_keywords: list[tuple[str, str]] = []
        for group in self.topics_config.get("companies_to_track", {}).values():
            for company in group:
                for kw in company.get("keywords", []):
                    company_keywords.append((kw.lower(), company["name"]))

        categories = self.topics_config.get("topic_categories", [])

        for article in articles:
            text = f"{article.title} {article.summary}".lower()
            score = 0

            for keyword, company_name in company_keywords:
                if keyword in text:
                    score += 3
                    if company_name not in article.matched_companies:
                        article.matched_companies.append(company_name)
                    if keyword not in article.matched_keywords:
                        article.matched_keywords.append(keyword)

            for cat in categories:
                for kw in cat.get("keywords", []):
                    if kw.lower() in text:
                        score += 1
                        if cat["name"] not in article.matched_categories:
                            article.matched_categories.append(cat["name"])

            article.relevance_score = score

        return articles

    def _deduplicate(self, articles: list[Article]) -> list[Article]:
        seen_titles: set[str] = set()
        seen_urls: set[str] = set()
        unique: list[Article] = []
        for article in articles:
            title_key = re.sub(r"\W+", "", article.title.lower())[:60]
            if title_key in seen_titles or article.url in seen_urls:
                continue
            seen_titles.add(title_key)
            if article.url:
                seen_urls.add(article.url)
            unique.append(article)
        return unique

    def _fetch_newsapi(self) -> list[Article]:
        import os

        api_key = os.getenv("NEWSAPI_KEY")
        if not api_key:
            print("  [skip] NewsAPI: NEWSAPI_KEY not set in .env")
            return []

        articles: list[Article] = []
        api_config = self.sources_config["optional_apis"]["newsapi"]
        queries = api_config.get("queries", [])
        max_per_query = api_config.get("max_results_per_query", 20)

        for endpoint in queries:
            try:
                resp = requests.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": endpoint["query"],
                        "sortBy": endpoint.get("sort_by", "publishedAt"),
                        "language": endpoint.get("language", "en"),
                        "apiKey": api_key,
                        "pageSize": max_per_query,
                    },
                    timeout=10,
                )
                for item in resp.json().get("articles", []):
                    if not item.get("url") or item["url"] == "[Removed]":
                        continue
                    published = None
                    if item.get("publishedAt"):
                        published = datetime.fromisoformat(
                            item["publishedAt"].replace("Z", "+00:00")
                        )
                    articles.append(
                        Article(
                            title=item.get("title", ""),
                            url=item["url"],
                            summary=item.get("description", ""),
                            published=published,
                            source_name=item.get("source", {}).get("name", "NewsAPI"),
                        )
                    )
            except Exception as exc:
                print(f"  [skip] NewsAPI query failed: {exc}")

        return articles


# ── Utility ────────────────────────────────────────────────────────────────────

def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()
