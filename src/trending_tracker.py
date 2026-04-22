import time
from typing import Optional


class TrendingTracker:
    """Fetches trending search queries related to AI topics via Google Trends."""

    def __init__(self, topics_config: dict):
        self.topics_config = topics_config
        trend_cfg = topics_config.get("trending_keywords", {})
        self.seed_terms: list[str] = trend_cfg.get("seed_terms", ["artificial intelligence"])
        self.geo: str = trend_cfg.get("geo", "US")
        self.timeframe: str = trend_cfg.get("timeframe", "now 7-d")

    def get_trending_keywords(self) -> list[str]:
        """Return a deduplicated list of trending keywords, falling back gracefully."""
        keywords: list[str] = []

        related = self._fetch_related_queries()
        keywords.extend(related)

        realtime = self._fetch_realtime_trending()
        keywords.extend(realtime)

        if not keywords:
            return self.seed_terms[:10]

        return _deduplicate(keywords)[:20]

    # ── Private helpers ────────────────────────────────────────────────────────

    def _fetch_related_queries(self) -> list[str]:
        try:
            from pytrends.request import TrendReq
        except ImportError:
            print("  [skip] pytrends not installed — skipping Google Trends")
            return []

        results: list[str] = []
        try:
            pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 15))
            # Google Trends accepts at most 5 terms per payload
            for i in range(0, len(self.seed_terms), 5):
                batch = self.seed_terms[i : i + 5]
                try:
                    pytrends.build_payload(
                        batch, cat=0, timeframe=self.timeframe, geo=self.geo
                    )
                    related = pytrends.related_queries()
                    for term in batch:
                        data = related.get(term, {})
                        top = data.get("top")
                        if top is not None and not top.empty:
                            results.extend(top["query"].tolist()[:5])
                    time.sleep(1)  # be polite to the Trends API
                except Exception as exc:
                    print(f"  [skip] Trends batch {batch}: {exc}")
                    results.extend(batch)
        except Exception as exc:
            print(f"  [skip] Google Trends unavailable: {exc}")
            return self.seed_terms[:5]

        return results

    def _fetch_realtime_trending(self) -> list[str]:
        try:
            from pytrends.request import TrendReq
        except ImportError:
            return []

        ai_markers = {"ai", "gpt", "claude", "gemini", "llm", "artificial", "openai", "chatbot"}
        try:
            pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 15))
            rt = pytrends.realtime_trending_searches(pn=self.geo)
            if rt.empty or "title" not in rt.columns:
                return []
            titles: list[str] = rt["title"].tolist()[:20]
            return [t for t in titles if any(m in t.lower() for m in ai_markers)][:5]
        except Exception:
            return []


# ── Utility ────────────────────────────────────────────────────────────────────

def _deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out
