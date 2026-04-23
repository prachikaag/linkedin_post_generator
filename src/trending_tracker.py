"""
Trending tracker: pulls Google Trends data for AI-related keywords
and returns the most relevant trending terms.
"""

import time
from pathlib import Path

import yaml


def _load_topics() -> dict:
    config_path = Path(__file__).parent.parent / "config" / "topics.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def _build_seed_keywords(topics: dict) -> list[str]:
    keywords = []
    for company in topics.get("ai_companies", []):
        keywords.extend(company.get("keywords", [])[:2])
    for cat in topics.get("categories", []):
        keywords.extend(cat.get("keywords", [])[:2])
    keywords.extend(topics.get("priority_keywords", [])[:5])
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for kw in keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            unique.append(kw)
    return unique[:20]


def fetch_google_trends(keywords: list[str], timeframe: str = "now 7-d") -> dict[str, int]:
    """
    Returns {keyword: interest_score} using pytrends.
    Falls back to empty dict if pytrends is unavailable or rate-limited.
    """
    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("  [warn] pytrends not installed — skipping Google Trends")
        return {}

    results: dict[str, int] = {}
    # pytrends supports max 5 keywords per request
    chunks = [keywords[i:i + 5] for i in range(0, len(keywords), 5)]

    for chunk in chunks:
        try:
            pt = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
            pt.build_payload(chunk, timeframe=timeframe, geo="")
            df = pt.interest_over_time()
            if df.empty:
                continue
            for kw in chunk:
                if kw in df.columns:
                    results[kw] = int(df[kw].mean())
            time.sleep(1)  # avoid rate limiting
        except Exception as e:
            print(f"  [warn] Google Trends error for {chunk}: {e}")
            time.sleep(2)

    return results


def fetch_related_queries(keyword: str) -> list[str]:
    """Returns list of related rising queries for a keyword."""
    try:
        from pytrends.request import TrendReq
        pt = TrendReq(hl="en-US", tz=0, timeout=(10, 25))
        pt.build_payload([keyword], timeframe="now 7-d", geo="")
        related = pt.related_queries()
        rising = related.get(keyword, {}).get("rising")
        if rising is not None and not rising.empty:
            return rising["query"].tolist()[:10]
    except Exception:
        pass
    return []


def get_trending_keywords(top_n: int = 15) -> list[dict]:
    """
    Returns a ranked list of trending AI keywords with their interest scores.
    Format: [{"keyword": str, "score": int, "rising_queries": list[str]}]
    """
    topics = _load_topics()
    seeds = _build_seed_keywords(topics)

    print(f"  Checking Google Trends for {len(seeds)} seed keywords...")
    scores = fetch_google_trends(seeds)

    if not scores:
        # Fallback: return seeds with equal weight if Trends unavailable
        print("  Using fallback keyword list (no trend data)")
        return [{"keyword": kw, "score": 50, "rising_queries": []} for kw in seeds[:top_n]]

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top = ranked[:top_n]

    result = []
    for kw, score in top:
        if score > 10:  # filter out zero-interest keywords
            result.append({
                "keyword": kw,
                "score": score,
                "rising_queries": [],  # skip extra API call unless needed
            })

    return result


def summarise_trends(trending: list[dict]) -> str:
    """Returns a short prose summary of trending keywords for use in the prompt."""
    if not trending:
        return "No trend data available."
    top_kws = [f"{t['keyword']} (score: {t['score']})" for t in trending[:8]]
    return "Trending AI keywords right now: " + ", ".join(top_kws) + "."
