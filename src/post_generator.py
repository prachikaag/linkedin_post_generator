import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from .news_gatherer import Article

# ── System prompt template ─────────────────────────────────────────────────────

_SYSTEM_TEMPLATE = """\
You are a LinkedIn ghostwriter for {author_name}, {author_title}.

## About {author_name}
{author_tagline}

## What {author_name} writes about
{focus_areas}

## Tone of Voice
{tone_traits}

## Writing Style Rules (follow these strictly)
{writing_style}

## Post Blueprint (follow this structure in order)
{post_structure}

## Absolute Do's
{dos}

## Absolute Don'ts
{donts}

## RESEARCH & CITATION STANDARDS (non-negotiable — enforced on every post)
- You MUST cite a minimum of {min_sources} distinct sources in every post, no exceptions
- Synthesise across all provided sources — do NOT summarise just one article
- All sources must appear at the end under a "Sources:" heading, one per line:
    [N]. [Short descriptive title] → [full URL]
- For any direct, verbatim quotes from a named person, you MUST attribute them as:
    "[exact quote]" — Full Name, Job Title, Company/Publication
  If you cannot confirm the quote is exact, paraphrase instead and do NOT use quote marks
- Every claim that came from a source must be traceable to one of the cited URLs
- The post must read like a researched commentary piece, not a reaction to a single article

## Hashtag Rules
- Always include: {always_hashtags}
- Choose from this rotation list to reach exactly {max_hashtags} total: {rotate_hashtags}
- Place all hashtags on the very last line of the post

## Output Rules
- Output ONLY the LinkedIn post text — no preamble, no "Here's the post:" label
- Target length: {post_length}
- Write as {author_name} in first person
- Make it sound like a real person who has done their homework, not a press release
"""


class PostGenerator:
    """Generates LinkedIn posts from article clusters using Claude CLI or Anthropic SDK."""

    def __init__(self, brand_kit: dict, posts_dir: Path):
        self.brand_kit = brand_kit
        self.posts_dir = posts_dir
        self.posts_dir.mkdir(exist_ok=True)
        research = brand_kit.get("research_standards", {})
        self.min_sources = research.get("min_sources", 4)
        self.model = os.getenv("ANTHROPIC_MODEL", "sonnet")
        self._system_prompt = self._build_system_prompt()

    def generate_post(
        self, articles: list[Article], trending_keywords: list[str]
    ) -> Optional[dict]:
        """Generate one research-style LinkedIn post from a cluster of articles."""
        if not articles:
            return None
        user_prompt = self._build_user_prompt(articles, trending_keywords)
        content = self._call_claude(user_prompt)
        if content:
            return self._save_post(articles, content, trending_keywords)
        return None

    # ── Prompt construction ────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        author = self.brand_kit.get("author", {})
        tone = self.brand_kit.get("tone_of_voice", {})
        brand = self.brand_kit.get("brand", {})
        hashtags = brand.get("hashtags", {})
        research = self.brand_kit.get("research_standards", {})

        length_guide = {
            "short": "300–500 characters (tight and punchy)",
            "medium": "500–900 characters (hook + context + take + sources)",
            "long": "900–1300 characters (deep-dive with a full argument)",
        }

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
            post_length=length_guide.get(
                brand.get("post_length", "medium"), length_guide["medium"]
            ),
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
            sources_block += f"Summary: {a.summary[:600] if a.summary else 'N/A'}\n"

        companies = sorted({c for a in articles for c in a.matched_companies})
        categories = sorted({c for a in articles for c in a.matched_categories})
        trending_str = (
            ", ".join(trending_keywords[:10])
            if trending_keywords
            else "AI, artificial intelligence"
        )

        return f"""\
Research and write a LinkedIn post synthesising ALL {len(articles)} of the following sources.

Source 1 is the primary anchor story. Sources 2–{len(articles)} provide supporting evidence, \
additional context, and citation depth.

HARD REQUIREMENT: You must cite all {len(articles)} sources in the post body and/or the Sources \
section at the end. The minimum is {self.min_sources} sources — never go below this.

For any direct verbatim quotes, you must attribute them explicitly:
"[exact quote]" — Full Name, Title, Company

## Source Material
{sources_block}

## Context
Companies involved: {', '.join(companies) or 'General AI news'}
Story categories: {', '.join(categories) or 'AI news'}
Currently trending (weave in naturally where relevant): {trending_str}

## Writing Instructions
- Synthesise across all sources — do NOT just paraphrase Source 1
- Add your genuine perspective: what does this mean specifically for brands and marketers?
- For product launches / new features: explain what it practically enables for a marketing team
- For funding news: explain what the investment signals about where the AI space is heading
- For research breakthroughs: explain in plain language why it changes what brands can do
- End with an engaging question that invites comments
- List all sources at the bottom under "Sources:" — one per line, with full URL
"""

    # ── Claude invocation ──────────────────────────────────────────────────────

    def _call_claude(self, user_prompt: str) -> Optional[str]:
        """
        Attempt generation via Claude CLI first (no API key needed in Claude Code
        environments), then fall back to the Anthropic Python SDK if available.
        """
        # ── 1. Claude CLI (Claude Code MCP connection) ─────────────────────────
        if shutil.which("claude"):
            try:
                result = subprocess.run(
                    [
                        "claude", "-p",
                        "--system-prompt", self._system_prompt,
                        "--model", self.model,
                        "--no-session-persistence",
                        "--tools", "",   # disable all tools — text-only generation
                        user_prompt,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=180,
                    # Run from /tmp so the repo's git hooks don't intercept the call
                    cwd="/tmp",
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
                if result.stderr:
                    print(f"  [warn] Claude CLI: {result.stderr[:300]}")
            except subprocess.TimeoutExpired:
                print("  [warn] Claude CLI timed out — falling back to SDK")
            except Exception as exc:
                print(f"  [warn] Claude CLI unavailable: {exc}")

        # ── 2. Anthropic Python SDK (requires ANTHROPIC_API_KEY in .env) ───────
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                sdk_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
                response = client.messages.create(
                    model=sdk_model,
                    max_tokens=1500,
                    system=[
                        {
                            "type": "text",
                            "text": self._system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return response.content[0].text.strip()
            except Exception as exc:
                print(f"  [error] Anthropic SDK: {exc}")

        print(
            "  [error] No Claude access found.\n"
            "  → In a Claude Code environment this works automatically.\n"
            "  → Otherwise add ANTHROPIC_API_KEY to your .env file."
        )
        return None

    # ── Persistence ────────────────────────────────────────────────────────────

    def _save_post(
        self, articles: list[Article], content: str, trending_keywords: list[str]
    ) -> dict:
        primary = articles[0]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
