import json
import re
import shutil
import subprocess
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    content_lines = [l for l in lines if not l.strip().startswith("#")]
    return "\n".join(content_lines).strip()


class TrendingTracker:
    """Fetches trending AI topics via Claude WebSearch MCP, with pytrends fallback."""

    def __init__(self, topics_config: dict):
        self.topics_config = topics_config
        trend_cfg = topics_config.get("trending_keywords", {})
        self.seed_terms: list[str] = trend_cfg.get("seed_terms", ["artificial intelligence"])
        self.geo: str = trend_cfg.get("geo", "US")
        self.timeframe: str = trend_cfg.get("timeframe", "now 7-d")

    def get_trending_keywords(self) -> list[str]:
        """Return a deduplicated list of trending keywords, falling back gracefully."""
        # Primary: Claude WebSearch MCP
        if shutil.which("claude"):
            keywords = self._fetch_via_claude_websearch()
            if keywords:
                return _deduplicate(keywords)[:20]

        # Secondary: pytrends (requires local internet access + package)
        keywords = self._fetch_via_pytrends()
        if keywords:
            return _deduplicate(keywords)[:20]

        # Final fallback: seed terms from config
        return self.seed_terms[:10]

    # ── Claude WebSearch MCP path ──────────────────────────────────────────────

    def _fetch_via_claude_websearch(self) -> list[str]:
        seeds_str = ", ".join(self.seed_terms[:8])
        prompt = _load_prompt("trending_search.txt").replace("{{seed_terms}}", seeds_str)

        result = subprocess.run(
            [
                "claude", "-p",
                "--model", "haiku",
                "--tools", "WebSearch",
                "--no-session-persistence",
            ],
            input=prompt,
            capture_output=True,
            text=True,
            cwd="/tmp",
            timeout=90,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return []

        raw = result.stdout.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)
        raw = raw.strip()

        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            return []

        try:
            keywords = json.loads(match.group(0))
            return [k for k in keywords if isinstance(k, str)][:20]
        except (json.JSONDecodeError, TypeError):
            return []

    # ── pytrends fallback ──────────────────────────────────────────────────────

    def _fetch_via_pytrends(self) -> list[str]:
        try:
            import time
            from pytrends.request import TrendReq
        except ImportError:
            return []

        results: list[str] = []
        try:
            pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 15))
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
                    time.sleep(1)
                except Exception as exc:
                    print(f"  [skip] Trends batch {batch}: {exc}")
                    results.extend(batch)
        except Exception as exc:
            print(f"  [skip] Google Trends unavailable: {exc}")
            return self.seed_terms[:5]

        return results


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
