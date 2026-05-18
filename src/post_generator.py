"""
Generates LinkedIn post drafts using the Anthropic Messages API.

Uses requests directly (no anthropic SDK required) so there are zero
extra dependencies beyond what's already installed.

The brand-kit system prompt is sent with cache_control: ephemeral so
repeated runs within the same session benefit from prompt caching.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests
import yaml

_ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_API_VERSION = "2023-06-01"
_BETA_HEADER = "prompt-caching-2024-07-31"
_REQUEST_TIMEOUT = 120  # seconds


class PostGenerator:
    def __init__(
        self,
        brand_kit_path: str = "config/brand_kit.yaml",
        posts_dir: str = "posts",
    ):
        self.brand_kit_path = brand_kit_path
        self.posts_dir = Path(posts_dir)
        self.posts_dir.mkdir(exist_ok=True)
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

        if not self.api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY is not set. "
                "Add it to your .env file or export it as an environment variable."
            )

    # ── Config ──────────────────────────────────────────────────────────────

    def _load_brand_kit(self) -> dict:
        with open(self.brand_kit_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    # ── Prompt construction ─────────────────────────────────────────────────

    def _build_system_prompt(self, kit: dict) -> str:
        author = kit.get("author", {})
        tov = kit.get("tone_of_voice", {})
        brand = kit.get("brand", {})
        standards = kit.get("research_standards", {})

        def bullets(items: List[str]) -> str:
            return "\n".join(f"- {item}" for item in items)

        def numbered(items: List[str]) -> str:
            return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))

        always_hashtags = " ".join(brand.get("hashtags", {}).get("always_include", []))
        rotate_hashtags = " ".join(brand.get("hashtags", {}).get("rotate_from", []))
        max_hashtags = brand.get("max_hashtags", 5)
        max_chars = brand.get("max_characters", 1457)
        max_words = brand.get("max_words", 251)
        min_sources = standards.get("min_sources", 4)

        return f"""You are writing LinkedIn posts for {author.get("name", "the author")}, {author.get("title", "")}.
Tagline: "{author.get("tagline", "")}"

## VOICE & PERSONALITY
{bullets(tov.get("primary_traits", []))}

## WRITING STYLE (follow every rule, no exceptions)
{bullets(tov.get("writing_style", []))}

## POST STRUCTURE (follow this exact order every time)
{numbered(tov.get("post_structure", []))}

## DOS
{bullets(tov.get("dos", []))}

## DON'TS
{bullets(tov.get("donts", []))}

## FOCUS AREAS
{bullets(brand.get("focus_areas", []))}

## HASHTAG RULES
- Always include: {always_hashtags}
- Pick additional tags from: {rotate_hashtags}
- Maximum {max_hashtags} total hashtags — place on the very last line

## HARD LIMITS
- Post body: max {max_chars} characters and {max_words} words
  (the sources list and hashtag line are excluded from this count)
- Every sentence: 15 words maximum — split anything longer into two sentences
- Minimum distinct sources to cite: {min_sources}

## URL RULE (zero exceptions)
Only use URLs that appear verbatim in the supplied article data.
Never construct, guess, shorten, or modify a URL — not even for well-known sites.
If you cannot confirm a URL came from the input, write:
  [URL not provided — verify before publishing]

## WORDS NEVER TO USE
"shipped", "AI lab", "programmed", "deployed" (except genuinely technical),
"leveraged", "utilised", "synergy", "thought leader",
"game-changer", "revolutionary", "disruptive" (without very specific evidence)"""

    def _build_user_prompt(self, articles: List[Dict], trending_keywords: List[str]) -> str:
        articles_json = json.dumps(articles, indent=2, default=str)
        keywords_str = ", ".join(trending_keywords[:15])

        return f"""Generate one LinkedIn post that synthesises all the articles below.
Weave in 2–3 of the trending keywords naturally — do not force them.

TRENDING KEYWORDS (pick 2–3)
{keywords_str}

ARTICLES TO SYNTHESISE
{articles_json}

Output the post body only.
No JSON, no frontmatter, no preamble or commentary before or after the post.
Follow the structure exactly:
  HOOK → CONTEXT → EVIDENCE → YOUR TAKE → SO WHAT → CTA
  [blank line]
  Sources (numbered, one per line)
  [blank line]
  Hashtags (on the very last line)"""

    # ── API call ────────────────────────────────────────────────────────────

    def _call_api(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": _ANTHROPIC_API_VERSION,
            "anthropic-beta": _BETA_HEADER,
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 2048,
            "system": [
                {
                    "type": "text",
                    "text": system_prompt,
                    # Cache the brand-kit system prompt — it rarely changes between runs
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            "messages": [{"role": "user", "content": user_prompt}],
        }
        resp = requests.post(
            _ANTHROPIC_API_URL, headers=headers, json=payload, timeout=_REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"].strip()

    # ── File handling ───────────────────────────────────────────────────────

    def _make_filename(self, primary_title: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        slug = re.sub(r"[^a-z0-9]+", "-", primary_title[:40].lower()).strip("-")
        return f"{timestamp}_{slug}.md"

    def _build_frontmatter(self, articles: List[Dict], trending_keywords: List[str]) -> str:
        primary = articles[0]

        all_companies: List[str] = []
        all_categories: List[str] = []
        for a in articles:
            all_companies.extend(a.get("matched_companies", []))
            all_categories.extend(a.get("matched_categories", []))

        def yaml_list(items: List[str], indent: int = 2) -> str:
            pad = " " * indent
            return (
                "\n".join(f"{pad}- {item}" for item in items)
                if items
                else f"{' ' * indent}[]"
            )

        q = lambda s: s.replace('"', "'")

        sources_block = "\n".join(
            f'  - title: "{q(a["title"])}"\n'
            f"    url: {a['url']}\n"
            f'    publication: "{a["source_name"]}"'
            for a in articles
        )

        return (
            "---\n"
            f'title: "{q(primary["title"])}"\n'
            f'date: "{datetime.now().strftime("%Y-%m-%d")}"\n'
            'status: "draft"\n'
            f"primary_source_url: {primary['url']}\n"
            f'primary_source_name: "{primary["source_name"]}"\n'
            "all_sources:\n"
            f"{sources_block}\n"
            f"source_count: {len(articles)}\n"
            "matched_companies:\n"
            f"{yaml_list(sorted(set(all_companies)))}\n"
            "matched_categories:\n"
            f"{yaml_list(sorted(set(all_categories)))}\n"
            "trending_keywords:\n"
            f"{yaml_list(trending_keywords[:5])}\n"
            f"relevance_score: {primary.get('relevance_score', 0)}\n"
            "---\n\n"
        )

    # ── Main generation ─────────────────────────────────────────────────────

    def generate(self, articles: List[Dict], trending_keywords: List[str]) -> Dict:
        """Generate one LinkedIn post from a cluster of articles and save it."""
        kit = self._load_brand_kit()
        system_prompt = self._build_system_prompt(kit)
        user_prompt = self._build_user_prompt(articles, trending_keywords)

        post_body = self._call_api(system_prompt, user_prompt)

        filename = self._make_filename(articles[0]["title"])
        filepath = self.posts_dir / filename
        frontmatter = self._build_frontmatter(articles, trending_keywords)
        filepath.write_text(frontmatter + post_body, encoding="utf-8")

        return {
            "filename": filename,
            "filepath": str(filepath),
            "content": post_body,
            "article_title": articles[0]["title"],
            "source_url": articles[0]["url"],
            "source_name": articles[0]["source_name"],
            "source_count": len(articles),
        }
