import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import anthropic
import yaml

from .news_gatherer import Article

# ── System prompt template ─────────────────────────────────────────────────────
# This is sent to Claude with prompt caching so it's only billed once per session.

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

## Hashtag Rules
- Always include: {always_hashtags}
- Choose from rotation list to reach exactly {max_hashtags} total hashtags: {rotate_hashtags}
- Put all hashtags on the final line of the post

## Output Rules
- Output ONLY the LinkedIn post text, nothing else
- No preamble, no explanation, no "Here's the post:" label
- Target length: {post_length}
- Cite the source URL clearly within the post body (label it "Source:" or "Read more:")
- Write as {author_name} in first person
- Make it feel like a real person wrote this, not a press release
"""


class PostGenerator:
    def __init__(self, brand_kit: dict, posts_dir: Path):
        self.brand_kit = brand_kit
        self.posts_dir = posts_dir
        self.posts_dir.mkdir(exist_ok=True)
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self._system_prompt = self._build_system_prompt()

    def generate_post(
        self, article: Article, trending_keywords: list[str]
    ) -> Optional[dict]:
        """Generate a LinkedIn post for one article and save it as a markdown draft."""
        user_prompt = self._build_user_prompt(article, trending_keywords)
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1200,
                system=[
                    {
                        "type": "text",
                        "text": self._system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=[{"role": "user", "content": user_prompt}],
            )
            post_content = response.content[0].text.strip()
            return self._save_post(article, post_content, trending_keywords)
        except anthropic.AuthenticationError:
            raise
        except Exception as exc:
            print(f"  [error] Generation failed for '{article.title[:60]}': {exc}")
            return None

    # ── Private helpers ────────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        author = self.brand_kit.get("author", {})
        tone = self.brand_kit.get("tone_of_voice", {})
        brand = self.brand_kit.get("brand", {})
        hashtags = brand.get("hashtags", {})

        length_guide = {
            "short": "300–500 characters (concise, punchy)",
            "medium": "500–900 characters (enough room for context and your take)",
            "long": "900–1300 characters (deep-dive with full argument)",
        }
        post_length = brand.get("post_length", "medium")

        def bullet_list(items: list) -> str:
            return "\n".join(f"- {i}" for i in items)

        def numbered_list(items: list) -> str:
            return "\n".join(f"{n}. {i}" for n, i in enumerate(items, 1))

        return _SYSTEM_TEMPLATE.format(
            author_name=author.get("name", "the author"),
            author_title=author.get("title", ""),
            author_tagline=author.get("tagline", ""),
            focus_areas=bullet_list(brand.get("focus_areas", [])),
            tone_traits=bullet_list(tone.get("primary_traits", [])),
            writing_style=bullet_list(tone.get("writing_style", [])),
            post_structure=numbered_list(tone.get("post_structure", [])),
            dos=bullet_list(tone.get("dos", [])),
            donts=bullet_list(tone.get("donts", [])),
            always_hashtags=" ".join(hashtags.get("always_include", [])),
            max_hashtags=brand.get("max_hashtags", 5),
            rotate_hashtags=" ".join(hashtags.get("rotate_from", [])),
            post_length=length_guide.get(post_length, length_guide["medium"]),
        )

    def _build_user_prompt(self, article: Article, trending_keywords: list[str]) -> str:
        context_lines = []
        if article.matched_companies:
            context_lines.append(f"Companies featured: {', '.join(article.matched_companies)}")
        if article.matched_categories:
            context_lines.append(f"Story type: {', '.join(article.matched_categories)}")

        trending_str = (
            ", ".join(trending_keywords[:10])
            if trending_keywords
            else "artificial intelligence, AI tools"
        )

        pub_date = (
            article.published.strftime("%B %d, %Y") if article.published else "recently"
        )

        return f"""\
Write a LinkedIn post reacting to the following news article.

## Article
Title: {article.title}
Source: {article.source_name}
URL: {article.url}
Published: {pub_date}

## Article Summary
{article.summary or "No summary available — use the title as your anchor."}

## Story Context
{chr(10).join(context_lines) if context_lines else "General AI news."}

## Currently Trending Search Terms (weave in naturally where relevant)
{trending_str}

## Instructions
- Add your genuine perspective on what this means for brands and marketers
- If this is a product launch or new feature, explain what it practically does and why it matters
- If this is funding news, explain what the investment signals about the AI space
- Include the source URL in the post body
- Follow the brand guidelines exactly
"""

    def _save_post(
        self, article: Article, content: str, trending_keywords: list[str]
    ) -> dict:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        slug = re.sub(r"[^\w\s-]", "", article.title.lower())[:40].strip()
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")
        filename = f"{timestamp}_{slug}.md"

        frontmatter = {
            "title": article.title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source_url": article.url,
            "source_name": article.source_name,
            "source_published": (
                article.published.strftime("%Y-%m-%d") if article.published else None
            ),
            "trending_keywords": trending_keywords[:5],
            "matched_companies": article.matched_companies,
            "matched_categories": article.matched_categories,
            "relevance_score": article.relevance_score,
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
            "article_title": article.title,
            "source_url": article.url,
            "source_name": article.source_name,
        }
