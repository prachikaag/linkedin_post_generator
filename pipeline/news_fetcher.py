"""
Fetch articles from RSS/Atom feeds using only stdlib.

Dependencies: none beyond Python stdlib + PyYAML

Namespace prefixes handled for RSS 2.0, Atom 1.0, and YouTube feeds.
"""

import re
import time
import logging
import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from typing import Optional

logger = logging.getLogger(__name__)

# XML namespaces used in Atom / YouTube feeds
_NS = {
    "atom":    "http://www.w3.org/2005/Atom",
    "media":   "http://search.yahoo.com/mrss/",
    "yt":      "http://www.youtube.com/xml/schemas/2015",
    "content": "http://purl.org/rss/1.0/modules/content/",
}

_HEADERS = {"User-Agent": "LinkedInPostGenerator/1.0 (github.com/prachikaag/linkedin_post_generator)"}


def fetch_feeds(sources_config: dict, max_age_hours: int = 48) -> list[dict]:
    """
    Fetch all enabled RSS/Atom feeds and return a deduplicated article list.
    Articles older than max_age_hours are discarded.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)

    # Collect and sort feeds by priority
    all_feeds: list[dict] = []
    for feeds in sources_config.get("rss_feeds", {}).values():
        if isinstance(feeds, list):
            for feed in feeds:
                if feed.get("enabled", True):
                    all_feeds.append(feed)

    _priority = {"high": 0, "medium": 1, "low": 2}
    all_feeds.sort(key=lambda f: _priority.get(f.get("priority", "low"), 2))

    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    articles: list[dict] = []

    for batch_start in range(0, len(all_feeds), 8):
        batch = all_feeds[batch_start : batch_start + 8]
        for feed in batch:
            try:
                raw = _get_feed(feed["url"])
                for article in _parse_feed(raw, feed["name"], cutoff):
                    url = article["url"]
                    norm = _norm_title(article["title"])
                    if url in seen_urls or norm in seen_titles:
                        continue
                    seen_urls.add(url)
                    seen_titles.add(norm)
                    articles.append(article)
            except Exception as exc:
                logger.warning("Feed %s failed: %s", feed.get("name"), exc)

        if batch_start + 8 < len(all_feeds):
            time.sleep(0.3)

    return articles


# ── HTTP ───────────────────────────────────────────────────────────────────

def _get_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()


# ── XML parsing ────────────────────────────────────────────────────────────

def _parse_feed(content: bytes, source_name: str, cutoff: datetime) -> list[dict]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        logger.warning("XML parse error in %s: %s", source_name, exc)
        return []

    tag = root.tag.lower()

    if "rss" in tag or root.find("channel") is not None:
        return _parse_rss(root, source_name, cutoff)
    else:
        # Atom feed (root tag is <feed>)
        return _parse_atom(root, source_name, cutoff)


def _parse_rss(root: ET.Element, source_name: str, cutoff: datetime) -> list[dict]:
    articles = []
    channel = root.find("channel")
    if channel is None:
        channel = root

    for item in channel.findall("item"):
        title = _text(item, "title")
        if not title:
            continue

        url = _text(item, "link") or ""
        if not url:
            # Try guid with isPermaLink
            guid = item.find("guid")
            if guid is not None and guid.get("isPermaLink", "true").lower() != "false":
                url = guid.text or ""

        if not url:
            continue

        published = _parse_date(
            _text(item, "pubDate") or _text(item, "dc:date") or ""
        )
        if published is None or published < cutoff:
            continue

        summary = _strip_html(
            _text(item, "description") or
            _text(item, "{http://purl.org/rss/1.0/modules/content/}encoded") or ""
        )[:800]

        articles.append(_article(title, url, summary, published, source_name))

    return articles


def _parse_atom(root: ET.Element, source_name: str, cutoff: datetime) -> list[dict]:
    articles = []
    ns = _detect_ns(root)

    for entry in root.findall(f"{ns}entry"):
        title_el = entry.find(f"{ns}title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        if not title:
            continue

        # link: prefer rel=alternate, else first href
        url = ""
        for link in entry.findall(f"{ns}link"):
            rel = link.get("rel", "alternate")
            href = link.get("href", "")
            if rel == "alternate" and href:
                url = href
                break
            elif href and not url:
                url = href
        if not url:
            continue

        pub_text = (
            _elem_text(entry.find(f"{ns}published")) or
            _elem_text(entry.find(f"{ns}updated")) or ""
        )
        published = _parse_date(pub_text)
        if published is None or published < cutoff:
            continue

        summary = _strip_html(
            _elem_text(entry.find(f"{ns}summary")) or
            _elem_text(entry.find(f"{ns}content")) or
            # YouTube: media:group/media:description
            _elem_text(entry.find(".//media:description", _NS)) or ""
        )[:800]

        articles.append(_article(title, url, summary, published, source_name))

    return articles


# ── Helpers ────────────────────────────────────────────────────────────────

def _article(title, url, summary, published, source_name) -> dict:
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "published": published.isoformat(),
        "source_name": source_name,
        "relevance_score": 0,
        "matched_companies": [],
        "matched_categories": [],
        "matched_keywords": [],
    }


def _detect_ns(root: ET.Element) -> str:
    """Return the namespace prefix string (e.g. '{http://...}') or ''."""
    tag = root.tag
    if tag.startswith("{"):
        return "{" + tag[1:tag.index("}")] + "}"
    return ""


def _text(elem: ET.Element, tag: str) -> str:
    child = elem.find(tag)
    return (child.text or "").strip() if child is not None else ""


def _elem_text(elem: Optional[ET.Element]) -> str:
    if elem is None:
        return ""
    return (elem.text or "").strip()


def _parse_date(s: str) -> Optional[datetime]:
    if not s:
        return None
    s = s.strip()
    # Try RFC 2822 (RSS pubDate)
    try:
        return parsedate_to_datetime(s)
    except Exception:
        pass
    # Try ISO 8601 (Atom published)
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s[:25], fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())[:60]
