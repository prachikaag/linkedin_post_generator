"""Fetches and scores articles from RSS feeds defined in config/sources.yaml."""
import re
import time
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field

import feedparser


@dataclass
class Article:
    title: str
    url: str
    summary: str
    published: datetime
    source_name: str
    relevance_score: int = 0
    matched_companies: list = field(default_factory=list)
    matched_categories: list = field(default_factory=list)
    matched_keywords: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "summary": self.summary[:800],
            "published": self.published.isoformat(),
            "source_name": self.source_name,
            "relevance_score": self.relevance_score,
            "matched_companies": self.matched_companies,
            "matched_categories": self.matched_categories,
            "matched_keywords": self.matched_keywords,
        }


class NewsGatherer:
    def __init__(self, sources_config: dict, topics_config: dict):
        self.sources = sources_config
        self.topics = topics_config
        freshness = topics_config.get("freshness", {})
        self.max_age_hours = freshness.get("max_article_age_hours", 48)
        self.min_score = freshness.get("min_relevance_score", 2)
        self.max_articles = freshness.get("max_articles_per_run", 25)

    def _clean_html(self, text: str) -> str:
        clean = re.sub(r"<[^>]+>", "", text or "")
        return " ".join(clean.split())

    def _get_all_feeds(self) -> list[dict]:
        priority_map = {"high": 0, "medium": 1, "low": 2}
        feeds = []
        for feed_list in self.sources.get("rss_feeds", {}).values():
            for feed in feed_list:
                if feed.get("enabled", True):
                    feeds.append({
                        "name": feed["name"],
                        "url": feed["url"],
                        "priority_val": priority_map.get(feed.get("priority", "medium"), 1),
                    })
        return sorted(feeds, key=lambda x: x["priority_val"])

    def _build_keyword_lists(self) -> tuple[list, list]:
        company_keywords = []
        category_keywords = []
        for company_list in self.topics.get("companies_to_track", {}).values():
            for company in company_list:
                if isinstance(company, dict):
                    company_keywords.append((
                        company.get("name", ""),
                        [kw.lower() for kw in company.get("keywords", [])],
                    ))
        for category in self.topics.get("topic_categories", []):
            category_keywords.append((
                category.get("name", ""),
                [kw.lower() for kw in category.get("keywords", [])],
            ))
        return company_keywords, category_keywords

    def _score_article(self, article: Article, company_keywords: list, category_keywords: list) -> None:
        text = f"{article.title} {article.summary}".lower()
        for company_name, keywords in company_keywords:
            for keyword in keywords:
                if keyword in text:
                    article.relevance_score += 3
                    if company_name not in article.matched_companies:
                        article.matched_companies.append(company_name)
                    if keyword not in article.matched_keywords:
                        article.matched_keywords.append(keyword)
        for category_name, keywords in category_keywords:
            for keyword in keywords:
                if keyword in text:
                    article.relevance_score += 1
                    if category_name not in article.matched_categories:
                        article.matched_categories.append(category_name)

    def _parse_published(self, entry) -> datetime | None:
        for attr in ("published_parsed", "updated_parsed"):
            time_struct = getattr(entry, attr, None)
            if time_struct:
                try:
                    return datetime.fromtimestamp(time.mktime(time_struct), tz=timezone.utc)
                except Exception:
                    continue
        return None

    def fetch_all(self) -> list[Article]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.max_age_hours)
        feeds = self._get_all_feeds()
        company_keywords, category_keywords = self._build_keyword_lists()
        seen_titles: set[str] = set()
        seen_urls: set[str] = set()
        articles: list[Article] = []

        for feed_info in feeds:
            try:
                parsed = feedparser.parse(feed_info["url"])
                for entry in parsed.entries:
                    url = getattr(entry, "link", None)
                    if not url or url in seen_urls:
                        continue

                    title = self._clean_html(getattr(entry, "title", ""))
                    if not title:
                        continue

                    normalized = re.sub(r"[^a-z0-9]", "", title.lower())[:60]
                    if normalized in seen_titles:
                        continue

                    published = self._parse_published(entry)
                    if not published or published < cutoff:
                        continue

                    summary = ""
                    for attr in ("summary", "description", "content"):
                        val = getattr(entry, attr, None)
                        if val:
                            if isinstance(val, list):
                                val = val[0].get("value", "") if val else ""
                            summary = self._clean_html(str(val))[:800]
                            break

                    article = Article(
                        title=title,
                        url=url,
                        summary=summary,
                        published=published,
                        source_name=feed_info["name"],
                    )
                    self._score_article(article, company_keywords, category_keywords)

                    if article.relevance_score >= self.min_score:
                        articles.append(article)
                        seen_titles.add(normalized)
                        seen_urls.add(url)
            except Exception:
                continue

        articles.sort(key=lambda a: a.relevance_score, reverse=True)
        return articles[: self.max_articles]
