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

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt template from prompts/, stripping comment lines."""
    path = _PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    content_lines = [l for l in lines if not l.strip().startswith("#")]
    return "\n".join(content_lines).strip()


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

        provided_urls = [a.url for a in articles if a.url]
        user_prompt = self._build_user_prompt(articles, trending_keywords)
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

        return self._save_post(articles, content, trending_keywords, url_report)

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

        template = _load_prompt("post_system.txt")
        replacements = {
            "{{author_name}}": author.get("name", "the author"),
            "{{author_title}}": author.get("title", ""),
            "{{author_tagline}}": author.get("tagline", ""),
            "{{focus_areas}}": bl(brand.get("focus_areas", [])),
            "{{tone_traits}}": bl(tone.get("primary_traits", [])),
            "{{writing_style}}": bl(tone.get("writing_style", [])),
            "{{post_structure}}": nl(tone.get("post_structure", [])),
            "{{dos}}": bl(tone.get("dos", [])),
            "{{donts}}": bl(tone.get("donts", [])),
            "{{min_sources}}": str(research.get("min_sources", 4)),
            "{{always_hashtags}}": " ".join(hashtags.get("always_include", [])),
            "{{max_hashtags}}": str(brand.get("max_hashtags", 5)),
            "{{rotate_hashtags}}": " ".join(hashtags.get("rotate_from", [])),
            "{{post_length}}": length_guide.get(
                brand.get("post_length", "medium"), length_guide["medium"]
            ),
        }
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)
        return template

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

        template = _load_prompt("post_user.txt")
        replacements = {
            "{{source_count}}": str(len(articles)),
            "{{min_sources}}": str(self.min_sources),
            "{{sources_block}}": sources_block,
            "{{companies}}": ", ".join(companies) or "General AI news",
            "{{categories}}": ", ".join(categories) or "AI news",
            "{{trending}}": trending_str,
        }
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)
        return template

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
                        "--tools", "",   # text-only — no tool calls, no WebFetch preamble
                    ],
                    input=user_prompt,   # pass via stdin, not positional arg
                    capture_output=True,
                    text=True,
                    timeout=180,
                    cwd="/tmp",   # avoids triggering repo git hooks
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
        - URLs matching the provided article list → 'source-verified' (came from RSS, real at fetch time)
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
            # Detect start of the Sources section
            if stripped_upper.startswith("SOURCES") or re.match(r"^\[1\][\.\)]", line.strip()):
                in_sources = True

            if in_sources:
                for url in url_pattern.findall(line):
                    clean = url.rstrip("/.,")
                    if clean in provided_set or url.rstrip("/.,") in provided_set:
                        url_statuses[url] = "source-verified"
                        # No annotation needed — came from RSS
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
        if len(candidate) > 100:   # real post, not just an empty section
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
