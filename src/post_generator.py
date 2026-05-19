import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
import yaml

from .news_gatherer import Article

BASE_DIR = Path(__file__).parent.parent

_SYSTEM_TEMPLATE = """\
You are a LinkedIn ghostwriter for {author_name}, {author_title}.

## About {author_name}
{author_tagline}

## What {author_name} writes about
{focus_areas}

## Tone of Voice
{tone_traits}

## Writing Style Rules (follow every one strictly)
{writing_style}

## Post Blueprint (follow this structure in order)
{post_structure}

## Absolute Do's
{dos}

## Absolute Don'ts
{donts}

## Research & Citation Standards (non-negotiable)
- Cite a minimum of {min_sources} distinct sources in every post — no exceptions
- Synthesise across ALL provided sources — do NOT summarise just one article
- All sources appear at the end under a "Sources:" heading, one per line:
    [N]. [Short descriptive title] → [full URL]
- For any direct verbatim quote: "[exact quote]" — Full Name, Job Title, Company
  If you cannot confirm a quote is exact, paraphrase instead — no quote marks

## CRITICAL URL RULE (zero exceptions)
- ONLY use URLs copied character-for-character from the "URL:" fields of the supplied sources
- NEVER construct, guess, modify, shorten, or recall any URL from training data
- If a source has no URL, write: [URL not provided — verify before publishing]

## Hashtag Rules
- Always include: {always_hashtags}
- Choose from the rotation list to reach exactly {max_hashtags} total: {rotate_hashtags}
- Place all hashtags on the very last line of the post

## Hard Limits
- Maximum {max_characters} characters and {max_words} words (post body, excluding sources)
- Every sentence must be 15 words or fewer
- Short paragraphs — 1 to 3 sentences max

## Words to Never Use
- "shipped" → say "launched", "released", or "announced"
- "AI lab" → use the company name directly
- "game-changer", "revolutionary", "disruptive" (without specifics)
- "leveraged", "utilised", "synergy", "thought leader"

## Output
Output ONLY the LinkedIn post text — no preamble, no label, no commentary.
Write as {author_name} in first person.
"""


class PostGenerator:
    """
    Generates LinkedIn posts from article clusters.

    Generation order:
      1. Anthropic API via requests (if ANTHROPIC_API_KEY is set)
      2. Claude CLI subprocess (if `claude` binary is on PATH)
    """

    def __init__(self, brand_kit: dict, posts_dir: Path, model: str = "claude-sonnet-4-6"):
        self.brand_kit = brand_kit
        self.posts_dir = posts_dir
        self.posts_dir.mkdir(exist_ok=True)
        self.model = model
        research = brand_kit.get("research_standards", {})
        self.min_sources = research.get("min_sources", 4)
        self._system_prompt = self._build_system_prompt()

    # ── Public API ─────────────────────────────────────────────────────────────

    def generate_post(
        self, articles: list[Article], trending_keywords: list[str]
    ) -> Optional[dict]:
        if not articles:
            return None

        user_prompt = self._build_user_prompt(articles, trending_keywords)
        raw = self._call_claude(user_prompt)
        if not raw:
            return None

        content = _strip_preamble(raw)
        return self._save_post(articles, content, trending_keywords)

    # ── Prompt construction ────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        author = self.brand_kit.get("author", {})
        tone = self.brand_kit.get("tone_of_voice", {})
        brand = self.brand_kit.get("brand", {})
        hashtags = brand.get("hashtags", {})
        research = self.brand_kit.get("research_standards", {})

        def bl(items: list) -> str:
            return "\n".join(f"- {i}" for i in items)

        def nl(items: list) -> str:
            return "\n".join(f"{n}. {i}" for n, i in enumerate(items, 1))

        return _SYSTEM_TEMPLATE.format(
            author_name=author.get("name", "the author"),
            author_title=author.get("title", ""),
            author_tagline=author.get("tagline", ""),
            focus_areas=bl(brand.get("focus_areas", [])),
            tone_traits=bl(tone.get("primary_traits", [])),
            writing_style=bl(tone.get("writing_style", [])),
            post_structure=nl(tone.get("post_structure", [])),
            dos=bl(tone.get("dos", [])),
            donts=bl(tone.get("donts", [])),
            min_sources=research.get("min_sources", 4),
            always_hashtags=" ".join(hashtags.get("always_include", [])),
            max_hashtags=brand.get("max_hashtags", 5),
            rotate_hashtags=" ".join(hashtags.get("rotate_from", [])),
            max_characters=brand.get("max_characters", 1457),
            max_words=brand.get("max_words", 251),
        )

    def _build_user_prompt(
        self, articles: list[Article], trending_keywords: list[str]
    ) -> str:
        sources_block = ""
        for i, a in enumerate(articles, 1):
            pub = a.published.strftime("%B %d, %Y") if a.published else "recent"
            label = " ← PRIMARY ANCHOR" if i == 1 else ""
            sources_block += f"\n### Source {i}{label}\n"
            sources_block += f"Publication: {a.source_name}\n"
            sources_block += f"Title: {a.title}\n"
            sources_block += f"URL: {a.url}\n"
            sources_block += f"Date: {pub}\n"
            sources_block += f"Summary: {(a.summary or 'N/A')[:600]}\n"

        companies = sorted({c for a in articles for c in a.matched_companies})
        categories = sorted({c for a in articles for c in a.matched_categories})
        trending_str = (
            ", ".join(trending_keywords[:10]) if trending_keywords else "AI, generative AI"
        )

        return (
            f"Write a LinkedIn post synthesising ALL {len(articles)} of the following sources.\n\n"
            f"Source 1 is the primary anchor story. Sources 2–{len(articles)} add context and depth.\n\n"
            f"HARD REQUIREMENT: Cite all sources. Minimum {self.min_sources} — never fewer.\n\n"
            "⚠️ URL RULE: Copy every URL character-for-character from the \"URL:\" fields below.\n"
            "Do NOT construct, modify, or recall any URL. Missing URL → write [URL not provided].\n\n"
            f"## Source Material\n{sources_block}\n"
            f"## Context\n"
            f"Companies: {', '.join(companies) or 'General AI news'}\n"
            f"Categories: {', '.join(categories) or 'AI news'}\n"
            f"Trending topics — weave in 2–3 naturally: {trending_str}\n\n"
            "## Writing Instructions\n"
            "- Synthesise across all sources — do NOT just paraphrase Source 1\n"
            "- Add your genuine perspective on what this means for brands and marketers\n"
            "- For launches/features: explain the practical implication for a marketing team\n"
            "- For funding: explain what the investment signals about the AI landscape\n"
            "- End with a specific question that invites genuine discussion in comments\n"
            "- List all sources at the bottom under \"Sources:\" with full URLs from above\n"
        )

    # ── Claude invocation ──────────────────────────────────────────────────────

    def _call_claude(self, user_prompt: str) -> Optional[str]:
        # 1. Direct Anthropic API via HTTP (preferred when API key is available)
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if api_key:
            result = self._call_via_api(api_key, user_prompt)
            if result:
                return result
            print("  [warn] Anthropic API failed — trying Claude CLI")

        # 2. Claude CLI subprocess (works in Claude Code environments without an API key)
        if shutil.which("claude"):
            return self._call_via_cli(user_prompt)

        print(
            "  [error] No Claude access found.\n"
            "          → In Claude Code: run `python main.py` from the terminal.\n"
            "          → Locally: add ANTHROPIC_API_KEY to your .env file."
        )
        return None

    def _call_via_api(self, api_key: str, user_prompt: str) -> Optional[str]:
        """Direct HTTP call to Anthropic API — no SDK required."""
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                    "anthropic-beta": "prompt-caching-2024-07-31",
                },
                json={
                    "model": self.model,
                    "max_tokens": 1800,
                    "system": [
                        {
                            "type": "text",
                            "text": self._system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    "messages": [{"role": "user", "content": user_prompt}],
                },
                timeout=120,
            )
            if resp.status_code == 401:
                print("  [error] Invalid ANTHROPIC_API_KEY — check your .env file")
                return None
            if resp.status_code == 429:
                print("  [error] Claude API rate limit — wait a moment and retry")
                return None
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"].strip()
        except requests.exceptions.Timeout:
            print("  [warn] Anthropic API timed out")
        except Exception as exc:
            print(f"  [warn] Anthropic API: {exc}")
        return None

    def _call_via_cli(self, user_prompt: str) -> Optional[str]:
        """Call Claude via CLI subprocess — works in Claude Code managed environments."""
        try:
            payload = json.dumps(
                {
                    "system": self._system_prompt,
                    "prompt": user_prompt,
                    "model": self.model,
                }
            )
            result = subprocess.run(
                [
                    "claude", "-p",
                    "--model", self.model,
                    "--no-session-persistence",
                ],
                input=user_prompt,
                capture_output=True,
                text=True,
                timeout=180,
                cwd="/tmp",
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            if result.stderr:
                print(f"  [warn] Claude CLI: {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print("  [warn] Claude CLI timed out")
        except Exception as exc:
            print(f"  [warn] Claude CLI: {exc}")
        return None

    # ── Persistence ────────────────────────────────────────────────────────────

    def _save_post(
        self,
        articles: list[Article],
        content: str,
        trending_keywords: list[str],
    ) -> dict:
        primary = articles[0]
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        slug = re.sub(r"[^\w\s-]", "", primary.title.lower())[:40].strip()
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")
        filename = f"{timestamp}_{slug}.md"

        all_companies = sorted({c for a in articles for c in a.matched_companies})
        all_categories = sorted({c for a in articles for c in a.matched_categories})

        frontmatter = {
            "title": primary.title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "primary_source_url": primary.url,
            "primary_source_name": primary.source_name,
            "all_sources": [
                {"title": a.title, "url": a.url, "publication": a.source_name}
                for a in articles
            ],
            "source_count": len(articles),
            "trending_keywords": trending_keywords[:5],
            "matched_companies": all_companies,
            "matched_categories": all_categories,
            "relevance_score": primary.relevance_score,
            "status": "draft",
            "model": self.model,
        }

        file_content = (
            "---\n"
            + yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
            + "---\n\n"
            + content
            + "\n"
        )

        filepath = self.posts_dir / filename
        filepath.write_text(file_content, encoding="utf-8")

        return {
            "filename": filename,
            "filepath": str(filepath),
            "content": content,
            "article_title": primary.title,
            "source_url": primary.url,
            "source_name": primary.source_name,
            "source_count": len(articles),
        }


# ── Helpers ────────────────────────────────────────────────────────────────────

def _strip_preamble(content: str) -> str:
    """Remove any explanatory text Claude emits before the actual post body."""
    if "\n---\n" in content:
        parts = content.split("\n---\n", 1)
        candidate = parts[1].strip()
        if len(candidate) > 100:
            return candidate
    return content
