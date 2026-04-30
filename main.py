#!/usr/bin/env python3
"""
LinkedIn Post Generator
-----------------------
Usage:
  python main.py run              # Full pipeline: fetch news, trends, generate posts
  python main.py run --dry-run    # Fetch and score news only, no generation
  python main.py run --max-posts 5
  python main.py list-posts       # List all saved draft posts
  python main.py show 1           # Show post #1 from the list
  python main.py show --file posts/2024-01-15_10-00-00_openai-launches.md
"""

import os
import shutil
import sys
from datetime import datetime
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


# ── config ────────────────────────────────────────────────────────────────────

@cli.command()
def config():
    """Show the paths to all editable config files."""
    console.print("\n[bold]Editable Configuration Files[/]\n")
    files = {
        "Topics of Interest": CONFIG_DIR / "topics.yaml",
        "Brand Kit & Tone of Voice": CONFIG_DIR / "brand_kit.yaml",
        "News Sources (RSS Feeds)": CONFIG_DIR / "sources.yaml",
        "My AI Experiments": CONFIG_DIR / "my_experiments.yaml",
        "Post Ideas & Angles": CONFIG_DIR / "post_ideas.yaml",
        "Environment Variables": BASE_DIR / ".env",
    }
    for label, path in files.items():
        exists = "[green]✓[/]" if path.exists() else "[red]✗ missing[/]"
        console.print(f"  {exists}  [bold]{label}[/]")
        console.print(f"     [dim]{path}[/]\n")


# ── add-experiment ─────────────────────────────────────────────────────────────

@cli.command("add-experiment")
@click.option("--tool", prompt="Tool / product name", help="e.g. Claude, ChatGPT, Midjourney")
@click.option("--company", prompt="Company name", help="e.g. Anthropic, OpenAI, Midjourney")
@click.option("--use-case", prompt="Use case (one line)", help="What were you trying to do?")
@click.option("--tried", prompt="What you tried", help="Describe what you actually did.")
@click.option("--happened", prompt="What happened", help="Honest results — what worked, what didn't.")
@click.option("--takeaway", prompt="Key takeaway", help="The one thing brands should know.")
@click.option("--tags", default="", help="Comma-separated tags, e.g. copywriting,brand strategy")
@click.option("--hours-saved", default=0.0, type=float, help="Estimated hours saved (optional).")
def add_experiment(
    tool: str,
    company: str,
    use_case: str,
    tried: str,
    happened: str,
    takeaway: str,
    tags: str,
    hours_saved: float,
):
    """Log a personal AI experiment to config/my_experiments.yaml."""
    experiments_file = CONFIG_DIR / "my_experiments.yaml"

    existing_data: dict = {}
    if experiments_file.exists():
        try:
            existing_data = yaml.safe_load(experiments_file.read_text(encoding="utf-8")) or {}
        except Exception:
            existing_data = {}

    experiments_list: list = existing_data.get("experiments", [])

    # Generate next ID
    existing_ids = [
        int(e.get("id", "exp000").replace("exp", ""))
        for e in experiments_list
        if str(e.get("id", "")).startswith("exp")
    ]
    next_num = (max(existing_ids) + 1) if existing_ids else 1
    new_id = f"exp{next_num:03d}"

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    new_exp: dict = {
        "id": new_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "tool": tool.strip(),
        "company": company.strip(),
        "use_case": use_case.strip(),
        "what_i_tried": tried.strip(),
        "what_happened": happened.strip(),
        "key_takeaway": takeaway.strip(),
        "include_in_posts": True,
        "tags": tag_list,
    }
    if hours_saved:
        new_exp["time_saved_hours"] = hours_saved

    experiments_list.append(new_exp)
    existing_data["experiments"] = experiments_list

    # Preserve the header comment when file already exists, otherwise write fresh
    if experiments_file.exists():
        raw = experiments_file.read_text(encoding="utf-8")
        header_end = raw.find("\nexperiments:")
        header = raw[:header_end] if header_end != -1 else ""
        body = yaml.dump(
            {"experiments": experiments_list},
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        experiments_file.write_text(header + "\n" + body, encoding="utf-8")
    else:
        experiments_file.write_text(
            yaml.dump(existing_data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    console.print(
        f"\n[green]✓[/] Experiment [bold]{new_id}[/] added to "
        f"[bold]config/my_experiments.yaml[/]\n"
        f"  Tool: {tool} ({company})\n"
        f"  Use case: {use_case}\n"
        f"\nNext run will weave this into relevant LinkedIn post drafts."
    )


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
