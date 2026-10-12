"""
Generate LinkedIn post drafts via the Anthropic Messages API.

Uses only stdlib (urllib + json). No third-party packages required beyond PyYAML.
"""

import re
import json
import logging
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"

_SYSTEM = """You are a LinkedIn post writer. Write one research-backed LinkedIn post
that synthesises a cluster of news articles, following the author's brand voice exactly.

CRITICAL URL RULE — zero exceptions:
You may ONLY use URLs that appear verbatim in the "url" field of the supplied articles.
Never construct, shorten, guess, or modify any URL.
If unsure, write: [URL not provided — verify before publishing]

COMPANY NAMES: Always use the actual company name from the article. Never anonymise.

OUTPUT: Return ONLY a raw JSON object. Start with { and end with }. No markdown fences, no other text."""

_USER = """
=== BRAND KIT ===
{brand_yaml}

=== TODAY'S DATE ===
{today}

=== FILE TIMESTAMP ===
{timestamp}

=== ARTICLES (synthesise ALL of them, not just the first) ===
{articles_json}

=== TRENDING KEYWORDS (weave in 2-3 naturally — don't force them) ===
{trending_json}

=== TASK ===
Write one LinkedIn post following the brand kit's post_structure exactly:

1. HOOK (1-2 lines) — bold statement, surprising stat, or question. Never start with "I".
2. CONTEXT (2-3 lines) — what's happening across the space. Reference multiple developments.
3. EVIDENCE (4-6 lines) — facts and data from multiple sources. Cite inline.
   For direct verbatim quotes: "[exact quote]" — Full Name, Title, Company
   If you cannot confirm a quote is verbatim, paraphrase (no quote marks).
4. YOUR TAKE (3-5 lines) — synthesis and personal opinion. What's the pattern? Be opinionated.
5. SO WHAT (2-3 lines) — what this means for brands and marketers. Concrete and actionable.
6. CTA (1 line) — a question that invites genuine discussion in comments.
7. SOURCES — numbered list. Minimum {min_sources} sources.
   Format: [N]. Short descriptive title → full URL
8. HASHTAGS — {max_hashtags} hashtags on the very last line.
   Always include: {always_hashtags}
   Also rotate from: {rotate_hashtags}

HARD LIMITS:
- Post body (hook through CTA) max 1,457 characters and 251 words. Sources and hashtags don't count.
- Every sentence max 15 words — split anything longer.
- Short paragraphs: 1-3 sentences, blank line between every paragraph.
- Max 1 emoji per paragraph; never two in the same paragraph.

WORDS NEVER TO USE: "shipped", "game-changer", "revolutionary", "disruptive",
"leveraged", "utilised", "synergy", "thought leader", "AI lab" (say the company name).

Return this JSON object exactly — one object, no array:
{{
  "filename": "{timestamp}_{slug}.md",
  "filepath": "posts/{timestamp}_{slug}.md",
  "content": "<complete file: YAML frontmatter + blank line + post body>",
  "article_title": "<articles[0].title>",
  "source_url": "<articles[0].url>",
  "source_name": "<articles[0].source_name>",
  "source_count": {source_count}
}}

Where {slug} = first 40 chars of articles[0].title: lowercase, spaces/punctuation → hyphens,
alphanumeric + hyphens only, strip leading/trailing hyphens.

The "content" field must begin with YAML frontmatter:
---
title: "<articles[0].title>"
date: "{today}"
status: "draft"
primary_source_url: <articles[0].url>
primary_source_name: <articles[0].source_name>
all_sources:
  - title: <article.title>
    url: <article.url>
    publication: <article.source_name>
  [one entry per article]
source_count: {source_count}
matched_companies:
  [deduplicated company names across all articles]
matched_categories:
  [deduplicated category names across all articles]
---

Then a blank line, then the full post body (hook through hashtags).
"""


def generate_post(
    api_key: str,
    articles: list[dict],
    trending_keywords: list[str],
    brand_config: dict,
    model: str = "claude-sonnet-4-6",
) -> dict:
    """Generate one LinkedIn post from a cluster of articles."""

    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    rs = brand_config.get("research_standards", {})
    min_sources = rs.get("min_sources", 4)

    bk = brand_config.get("brand", {})
    max_hashtags = bk.get("max_hashtags", 5)
    always_hashtags = " ".join(bk.get("hashtags", {}).get("always_include", ["#AI"]))
    rotate_hashtags = " ".join(bk.get("hashtags", {}).get("rotate_from", [])[:10])

    brand_yaml = yaml.dump(brand_config, default_flow_style=False, allow_unicode=True)
    slug_hint = _make_slug(articles[0].get("title", "post"))

    user_msg = _USER.format(
        brand_yaml=brand_yaml,
        today=today,
        timestamp=timestamp,
        slug=slug_hint,
        articles_json=json.dumps(articles, indent=2, ensure_ascii=False),
        trending_json=json.dumps(trending_keywords, ensure_ascii=False),
        min_sources=min_sources,
        max_hashtags=max_hashtags,
        always_hashtags=always_hashtags,
        rotate_hashtags=rotate_hashtags,
        source_count=len(articles),
    )

    try:
        result = _call_api(
            api_key=api_key,
            model=model,
            max_tokens=8096,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = result.get("content", [{}])[0].get("text", "").strip()

        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            post = json.loads(text[start:end])

            # Ensure filename is set
            if not post.get("filename"):
                post["filename"] = f"{timestamp}_{slug_hint}.md"
                post["filepath"] = f"posts/{post['filename']}"

            return post
    except Exception as exc:
        logger.error("Post generation failed: %s", exc)

    return {}


def save_post(result: dict, posts_dir: Path) -> Optional[str]:
    """Write the post to posts_dir. Returns the saved path or None."""
    posts_dir.mkdir(parents=True, exist_ok=True)

    filename = result.get("filename", "")
    content = result.get("content", "")

    if not filename or not content:
        return None

    filepath = posts_dir / filename
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def _make_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())
    return slug.strip("-")[:40]


# ── Anthropic API client (stdlib only) ────────────────────────────────────

def _call_api(
    api_key: str,
    model: str,
    max_tokens: int,
    messages: list[dict],
    system: Optional[str] = None,
) -> dict:
    payload: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        payload["system"] = system

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        _API_URL,
        data=data,
        headers={
            "x-api-key": api_key,
            "anthropic-version": _API_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())
