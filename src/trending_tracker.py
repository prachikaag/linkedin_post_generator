"""
Discovers trending AI keyword phrases from the past 7 days.

Primary method  : Google Trends via pytrends (install: pip install pytrends).
Fallback method : Returns seed terms from config/topics.yaml.

The pipeline always has keywords to work with — pytrends is optional.
"""

import time
from typing import List

import yaml


class TrendingTracker:
    def __init__(self, topics_path: str = "config/topics.yaml"):
        self.topics = self._load_yaml(topics_path)

    def _load_yaml(self, path: str) -> dict:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _fetch_via_pytrends(
        self, seed_terms: List[str], geo: str, timeframe: str
    ) -> List[str]:
        from pytrends.request import TrendReq  # type: ignore

        pt = TrendReq(hl="en-US", tz=360, timeout=(10, 30))
        trending: List[str] = []

        # pytrends accepts at most 5 keywords per payload
        for i in range(0, min(len(seed_terms), 15), 5):
            batch = seed_terms[i : i + 5]
            try:
                pt.build_payload(batch, timeframe=timeframe, geo=geo)
                related = pt.related_queries()
                for term in batch:
                    if term not in related:
                        continue
                    top_df = related[term].get("top")
                    if top_df is None or top_df.empty:
                        continue
                    for _, row in top_df.head(5).iterrows():
                        kw = str(row["query"]).strip()
                        if kw and len(kw) > 3:
                            trending.append(kw)
                time.sleep(1)  # respect Google Trends rate limits
            except Exception:
                continue

        # Deduplicate while preserving order
        seen: set = set()
        unique: List[str] = []
        for kw in trending:
            norm = kw.lower()
            if norm not in seen:
                seen.add(norm)
                unique.append(kw)
        return unique

    def fetch(self, verbose: bool = True) -> List[str]:
        config = self.topics.get("trending_keywords", {})
        seed_terms: List[str] = config.get(
            "seed_terms",
            ["artificial intelligence", "ChatGPT", "AI tools", "generative AI"],
        )
        geo: str = config.get("geo", "US")
        timeframe: str = config.get("timeframe", "now 7-d")

        try:
            keywords = self._fetch_via_pytrends(seed_terms, geo, timeframe)
            if keywords:
                return keywords[:20]
            if verbose:
                print("    Google Trends returned no data — using seed terms as fallback.")
        except ImportError:
            if verbose:
                print("    pytrends not installed — using seed terms as fallback.")
                print("    To enable: pip install pytrends")
        except Exception as exc:
            if verbose:
                print(f"    Google Trends error ({exc}) — using seed terms.")

        return seed_terms[:15]
