"""
trending_tracker.py
Finds the most-discussed AI keywords from the past 7 days.

Primary source: Google Trends via pytrends (no API key required).
Fallback: returns the seed terms from config/topics.yaml so the pipeline
          never blocks even if Google Trends is unavailable.

To change the seed terms or geography: edit config/topics.yaml →
  trending_keywords.seed_terms and trending_keywords.geo
"""
import random
import time


def get_trending_keywords(config: dict) -> list[str]:
    """Return 10–20 trending AI keyword phrases."""
    topics = config["topics"]
    trend_cfg = topics.get("trending_keywords", {})
    seed_terms = trend_cfg.get("seed_terms", _DEFAULT_SEEDS)
    geo = trend_cfg.get("geo", "US")
    timeframe = trend_cfg.get("timeframe", "now 7-d")

    try:
        phrases = _fetch_google_trends(seed_terms, geo, timeframe)
        if phrases:
            return phrases
    except Exception:
        pass

    return _fallback_keywords(topics)


# ── Google Trends ─────────────────────────────────────────────────────────────

def _fetch_google_trends(seed_terms: list[str], geo: str, timeframe: str) -> list[str]:
    """
    Query Google Trends for related/rising queries for each seed term.
    Limits to 3 seed terms per run to avoid rate-limiting.
    """
    from pytrends.request import TrendReq  # lazy import — optional dependency

    pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 30))
    all_phrases: list[str] = []

    for term in seed_terms[:3]:
        try:
            pytrends.build_payload([term], timeframe=timeframe, geo=geo)
            related = pytrends.related_queries()
            if related and term in related:
                top = related[term].get("top")
                if top is not None and not top.empty:
                    all_phrases.extend(top["query"].tolist()[:6])
                rising = related[term].get("rising")
                if rising is not None and not rising.empty:
                    all_phrases.extend(rising["query"].tolist()[:4])
            time.sleep(random.uniform(1.5, 3.0))  # polite rate limiting
        except Exception:
            continue

    return _dedupe(all_phrases)[:20]


# ── Fallback ──────────────────────────────────────────────────────────────────

def _fallback_keywords(topics: dict) -> list[str]:
    """
    When Google Trends is unavailable, build a keyword list from
    company names and topic categories in topics.yaml.
    This is always safe — no external calls.
    """
    keywords: list[str] = []
    for group in topics.get("companies_to_track", {}).values():
        for company in group:
            keywords.append(company["name"])
    for cat in topics.get("topic_categories", []):
        keywords.append(cat["name"])
    return _dedupe(keywords)[:20]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if isinstance(item, str) and item.lower() not in seen:
            seen.add(item.lower())
            result.append(item)
    return result


_DEFAULT_SEEDS = [
    "artificial intelligence",
    "ChatGPT",
    "AI tools",
    "generative AI",
    "AI agent",
]
