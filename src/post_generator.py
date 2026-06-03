"""
post_generator.py
Calls the Anthropic Claude API to write a research-backed LinkedIn post
from a cluster of scored articles, then saves it as a markdown draft.

Voice, structure, and style are driven entirely by config/brand_kit.yaml.
Edit that file to change tone, post length, hashtags, or writing rules.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import anthropic

BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "posts"


# ── Public entry point ────────────────────────────────────────────────────────

def generate_post(articles: list[dict], trending_keywords: list[str], config: dict) -> dict:
    """
    Generate one LinkedIn post from a cluster of articles.
    Returns a result dict with filename, filepath, content, and metadata.
    """
    brand = config["brand_kit"]
    model = config.get("anthropic_model", "claude-sonnet-4-6")

    client = anthropic.Anthropic()
    system_prompt = _build_system_prompt(brand)
    user_prompt = _build_user_prompt(articles, trending_keywords, brand)

    message = client.messages.create(
        model=model,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},  # cache the static brand context
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    post_text = message.content[0].text.strip()
    return _save_post(post_text, articles)


# ── Prompt builders ───────────────────────────────────────────────────────────

def _build_system_prompt(brand: dict) -> str:
    """Static system prompt built from brand_kit.yaml. Cached by Claude API."""
    author = brand.get("author", {})
    tov = brand.get("tone_of_voice", {})
    b = brand.get("brand", {})
    rs = brand.get("research_standards", {})

    name = author.get("name", "the author")
    title = author.get("title", "")
    tagline = author.get("tagline", "")

    traits = "\n".join(f"- {t}" for t in tov.get("primary_traits", []))
    style = "\n".join(f"- {r}" for r in tov.get("writing_style", []))
    structure = "\n".join(
        f"{i + 1}. {s}" for i, s in enumerate(tov.get("post_structure", []))
    )
    dos = "\n".join(f"- {d}" for d in tov.get("dos", []))
    donts = "\n".join(f"- {d}" for d in tov.get("donts", []))
    focus = "\n".join(f"- {f}" for f in b.get("focus_areas", []))
    angles = "\n".join(f"- {a}" for a in b.get("content_angles", []))

    always_tags = " ".join(b.get("hashtags", {}).get("always_include", []))
    rotate_tags = ", ".join(b.get("hashtags", {}).get("rotate_from", []))
    max_hashtags = b.get("max_hashtags", 5)
    min_sources = rs.get("min_sources", 4)

    return f"""You are {name} — {title}.
{tagline}

You write for brand strategists, marketers, and business leaders who want to understand and apply AI — not just follow the hype. Your posts are opinionated, grounded in real news, and always tie AI developments back to what they mean for brands and teams.

## Your Voice & Traits
{traits}

## Writing Style Rules (follow every rule on every post)
{style}

## Post Structure — follow this exact order
{structure}

## Your Brand Focus Areas (the lenses you write through)
{focus}

## Content Angles You Use
{angles}

## Dos
{dos}

## Don'ts
{donts}

## Banned Words (never use these)
- "shipped" → say "launched", "released", "put out", or "announced"
- "AI lab" → say the company name, or "AI company", "AI maker"
- "leveraged", "utilised", "synergy", "thought leader", "game-changer", "revolutionary", "disruptive" (unless immediately followed by a specific fact)
- "programmed", "deployed" (except in a genuinely technical context)

## Hard Limits (non-negotiable)
- Post body: maximum 1,457 characters and 251 words (EXCLUDING the sources list and hashtags)
- Every sentence: 15 words or fewer. Split anything longer into two sentences.
- Minimum {min_sources} distinct sources cited in the sources list
- Only use URLs that appear verbatim in the articles supplied — never construct, guess, or modify a URL
- One emoji per paragraph maximum. Never two in the same paragraph.

## Hashtag Rule
Always include: {always_tags}
Pick remaining from: {rotate_tags}
Total hashtags per post: {max_hashtags} (on the very last line)"""


def _build_user_prompt(
    articles: list[dict], trending_keywords: list[str], brand: dict
) -> str:
    """Dynamic prompt with the articles and trending keywords for this run."""
    rs = brand.get("research_standards", {})
    min_sources = rs.get("min_sources", 4)
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    articles_json = json.dumps(
        [
            {
                "title": a["title"],
                "url": a["url"],
                "summary": a["summary"],
                "source_name": a["source_name"],
                "published": a.get("published", ""),
                "matched_companies": a.get("matched_companies", []),
                "matched_categories": a.get("matched_categories", []),
            }
            for a in articles[:8]
        ],
        indent=2,
    )

    trending_str = ", ".join(f'"{k}"' for k in trending_keywords[:12])

    return f"""Today's date: {today}

## Trending Keywords (weave 2–3 naturally — don't force them all in)
{trending_str}

## Articles to Synthesise
Read all of them. Reference multiple articles — do not summarise just one.
{articles_json}

## Your Task
Write ONE LinkedIn post that:
1. Synthesises the articles above into a single narrative with your opinionated take
2. Follows the post structure from your system instructions exactly
3. Cites sources inline and lists ALL cited sources at the end (minimum {min_sources})
4. Connects the AI news to what it means for brands, marketers, or business leaders
5. Is written in first person as yourself

## URL Rule (zero exceptions)
Only use URLs that appear verbatim in the "url" fields of the articles above.
Never construct, shorten, or modify a URL. If uncertain, write: [URL not provided — verify before publishing]

## Output Format
Output ONLY the post. No preamble, no explanation, no markdown fences.
Start directly with the hook line.

At the very end include:
---

Sources:
[1]. [Short descriptive title] → [exact URL from articles]
[2]. [Short descriptive title] → [exact URL from articles]
... (minimum {min_sources} sources)

[all hashtags on one line]"""


# ── Saving ────────────────────────────────────────────────────────────────────

def _save_post(post_text: str, articles: list[dict]) -> dict:
    """Write the post to posts/ with YAML frontmatter."""
    POSTS_DIR.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc)
    primary = articles[0] if articles else {}

    slug = re.sub(r"[^a-z0-9]+", "-", primary.get("title", "post")[:40].lower()).strip("-")
    filename = f"{now.strftime('%Y-%m-%d_%H-%M-%S')}_{slug}.md"
    filepath = POSTS_DIR / filename

    frontmatter = _build_frontmatter(articles, now)
    filepath.write_text(frontmatter + post_text, encoding="utf-8")

    return {
        "filename": filename,
        "filepath": str(filepath),
        "content": post_text,
        "article_title": primary.get("title", ""),
        "source_url": primary.get("url", ""),
        "source_name": primary.get("source_name", ""),
        "source_count": len(articles),
    }


def _build_frontmatter(articles: list[dict], now: datetime) -> str:
    primary = articles[0] if articles else {}
    all_companies = list({c for a in articles for c in a.get("matched_companies", [])})
    all_categories = list({c for a in articles for c in a.get("matched_categories", [])})

    lines = [
        "---",
        f'title: "{_safe(primary.get("title", ""))}"',
        f'date: "{now.strftime("%Y-%m-%d")}"',
        f"primary_source_url: {primary.get('url', '')}",
        f'primary_source_name: "{primary.get("source_name", "")}"',
        "all_sources:",
    ]

    for a in articles:
        lines += [
            f'  - title: "{_safe(a.get("title", ""))}"',
            f"    url: {a.get('url', '')}",
            f'    publication: "{a.get("source_name", "")}"',
        ]

    lines += [
        f"source_count: {len(articles)}",
        "matched_companies:",
    ]
    lines += [f"  - {c}" for c in all_companies]
    lines += ["matched_categories:"]
    lines += [f"  - {c}" for c in all_categories]
    lines += [
        f'relevance_score: {primary.get("relevance_score", 0)}',
        'status: "draft"',
        "---",
        "",
    ]

    return "\n".join(lines) + "\n"


def _safe(text: str) -> str:
    return text.replace('"', "'")
