import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
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

## ⚠️ CRITICAL URL RULE (zero exceptions)
- You may ONLY use the exact URLs that appear in the "URL:" fields of the Source Material
- NEVER construct, guess, infer, complete, or recall any URL from your training data
- NEVER modify or shorten a provided URL
- If a source does not have a "URL:" field or it is blank, write "[URL not provided]" in the sources list — do not invent a URL
- Every URL in your Sources section must be copied character-for-character from the Source Material

## Hashtag Rules
- Always include: {always_hashtags}
- Choose from this rotation list to reach exactly {max_hashtags} total: {rotate_hashtags}
- Place all hashtags on the very last line of the post

## Output Rules
- Output ONLY the LinkedIn post text — no preamble, no "Here's the post:" label, no commentary
- Target length: {post_length}
- Write as {author_name} in first person
- Make it sound like a real person who has done their homework, not a press release
"""


class PostGenerator:
    """
    Generates LinkedIn posts from article clusters using Claude CLI or Anthropic SDK.

    Accepts three optional config dicts beyond the core brand_kit:
      tone_config       — from config/tone_of_voice.yaml  (voice, style, structure)
      templates_config  — from config/post_templates.yaml (per-angle framing)
      experiments_config — from config/my_experiments.yaml (personal HitL evidence)
    """

    def __init__(
        self,
        brand_kit: dict,
        posts_dir: Path,
        tone_config: Optional[dict] = None,
        templates_config: Optional[dict] = None,
        experiments_config: Optional[dict] = None,
    ):
        self.brand_kit = brand_kit
        self.posts_dir = posts_dir
        self.posts_dir.mkdir(exist_ok=True)

        # Tone: prefer separate tone_of_voice.yaml; fall back to inline brand_kit section
        self.tone = tone_config or brand_kit.get("tone_of_voice", {})

        self.templates_config = templates_config or {}
        self.experiments_config = experiments_config or {}

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

        template = self._detect_template(articles)
        experiments = self._pick_relevant_experiments(articles)

        provided_urls = [a.url for a in articles if a.url]
        user_prompt = self._build_user_prompt(
            articles, trending_keywords, template, experiments
        )
        raw = self._call_claude(user_prompt)
        if not raw:
            return None

        content = _strip_preamble(raw)
        content, url_report = self._validate_source_urls(content, provided_urls)

        broken = [u for u, s in url_report.items() if s == "broken"]
        unverified = [u for u, s in url_report.items() if s == "unverified"]
        if broken:
            print(f"  [⚠️  {len(broken)} broken URL(s) flagged in post — fix before publishing]")
        if unverified:
            print(f"  [ℹ️  {len(unverified)} URL(s) could not be verified (no network?) — check before publishing]")

        template_name = template["name"] if template else "General"
        return self._save_post(articles, content, trending_keywords, url_report, template_name)

    # ── Template detection ─────────────────────────────────────────────────────

    def _detect_template(self, articles: list[Article]) -> Optional[dict]:
        """
        Match the article cluster against post_templates.yaml to find the best-fit angle.
        YouTube sources are detected by source name, not keywords.
        Returns the matched template dict, or None when no template scores high enough.
        """
        templates = self.templates_config.get("templates", [])
        if not templates:
            return None

        all_text = " ".join(
            f"{a.title} {a.summary}" for a in articles
        ).lower()
        source_names = " ".join(a.source_name.lower() for a in articles)
        is_youtube = "youtube" in source_names

        best_template: Optional[dict] = None
        best_score = 0

        for tmpl in templates:
            # YouTube sources get matched immediately to the YouTube template
            if tmpl.get("name") == "YouTube Video Release" and is_youtube:
                return tmpl

            trigger_keywords = tmpl.get("trigger_keywords", [])
            if not trigger_keywords:
                continue

            score = sum(1 for kw in trigger_keywords if kw.lower() in all_text)
            if score > best_score:
                best_score = score
                best_template = tmpl

        # Require at least 2 keyword matches to activate a template
        return best_template if best_score >= 2 else None

    # ── Experiment injection ───────────────────────────────────────────────────

    def _pick_relevant_experiments(self, articles: list[Article]) -> list[dict]:
        """
        Rank experiments from my_experiments.yaml by relevance to the article cluster.
        Returns the top N experiments (usually 1) to weave into the post prompt.
        """
        all_experiments = self.experiments_config.get("experiments", [])
        if not all_experiments:
            return []

        settings = self.experiments_config.get("settings", {})
        max_per_post = settings.get("max_experiments_per_post", 1)
        require_tag_match = settings.get("require_tag_match", False)
        min_score = settings.get("min_relevance_score", 2)

        all_text = " ".join(
            f"{a.title} {a.summary}" for a in articles
        ).lower()
        company_names = {c.lower() for a in articles for c in a.matched_companies}
        category_names = {c.lower() for a in articles for c in a.matched_categories}

        scored: list[tuple[int, dict]] = []
        for exp in all_experiments:
            if not exp.get("usable_in_posts", True):
                continue

            score = 0
            tool = exp.get("tool", "").lower()
            tags = [t.lower() for t in exp.get("tags", [])]

            # Strong match: tool name appears in tracked company names
            if any(tool in company for company in company_names):
                score += 5
            # Moderate match: tool name appears anywhere in article text
            if tool in all_text:
                score += 3
            # Tag overlap with article categories
            for tag in tags:
                if any(tag in cat for cat in category_names):
                    score += 2
                if tag in all_text:
                    score += 1

            if score >= min_score or (not require_tag_match and score > 0):
                scored.append((score, exp))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored[:max_per_post]]

    # ── Prompt construction ────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        author = self.brand_kit.get("author", {})
        tone = self.tone
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
        self,
        articles: list[Article],
        trending_keywords: list[str],
        template: Optional[dict],
        experiments: list[dict],
    ) -> str:
        # ── Source material block ──────────────────────────────────────────────
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

        # ── Template / angle block ─────────────────────────────────────────────
        template_block = ""
        if template:
            template_block = f"""
## Post Angle: {template['name']}
{template.get('framing', '').strip()}

Hook guidance: {template.get('hook_style', '')}
"""

        # ── Personal experiments block ─────────────────────────────────────────
        experiment_block = ""
        if experiments:
            exp = experiments[0]
            verdict_label = {
                "positive": "Worked well",
                "mixed": "Mixed results",
                "negative": "Didn't work as hoped",
            }.get(exp.get("verdict", ""), exp.get("verdict", ""))

            time_note = (
                f"\n- Time impact: {exp['time_saved']}" if exp.get("time_saved") else ""
            )
            experiment_block = f"""
## Your Personal Experience (use if it strengthens the post)
You have personally experimented with {exp.get('tool', 'this tool')}:
- Task: {exp.get('use_case', '')}
- What happened: {exp.get('what_happened', '').strip()}
- Verdict: {verdict_label}{time_note}

Weave this in naturally as first-person evidence — only if it genuinely adds to the post.
Do NOT force it if it doesn't fit. Attribute it to yourself ("In my own work, I found..." or similar).
"""

        return f"""\
Research and write a LinkedIn post synthesising ALL {len(articles)} of the following sources.

Source 1 is the primary anchor story. Sources 2–{len(articles)} provide supporting evidence, \
additional context, and citation depth.

HARD REQUIREMENT: Cite all {len(articles)} sources. Minimum {self.min_sources} — never fewer.

⚠️ URL RULE: Copy every source URL character-for-character from the "URL:" fields below.
Do NOT construct, modify, shorten, or recall any URL. If a URL field is missing, write [URL not provided].

For direct verbatim quotes: "[exact quote]" — Full Name, Title, Company
{template_block}
## Source Material
{sources_block}
## Context
Companies involved: {', '.join(companies) or 'General AI news'}
Story categories: {', '.join(categories) or 'AI news'}
Currently trending (weave in naturally): {trending_str}
{experiment_block}
## Writing Instructions
- Synthesise across all sources — do NOT just paraphrase Source 1
- Add genuine perspective on what this means for brands and marketers specifically
- For launches/features: explain the practical implication for a marketing team
- For funding: explain what the investment signals about the AI landscape
- For YouTube videos: write as someone who watched it and has a reaction
- End with an engaging question that invites comments
- List all sources at the bottom under "Sources:" with full URLs copied from above
"""

    # ── Claude invocation ──────────────────────────────────────────────────────

    def _call_claude(self, user_prompt: str) -> Optional[str]:
        """
        Attempt generation via Claude CLI first (works in Claude Code environments
        without an API key), then fall back to the Anthropic Python SDK.
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
                        "--tools", "",
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

    # ── URL validation ─────────────────────────────────────────────────────────

    def _validate_source_urls(
        self, content: str, provided_urls: list[str]
    ) -> tuple[str, dict]:
        """
        Scan the Sources section of the post.
        - URLs matching the provided article list → 'source-verified'
        - Any extra URL Claude added → HEAD-checked live
        - Broken URLs → annotated with ⚠️ warning in the post text
        - Unverifiable URLs (no network) → annotated with [unverified]
        Returns (annotated_content, {url: status})
        """
        url_pattern = re.compile(r"https?://[^\s\)\]\>\"\'<]+")
        provided_set = {u.rstrip("/") for u in provided_urls if u}

        lines = content.split("\n")
        result_lines: list[str] = []
        in_sources = False
        url_statuses: dict[str, str] = {}

        for line in lines:
            stripped_upper = line.strip().upper()
            if stripped_upper.startswith("SOURCES") or re.match(r"^\[1\][\.\)]", line.strip()):
                in_sources = True

            if in_sources:
                for url in url_pattern.findall(line):
                    clean = url.rstrip("/.,")
                    if clean in provided_set or url.rstrip("/.,") in provided_set:
                        url_statuses[url] = "source-verified"
                    elif url not in url_statuses:
                        status = _check_url(url)
                        url_statuses[url] = status
                        if status == "broken":
                            line = line.replace(
                                url,
                                f"{url} ⚠️ [BROKEN LINK — remove before publishing]",
                            )
                        elif status == "unverified":
                            line = line.replace(
                                url,
                                f"{url} [unverified — check before publishing]",
                            )

            result_lines.append(line)

        return "\n".join(result_lines), url_statuses

    # ── Persistence ────────────────────────────────────────────────────────────

    def _save_post(
        self,
        articles: list[Article],
        content: str,
        trending_keywords: list[str],
        url_report: dict | None = None,
        template_name: str = "General",
    ) -> dict:
        primary = articles[0]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        slug = re.sub(r"[^\w\s-]", "", primary.title.lower())[:40].strip()
        slug = re.sub(r"[\s_]+", "-", slug).strip("-")
        filename = f"{timestamp}_{slug}.md"

        all_companies = sorted({c for a in articles for c in a.matched_companies})
        all_categories = sorted({c for a in articles for c in a.matched_categories})

        broken_count = sum(1 for s in (url_report or {}).values() if s == "broken")
        unverified_count = sum(1 for s in (url_report or {}).values() if s == "unverified")

        frontmatter = {
            "title": primary.title,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "post_angle": template_name,
            "primary_source_url": primary.url,
            "primary_source_name": primary.source_name,
            "all_sources": [
                {"title": a.title, "url": a.url, "publication": a.source_name}
                for a in articles
            ],
            "source_count": len(articles),
            "url_validation": {
                "source_verified": sum(1 for s in (url_report or {}).values() if s == "source-verified"),
                "broken": broken_count,
                "unverified": unverified_count,
            },
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
            "broken_urls": broken_count,
            "post_angle": template_name,
        }


# ── Module-level helpers ───────────────────────────────────────────────────────

def _strip_preamble(content: str) -> str:
    """
    Remove any explanatory text Claude emits before the actual post.
    If there's a '---' separator (Claude explaining something first, then writing
    the post after a divider), take everything after the first separator.
    """
    if "\n---\n" in content:
        parts = content.split("\n---\n", 1)
        candidate = parts[1].strip()
        if len(candidate) > 100:
            return candidate
    return content


def _check_url(url: str, timeout: int = 6) -> str:
    """
    HEAD-check a URL and return one of: 'verified', 'broken', 'unverified'.
    'unverified' means the network is unavailable or the check timed out —
    the URL may still be valid; the user should check manually before publishing.
    """
    try:
        resp = requests.head(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": "LinkedInPostBot/1.0"},
        )
        return "verified" if resp.status_code < 400 else "broken"
    except requests.exceptions.HTTPError:
        return "broken"
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return "unverified"
    except Exception:
        return "unverified"
