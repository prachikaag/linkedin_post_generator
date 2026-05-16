"""Fetches trending AI keyword phrases via pytrends, with a curated fallback."""


class TrendingTracker:
    def __init__(self, topics_config: dict):
        trend_config = topics_config.get("trending_keywords", {})
        self.seed_terms = trend_config.get(
            "seed_terms",
            ["artificial intelligence", "ChatGPT", "AI tools", "generative AI", "AI agent"],
        )
        self.geo = trend_config.get("geo", "US")
        self.timeframe = trend_config.get("timeframe", "now 7-d")

    def get_trending_keywords(self) -> list[str]:
        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl="en-US", tz=360)
            trending_phrases: list[str] = []

            for i in range(0, min(len(self.seed_terms), 10), 5):
                batch = self.seed_terms[i : i + 5]
                try:
                    pytrends.build_payload(
                        batch, cat=0, timeframe=self.timeframe, geo=self.geo, gprop=""
                    )
                    related = pytrends.related_queries()
                    for term in batch:
                        rising = related.get(term, {}).get("rising")
                        if rising is not None and not rising.empty:
                            for _, row in rising.head(5).iterrows():
                                phrase = str(row["query"])
                                if len(phrase) > 5 and phrase not in trending_phrases:
                                    trending_phrases.append(phrase)
                except Exception:
                    continue

            if trending_phrases:
                return trending_phrases[:20]
        except Exception:
            pass

        return self._fallback_keywords()

    def _fallback_keywords(self) -> list[str]:
        return [
            "AI agent frameworks",
            "large language model capabilities",
            "generative AI enterprise adoption",
            "multimodal AI models",
            "AI startup funding 2025",
            "Claude AI features",
            "ChatGPT new update",
            "Gemini AI release",
            "AI marketing automation",
            "AI productivity tools",
            "neural network breakthroughs",
            "AI regulation policy",
            "open source AI models",
            "AI creative tools",
            "machine learning applications",
        ]
