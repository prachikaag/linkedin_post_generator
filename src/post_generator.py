"""Generates LinkedIn posts using the Claude API with prompt caching."""
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import anthropic


class PostGenerator:
    def __init__(self, brand_config: dict, posts_dir: Path):
        self.brand = brand_config
        self.posts_dir = posts_dir
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.client = anthropic.Anthropic()
        model_env = os.getenv("ANTHROPIC_MODEL", "sonnet").lower()
        model_map = {
            "opus": "claude-opus-4-7",
            "sonnet": "claude-sonnet-4-6",
            "haiku": "claude-haiku-4-5",
        }
        self.model = model_map.get(model_env, model_env)

    def _build_system_prompt(self) -> str:
        author = self.brand.get("author", {})
        tov = self.brand.get("tone_of_voice", {})
        brand = self.brand.get("brand", {})
        standards = self.brand.get("research_standards", {})

        traits = "\n".join(f"- {t}" for t in tov.get("primary_traits", []))
        style = "\n".join(f"- {s}" for s in tov.get("writing_style", []))
        structure = "\n".join(
            f"{i+1}. {s}" for i, s in enumerate(tov.get("post_structure", []))
        )
        dos = "\n".join(f"- {d}" for d in tov.get("dos", []))
        donts = "\n".join(f"- {d}" for d in tov.get("donts", []))
        focus = "\n".join(f"- {f}" for f in brand.get("focus_areas", []))
        always_tags = " ".join(brand.get("hashtags", {}).get("always_include", []))
        rotate_tags = ", ".join(brand.get("hashtags", {}).get("rotate_from", []))
        max_hashtags = brand.get("max_hashtags", 5)
        max_chars = brand.get("max_characters", 1457)
        max_words = brand.get("max_words", 251)
        min_sources = standards.get("min_sources", 4)
        quote_format = standards.get("quote_format", '"[quote]" — Full Name, Title, Company')
        source_format = standards.get("source_list_format", "[N]. [Title] → [URL]")

        return f"""You are writing LinkedIn posts as {author.get("name", "the author")}, {author.get("title", "")}.
Tagline: {author.get("tagline", "")}

## Who you are
{traits}

## Writing style rules (follow every one)
{style}

## Post structure (follow in order)
{structure}

## What makes a great post
{dos}

## What undermines credibility
{donts}

## Brand focus areas (write through these lenses)
{focus}

## Hashtag rules
- Always include: {always_tags}
- Rotate from: {rotate_tags}
- Total hashtags per post: exactly {max_hashtags}
- Hashtags go on the very last line of the post

## Hard limits (non-negotiable)
- Post body (excluding SOURCES and HASHTAGS): maximum {max_chars} characters AND {max_words} words
- Every sentence: 15 words or fewer
- Maximum 1 emoji per paragraph — never two in the same paragraph
- Cite a minimum of {min_sources} distinct sources

## Citation rules
- Direct verbatim quotes: {quote_format}
- If a quote is not verbatim, paraphrase — no quote marks
- Source list format: {source_format}
- CRITICAL URL RULE: Only use URLs that appear verbatim in the article data supplied. Never construct, guess, shorten, or modify a URL. If uncertain, write [URL not provided — verify before publishing]

## Banned words
- "shipped" — use "launched", "released", "put out", or "announced"
- "AI lab" — use the company name directly, or "AI company", "AI maker"
- "programmed", "deployed" (except in genuinely technical context)
- "leveraged", "utilised", "synergy", "thought leader", "game-changer", "revolutionary", "disruptive" (without specifics)

## Company names
Always use the actual company name when it appears in the source — never anonymise as "a consulting firm" or "a major player".

Write the post now. Output only the post text — no preamble, no explanation."""

    def _build_user_message(self, articles: list[dict], trending_keywords: list[str]) -> str:
        kw_list = ", ".join(trending_keywords[:10])
        article_blocks = []
        for i, a in enumerate(articles, 1):
            article_blocks.append(
                f"[Article {i}]\n"
                f"Title: {a.get('title', '')}\n"
                f"Source: {a.get('source_name', '')}\n"
                f"URL: {a.get('url', '')}\n"
                f"Published: {a.get('published', '')}\n"
                f"Summary: {a.get('summary', '')}"
            )
        articles_text = "\n\n".join(article_blocks)

        return f"""Write a LinkedIn post synthesising ALL of the articles below.

TRENDING KEYWORDS THIS WEEK (weave 2-3 naturally):
{kw_list}

ARTICLES TO SYNTHESISE:
{articles_text}

Instructions:
- Follow the post structure exactly: HOOK → CONTEXT → EVIDENCE → YOUR TAKE → SO WHAT → CTA → SOURCES → HASHTAGS
- Draw from ALL articles — do not summarise only the first one
- Only use URLs that appear verbatim in the article data above
- Keep the post body under the character and word limits
- End with the SOURCES numbered list then HASHTAGS on the final line"""

    def _make_slug(self, title: str) -> str:
        slug = title.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")
        return slug[:40].rstrip("-")

    def _make_frontmatter(self, articles: list[dict], trending_keywords: list[str]) -> str:
        primary = articles[0] if articles else {}
        all_sources = [
            {"title": a.get("title", ""), "url": a.get("url", ""), "publication": a.get("source_name", "")}
            for a in articles
        ]
        companies = list({c for a in articles for c in a.get("matched_companies", [])})
        categories = list({c for a in articles for c in a.get("matched_categories", [])})
        used_keywords = trending_keywords[:5]
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        sources_yaml = "\n".join(
            f'  - title: "{s["title"]}"\n    url: "{s["url"]}"\n    publication: "{s["publication"]}"'
            for s in all_sources
        )
        kw_yaml = "\n".join(f'  - "{k}"' for k in used_keywords)
        company_yaml = "\n".join(f'  - "{c}"' for c in companies)
        category_yaml = "\n".join(f'  - "{c}"' for c in categories)

        return f"""---
title: "{primary.get('title', '')}"
date: "{today}"
primary_source_url: "{primary.get('url', '')}"
primary_source_name: "{primary.get('source_name', '')}"
all_sources:
{sources_yaml}
source_count: {len(articles)}
trending_keywords:
{kw_yaml}
matched_companies:
{company_yaml}
matched_categories:
{category_yaml}
relevance_score: {primary.get('relevance_score', 0)}
status: "draft"
---"""

    def generate_post(self, articles: list[dict], trending_keywords: list[str]) -> dict | None:
        if not articles:
            return None

        system_prompt = self._build_system_prompt()
        user_message = self._build_user_message(articles, trending_keywords)

        print("\n--- Generating post ---")
        post_content = ""
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=2048,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_message}],
            ) as stream:
                for text in stream.text_stream:
                    post_content += text
                    print(text, end="", flush=True)
        except Exception as e:
            print(f"\nError calling Claude API: {e}")
            return None

        print("\n--- Post complete ---\n")

        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        slug = self._make_slug(articles[0].get("title", "post"))
        filename = f"{timestamp}_{slug}.md"
        filepath = self.posts_dir / filename

        frontmatter = self._make_frontmatter(articles, trending_keywords)
        file_content = f"{frontmatter}\n\n{post_content}\n"
        filepath.write_text(file_content, encoding="utf-8")

        return {
            "filename": filename,
            "filepath": str(filepath),
            "content": post_content,
            "article_title": articles[0].get("title", ""),
            "source_url": articles[0].get("url", ""),
            "source_name": articles[0].get("source_name", ""),
            "source_count": len(articles),
        }
