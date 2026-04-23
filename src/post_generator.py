"""
Post generator: uses the Anthropic API to draft LinkedIn posts
based on news articles, trending keywords, and brand guidelines.
"""

import json
import os
from pathlib import Path

import anthropic
import yaml


def _load_brand_kit() -> dict:
    config_path = Path(__file__).parent.parent / "config" / "brand_kit.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def _build_system_prompt(brand: dict) -> str:
    persona = brand.get("persona", {})
    tone = brand.get("tone", {})
    structure = brand.get("post_structure", {})
    style_rules = brand.get("style_rules", [])
    examples = brand.get("example_posts", [])

    example_text = ""
    if examples:
        example_text = "\n\n## EXAMPLE POSTS (for tone reference only — do not copy):\n"
        for ex in examples[:2]:
            example_text += f"\n---\n{ex.get('post', '')}\n"

    rules_text = "\n".join(f"- {r}" for r in style_rules)

    return f"""You are writing LinkedIn posts on behalf of {persona.get('name', 'the user')},
a {persona.get('role', 'marketing professional')}.

Their audience: {persona.get('audience', 'marketing and brand professionals')}.

Their positioning: {persona.get('positioning', '').strip()}

## TONE OF VOICE:
Primary style: {tone.get('primary', 'conversational-professional')}
Descriptors: {', '.join(tone.get('descriptors', []))}
Avoid: {', '.join(tone.get('avoid', []))}

## POST STRUCTURE:
- Hook: {structure.get('hook', {}).get('description', 'Open with a bold, scroll-stopping line')}
- Body: {structure.get('body', {}).get('structure', '3-5 short paragraphs')}
- Close: {structure.get('closing', {}).get('style', 'End with a question')}
- Length: {structure.get('length', {}).get('ideal_words', 180)} words (range: {structure.get('length', {}).get('min_words', 120)}–{structure.get('length', {}).get('max_words', 280)})

## WRITING RULES:
{rules_text}

## HASHTAG RULES:
Always include: {', '.join(brand.get('hashtags', {}).get('always_include', []))}
Add {brand.get('hashtags', {}).get('max_hashtags', 5) - len(brand.get('hashtags', {}).get('always_include', []))} more from: {', '.join(brand.get('hashtags', {}).get('rotate_from', [])[:8])}
{example_text}

IMPORTANT OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
  "post": "<the full LinkedIn post text including hashtags>",
  "headline": "<one punchy sentence summarising the angle — for internal use>",
  "content_angle": "<which angle you used>",
  "sources_cited": ["<source name>", ...],
  "suggested_image_prompt": "<a one-line prompt for generating a visual to accompany this post>"
}}"""


def _build_user_prompt(
    articles: list[dict],
    trending: list[dict],
    brand: dict,
    post_count: int = 3,
) -> str:
    # Format articles for the prompt
    article_lines = []
    for i, art in enumerate(articles[:10], 1):
        cats = ", ".join(art.get("matched_categories", []))
        article_lines.append(
            f"{i}. [{art['source']}] {art['title']}\n"
            f"   Summary: {art.get('summary', '')[:200]}\n"
            f"   URL: {art.get('url', '')}\n"
            f"   Categories: {cats}"
        )
    articles_text = "\n\n".join(article_lines) or "No articles provided."

    # Format trending keywords
    if trending:
        trend_text = "Trending: " + ", ".join(
            f"{t['keyword']} ({t['score']})" for t in trending[:10]
        )
    else:
        trend_text = "No trend data available."

    # Content angles
    angles = brand.get("content_angles", [])
    angles_text = "\n".join(f"- {a}" for a in angles)

    return f"""Based on the news articles below, write {post_count} distinct LinkedIn post(s).

## TODAY'S NEWS ARTICLES:
{articles_text}

## TRENDING KEYWORDS RIGHT NOW:
{trend_text}

## AVAILABLE CONTENT ANGLES (pick the best fit for each post):
{angles_text}

## INSTRUCTIONS:
1. Each post should be based on a DIFFERENT article or angle.
2. Pick the most newsworthy, brand-relevant stories.
3. Weave in trending keywords naturally where appropriate.
4. Always cite the source naturally within the post text (e.g., "via TechCrunch" or "according to VentureBeat").
5. Connect every tech development to a practical implication for brand teams or marketers.
6. Return a JSON array of {post_count} post objects, each following the required format.

Return ONLY valid JSON — no markdown fences, no explanation outside the JSON."""


def generate_posts(
    articles: list[dict],
    trending: list[dict],
    post_count: int = 3,
    model: str = "claude-opus-4-7",
) -> list[dict]:
    """
    Calls Anthropic API to generate LinkedIn posts.
    Returns list of post dicts.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")

    brand = _load_brand_kit()
    client = anthropic.Anthropic(api_key=api_key)

    system = _build_system_prompt(brand)
    user = _build_user_prompt(articles, trending, brand, post_count)

    print(f"  Calling {model} to generate {post_count} posts...")

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    raw = message.content[0].text.strip()

    # Parse JSON response
    try:
        posts = json.loads(raw)
        if isinstance(posts, dict):
            posts = [posts]
    except json.JSONDecodeError:
        # Attempt to extract JSON array from response
        import re
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            posts = json.loads(match.group())
        else:
            raise ValueError(f"Could not parse JSON from model response:\n{raw[:500]}")

    return posts


def format_post_for_display(post: dict, index: int) -> str:
    """Formats a post dict as readable terminal output."""
    lines = [
        f"\n{'='*60}",
        f"POST #{index}  |  Angle: {post.get('content_angle', 'N/A')}",
        f"{'='*60}",
        "",
        post.get("post", ""),
        "",
        f"[Internal headline: {post.get('headline', '')}]",
        f"[Sources: {', '.join(post.get('sources_cited', []))}]",
        f"[Image prompt: {post.get('suggested_image_prompt', '')}]",
    ]
    return "\n".join(lines)
