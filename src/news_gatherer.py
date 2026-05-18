"""
Fetches AI news from RSS feeds listed in config/sources.yaml.
Scores each article by relevance using keywords in config/topics.yaml.
Returns deduplicated, ranked articles ready for post generation.

Uses only the standard library + requests (no feedparser dependency).
Parses RSS 2.0 (<item>) and Atom (<entry>) formats.
"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Dict, List, Optional

import requests
import yaml


# Atom namespace shorthand
_ATOM = "http://www.w3.org/2005/Atom"
_CONTENT = "http://purl.org/rss/1.0/modules/content/"

_REQUEST_TIMEOUT = 15  # seconds per feed


class NewsGatherer:
    def __init__(
        self,
        sources_path: str = "config/sources.yaml",
        topics_path: str = "config/topics.yaml",
    ):
        self.sources = self._load_yaml(sources_path)
        self.topics = self._load_yaml(topics_path)

    # ── Config loading ──────────────────────────────────────────────────────

    def _load_yaml(self, path: str) -> dict:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    # ── Text utilities ──────────────────────────────────────────────────────

    @staticmethod
    def _strip_html(text: str) -> str:
        return re.sub(r"<[^>]+>", "", text or "").strip()

    @staticmethod
    def _parse_rss_date(date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        # RFC 2822 format used by RSS (<pubDate>)
        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            pass
        # ISO 8601 format used by Atom (<published>/<updated>)
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    # ── RSS / Atom parsing ──────────────────────────────────────────────────

    def _parse_feed(self, xml_text: str, feed_name: str) -> List[Dict]:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        articles: List[Dict] = []

        # ── RSS 2.0 ──────────────────────────────────────────
        for item in root.iter("item"):
            title = self._strip_html(item.findtext("title", ""))
            link = item.findtext("link", "").strip()
            # Some feeds put the URL in <guid isPermaLink="true">
            if not link:
                guid = item.find("guid")
                if guid is not None and guid.get("isPermaLink", "true").lower() != "false":
                    link = (guid.text or "").strip()

            summary_raw = (
                item.findtext(f"{{{_CONTENT}}}encoded")
                or item.findtext("description")
                or ""
            )
            summary = self._strip_html(summary_raw)[:800]
            pub_date = self._parse_rss_date(item.findtext("pubDate", ""))

            if title and link:
                articles.append(
                    {
                        "title": title,
                        "url": link,
                        "summary": summary,
                        "published_dt": pub_date,
                        "source_name": feed_name,
                    }
                )

        # ── Atom ─────────────────────────────────────────────
        for entry in root.findall(f"{{{_ATOM}}}entry"):
            title_el = entry.find(f"{{{_ATOM}}}title")
            link_el = entry.find(f"{{{_ATOM}}}link")
            summary_el = entry.find(f"{{{_ATOM}}}summary") or entry.find(
                f"{{{_ATOM}}}content"
            )
            pub_el = entry.find(f"{{{_ATOM}}}published") or entry.find(
                f"{{{_ATOM}}}updated"
            )

            title = self._strip_html(title_el.text if title_el is not None else "")
            url = link_el.get("href", "") if link_el is not None else ""
            if not url and link_el is not None:
                url = (link_el.text or "").strip()
            summary = self._strip_html(
                summary_el.text if summary_el is not None else ""
            )[:800]
            pub_date = self._parse_rss_date(
                pub_el.text if pub_el is not None else ""
            )

            if title and url:
                articles.append(
                    {
                        "title": title,
                        "url": url,
                        "summary": summary,
                        "published_dt": pub_date,
                        "source_name": feed_name,
                    }
                )

        return articles

    # ── Relevance scoring ───────────────────────────────────────────────────

    def _score_article(self, title: str, summary: str) -> Dict:
        text = (title + " " + summary).lower()
        score = 0
        matched_companies: List[str] = []
        matched_keywords: List[str] = []
        matched_categories: List[str] = []

        for group in self.topics.get("companies_to_track", {}).values():
            for company in group:
                company_name = company.get("name", "")
                for kw in company.get("keywords", []):
                    if kw.lower() in text:
                        score += 3
                        if company_name not in matched_companies:
                            matched_companies.append(company_name)
                        if kw not in matched_keywords:
                            matched_keywords.append(kw)

        for category in self.topics.get("topic_categories", []):
            cat_name = category.get("name", "")
            for kw in category.get("keywords", []):
                if kw.lower() in text:
                    score += 1
                    if cat_name not in matched_categories:
                        matched_categories.append(cat_name)

        return {
            "score": score,
            "matched_companies": matched_companies,
            "matched_keywords": matched_keywords,
            "matched_categories": matched_categories,
        }

    # ── Feed collection ─────────────────────────────────────────────────────

    def _collect_feeds(self) -> List[Dict]:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        feeds = []
        for section in self.sources.get("rss_feeds", {}).values():
            for feed in section:
                if feed.get("enabled", True):
                    rank = priority_order.get(feed.get("priority", "low"), 2)
                    feeds.append((rank, feed))
        feeds.sort(key=lambda x: x[0])
        return [f for _, f in feeds]

    # ── Main fetch ──────────────────────────────────────────────────────────

    def fetch(self, verbose: bool = True) -> List[Dict]:
        freshness = self.topics.get("freshness", {})
        max_age_hours = freshness.get("max_article_age_hours", 48)
        min_score = freshness.get("min_relevance_score", 2)
        max_articles = freshness.get("max_articles_per_run", 25)

        cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=max_age_hours)
        feeds = self._collect_feeds()

        articles: List[Dict] = []
        seen_titles: set = set()
        seen_urls: set = set()

        headers = {
            "User-Agent": "LinkedInPostGenerator/1.0 (RSS reader; +https://github.com/prachikaag/linkedin_post_generator)"
        }

        for feed_cfg in feeds:
            feed_name = feed_cfg.get("name", feed_cfg["url"])
            try:
                resp = requests.get(
                    feed_cfg["url"], headers=headers, timeout=_REQUEST_TIMEOUT
                )
                resp.raise_for_status()
                raw_articles = self._parse_feed(resp.text, feed_name)
                feed_hits = 0

                for art in raw_articles:
                    pub_date = art.pop("published_dt", None)

                    # Freshness filter
                    if pub_date:
                        if pub_date.tzinfo is None:
                            pub_date = pub_date.replace(tzinfo=timezone.utc)
                        if pub_date < cutoff:
                            continue

                    title = art["title"]
                    url = art["url"]

                    # Deduplicate
                    norm = re.sub(r"[^a-z0-9]", "", title.lower())[:60]
                    if norm in seen_titles or url in seen_urls:
                        continue
                    seen_titles.add(norm)
                    seen_urls.add(url)

                    scored = self._score_article(title, art["summary"])
                    if scored["score"] < min_score:
                        continue

                    articles.append(
                        {
                            "title": title,
                            "url": url,
                            "summary": art["summary"],
                            "published": pub_date.isoformat() if pub_date else None,
                            "source_name": feed_name,
                            "relevance_score": scored["score"],
                            "matched_companies": scored["matched_companies"],
                            "matched_keywords": scored["matched_keywords"],
                            "matched_categories": scored["matched_categories"],
                        }
                    )
                    feed_hits += 1

                if verbose and feed_hits:
                    print(f"    {feed_name}: {feed_hits} article(s)")

            except Exception as exc:
                if verbose:
                    print(f"    [skip] {feed_name}: {exc}")

        articles.sort(key=lambda x: x["relevance_score"], reverse=True)
        return articles[:max_articles]
