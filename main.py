#!/usr/bin/env python3
"""
LinkedIn Post Generator
-----------------------
Usage:
  python main.py run                        # Full pipeline: fetch news, trends, generate posts
  python main.py run --dry-run              # Fetch and score news only, no generation
  python main.py run --max-posts 5

  python main.py write-post --topic "Claude 4 launch"
  python main.py write-post --url "https://techcrunch.com/..."

  python main.py list-posts                 # List all saved draft posts
  python main.py show 1                     # Show post #1 from the list
  python main.py mark-published 1           # Mark post #1 as published
  python main.py config                     # Show paths to all config files
"""

import os
import shutil
import sys
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; set env vars manually if not installed

load_dotenv()

console = Console()

BASE_DIR = Path(__file__).parent

CONFIG_DIR = BASE_DIR / "config"
POSTS_DIR = BASE_DIR / "posts"


# ── CLI Entry Point ────────────────────────────────────────────────────────────

@click.group()
def cli():
    """LinkedIn Post Generator — AI-powered drafts from trending AI news."""
    pass


# ── run ───────────────────────────────────────────────────────────────────────

@cli.command()
@click.option(
    "--max-posts",
    default=3,
    show_default=True,
    help="Maximum number of posts to generate per run.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Fetch and rank news without generating any posts.",
)
def run(max_posts: int, dry_run: bool):
    """Run the full pipeline: fetch news → track trends → generate posts."""
    if not dry_run:
        has_claude_cli = shutil.which("claude") is not None
        has_api_key = bool(os.getenv("ANTHROPIC_API_KEY"))
        if not has_claude_cli and not has_api_key:
            console.print(
                "[bold red]Error:[/] No Claude access found.\n\n"
                "Either:\n"
                "  [bold]A)[/] Run inside Claude Code — the [bold]claude[/] CLI is detected automatically.\n"
                "  [bold]B)[/] Set [bold]ANTHROPIC_API_KEY[/] in your [bold].env[/] file "
                "(copy from [bold].env.example[/])."
            )
            sys.exit(1)
        if has_claude_cli:
            console.print("[dim]Using Claude Code CLI connection (no API key needed).[/]")
        else:
            console.print("[dim]Using Anthropic API key from .env[/]")

    from src.pipeline import Pipeline

    pipeline = Pipeline(CONFIG_DIR, POSTS_DIR)
    pipeline.run(max_posts=max_posts, dry_run=dry_run)


# ── list-posts ────────────────────────────────────────────────────────────────

@cli.command("list-posts")
def list_posts():
    """List all generated draft posts in the /posts directory."""
    posts = sorted(POSTS_DIR.glob("*.md"))
    if not posts:
        console.print(
            "[yellow]No posts found.[/] "
            "Run [bold]python main.py run[/] to generate some."
        )
        return

    table = Table(title="Saved Draft Posts", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="cyan", width=4, justify="right")
    table.add_column("Date", style="yellow", width=12)
    table.add_column("Status", style="bold green", width=10)
    table.add_column("Companies", style="magenta", width=28)
    table.add_column("Filename", style="white")

    for i, post_file in enumerate(posts, 1):
        date, status, companies = _read_frontmatter(post_file)
        table.add_row(str(i), date, status, companies, post_file.name)

    console.print(table)
    console.print(
        f"\n[dim]Use [bold]python main.py show <number>[/bold] to read a post.[/]"
    )


# ── show ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("number", type=int, required=False)
@click.option("--file", "-f", "filename", default=None, help="Exact filename to show.")
def show(number: int, filename: str):
    """Show a draft post. Pass the post number from list-posts, or --file <name>."""
    if filename:
        post_file = POSTS_DIR / filename
        if not post_file.exists():
            console.print(f"[red]File not found:[/] {filename}")
            sys.exit(1)
    elif number:
        posts = sorted(POSTS_DIR.glob("*.md"))
        if number < 1 or number > len(posts):
            console.print(
                f"[red]Invalid post number {number}.[/] "
                f"There are {len(posts)} post(s). Run [bold]list-posts[/] to see them."
            )
            sys.exit(1)
        post_file = posts[number - 1]
    else:
        console.print(
            "[yellow]Provide a post number or --file <filename>.[/]\n"
            "Example: [bold]python main.py show 1[/]"
        )
        sys.exit(1)

    raw = post_file.read_text(encoding="utf-8")

    # Separate frontmatter from body
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            meta_str, body = parts[1], parts[2].strip()
            try:
                meta = yaml.safe_load(meta_str)
            except Exception:
                meta = {}
        else:
            meta, body = {}, raw
    else:
        meta, body = {}, raw

    # Build metadata summary
    meta_lines = []
    if meta.get("source_name"):
        meta_lines.append(f"Source: {meta['source_name']}")
    if meta.get("source_published"):
        meta_lines.append(f"Published: {meta['source_published']}")
    if meta.get("matched_companies"):
        meta_lines.append(f"Companies: {', '.join(meta['matched_companies'])}")
    if meta.get("trending_keywords"):
        meta_lines.append(f"Trending: {', '.join(meta['trending_keywords'])}")
    if meta.get("source_url"):
        meta_lines.append(f"URL: {meta['source_url']}")

    if meta_lines:
        console.print(
            Panel(
                "\n".join(meta_lines),
                title="[bold]Article Metadata[/]",
                border_style="dim blue",
                padding=(0, 2),
            )
        )

    console.print(
        Panel(
            body,
            title=f"[bold]{post_file.name}[/]",
            subtitle=f"[dim]Status: {meta.get('status', 'draft')}[/]",
            border_style="green",
            padding=(1, 2),
        )
    )


# ── write-post ───────────────────────────────────────────────────────────────

@cli.command("write-post")
@click.option("--topic", "-t", default=None, help="Topic or keyword phrase to write about.")
@click.option("--url", "-u", default=None, help="Specific article URL to anchor the post on.")
def write_post(topic: str, url: str):
    """Generate a post on a specific topic or from a specific news URL.

    Examples:

      python main.py write-post --topic "Claude 4 launch"

      python main.py write-post --url "https://techcrunch.com/2025/..."
    """
    if not topic and not url:
        console.print(
            "[yellow]Provide either --topic or --url.[/]\n\n"
            "  [bold]python main.py write-post --topic \"Claude 4 launch\"[/]\n"
            "  [bold]python main.py write-post --url \"https://techcrunch.com/...\"[/]"
        )
        sys.exit(1)

    if not shutil.which("claude") and not os.getenv("ANTHROPIC_API_KEY"):
        console.print(
            "[bold red]Error:[/] No Claude access.\n"
            "Run inside Claude Code or add ANTHROPIC_API_KEY to .env"
        )
        sys.exit(1)

    from src.topic_searcher import TopicSearcher
    from src.post_generator import PostGenerator
    import yaml

    brand_kit = yaml.safe_load((CONFIG_DIR / "brand_kit.yaml").read_text())
    topics_cfg = yaml.safe_load((CONFIG_DIR / "topics.yaml").read_text())

    searcher = TopicSearcher(topics_cfg)

    if url:
        console.print(f"\n[bold cyan]Fetching article and finding related sources...[/]")
        console.print(f"[dim]URL: {url}[/]")
        articles = searcher.search_from_url(url)
    else:
        console.print(f"\n[bold cyan]Searching for recent articles on:[/] [bold]{topic}[/]")
        articles = searcher.search(topic)

    if not articles:
        console.print(
            "[red]No articles found.[/] Try a broader topic phrase or check your internet connection."
        )
        sys.exit(1)

    console.print(f"[green]✓[/] {len(articles)} source(s) found:")
    for i, a in enumerate(articles, 1):
        console.print(f"  [dim]{i}.[/] {a.title[:70]} [dim]({a.source_name})[/]")

    from src.trending_tracker import TrendingTracker
    tracker = TrendingTracker(topics_cfg)
    trending = tracker.get_trending_keywords()

    console.print(f"\n[bold cyan]Generating post...[/]")
    POSTS_DIR.mkdir(exist_ok=True)
    generator = PostGenerator(brand_kit, POSTS_DIR)
    result = generator.generate_post(articles, trending)

    if not result:
        console.print("[red]Post generation failed.[/]")
        sys.exit(1)

    console.print(
        f"\n[green]✓[/] Saved → [bold]{result['filename']}[/] "
        f"[dim]({result['source_count']} sources cited)[/]"
    )
    console.print(
        Panel(
            result["content"],
            title=f"[bold]{result['article_title'][:55]}[/]",
            subtitle=f"[dim]{result['filename']}[/]",
            border_style="green",
            padding=(1, 2),
        )
    )


# ── mark-published ────────────────────────────────────────────────────────────

@cli.command("mark-published")
@click.argument("number", type=int, required=False)
@click.option("--file", "-f", "filename", default=None, help="Exact filename to mark.")
def mark_published(number: int, filename: str):
    """Mark a draft post as published.

    Example: python main.py mark-published 1
    """
    if filename:
        post_file = POSTS_DIR / filename
    elif number:
        posts = sorted(POSTS_DIR.glob("*.md"))
        if number < 1 or number > len(posts):
            console.print(f"[red]Invalid post number {number}.[/]")
            sys.exit(1)
        post_file = posts[number - 1]
    else:
        console.print("[yellow]Provide a post number or --file <filename>.[/]")
        sys.exit(1)

    if not post_file.exists():
        console.print(f"[red]File not found:[/] {post_file.name}")
        sys.exit(1)

    raw = post_file.read_text(encoding="utf-8")
    updated = raw.replace("status: draft", "status: published", 1)

    if updated == raw:
        console.print(f"[yellow]Post is already marked as published or has no status field.[/]")
        return

    post_file.write_text(updated, encoding="utf-8")
    console.print(f"[green]✓[/] [bold]{post_file.name}[/] marked as [bold green]published[/].")


# ── config ────────────────────────────────────────────────────────────────────

@cli.command()
def config():
    """Show the paths to all editable config files."""
    console.print("\n[bold]Editable Configuration Files[/]\n")
    files = {
        "Topics of Interest": CONFIG_DIR / "topics.yaml",
        "Brand Kit & Tone of Voice": CONFIG_DIR / "brand_kit.yaml",
        "News Sources (RSS Feeds)": CONFIG_DIR / "sources.yaml",
        "Environment Variables": BASE_DIR / ".env",
    }
    for label, path in files.items():
        exists = "[green]✓[/]" if path.exists() else "[red]✗ missing[/]"
        console.print(f"  {exists}  [bold]{label}[/]")
        console.print(f"     [dim]{path}[/]\n")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _read_frontmatter(post_file: Path) -> tuple[str, str, str]:
    """Return (date, status, companies) from a post's YAML frontmatter."""
    try:
        raw = post_file.read_text(encoding="utf-8")
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 2:
                meta = yaml.safe_load(parts[1]) or {}
                date = str(meta.get("date", "—"))
                status = str(meta.get("status", "draft"))
                companies = ", ".join(meta.get("matched_companies", [])[:3]) or "—"
                return date, status, companies
    except Exception:
        pass
    return "—", "unknown", "—"


if __name__ == "__main__":
    cli()
