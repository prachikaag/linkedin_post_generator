import json
import re
import shutil
import subprocess
import time


class TrendingTracker:
    """
    Discovers trending AI topics via Claude WebSearch, with a seed-term fallback.

    Primary path  : calls `claude` CLI with --tools WebSearch (available in Claude Code)
    Fallback path : returns seed terms from config/topics.yaml
    """

    def __init__(self, topics_config: dict):
        trend_cfg = topics_config.get("trending_keywords", {})
        self.seed_terms: list[str] = trend_cfg.get(
            "seed_terms",
            ["artificial intelligence", "ChatGPT", "AI tools", "generative AI"],
        )
        self.geo: str = trend_cfg.get("geo", "US")

    def get_trending_keywords(self) -> list[str]:
        keywords: list[str] = []

        if shutil.which("claude"):
            keywords = self._fetch_via_websearch()
            if len(keywords) < 5:
                print("  [info] WebSearch returned few results — augmenting with seed terms")

        # Always augment with seed terms to ensure we have enough keywords
        combined = keywords + [s for s in self.seed_terms if s not in keywords]
        return _deduplicate(combined)[:20]

    # ── Claude WebSearch path ──────────────────────────────────────────────────

    def _fetch_via_websearch(self) -> list[str]:
        seeds_str = ", ".join(self.seed_terms[:8])
        prompt = f"""Search the web for the most recent trending AI news topics from the past 7 days.

Focus on topics related to: {seeds_str}

Use WebSearch to find what's happening in AI right now — new model releases, \
funding announcements, product launches, research breakthroughs, regulation news.

Return ONLY a JSON array of 15–20 trending keyword phrases (2–5 words each).
Format: ["keyword phrase 1", "keyword phrase 2", ...]
Return ONLY the raw JSON array starting with [ — no markdown, no explanation.
"""

        try:
            result = subprocess.run(
                [
                    "claude", "-p",
                    "--model", "claude-haiku-4-5",
                    "--tools", "WebSearch",
                    "--no-session-persistence",
                ],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=90,
                cwd="/tmp",
            )
        except subprocess.TimeoutExpired:
            print("  [skip] Trending search timed out")
            return []
        except Exception as exc:
            print(f"  [skip] Trending search: {exc}")
            return []

        if result.returncode != 0 or not result.stdout.strip():
            return []

        return _extract_json_array(result.stdout)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_json_array(text: str) -> list[str]:
    """Pull a JSON array of strings from Claude's raw output."""
    # Strip markdown fences if present
    text = re.sub(r"```[a-z]*\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\n?```", "", text)
    text = text.strip()

    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        return []

    try:
        items = json.loads(match.group(0))
        return [k for k in items if isinstance(k, str)]
    except (json.JSONDecodeError, TypeError):
        return []


def _deduplicate(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out
