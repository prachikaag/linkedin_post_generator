#!/usr/bin/env python3
"""
LinkedIn Post Generator
-----------------------
Usage:
  python main.py run                        # Full pipeline: fetch news → trends → generate posts
  python main.py run --dry-run              # Fetch and score news only (no generation)
  python main.py run --max-posts 5          # Generate up to 5 posts per run

  python main.py list-posts                 # List all draft posts
  python main.py list-posts --status approved  # Filter by status (draft/approved/published/rejected)
  python main.py show 1                     # Show post #1 from the list
  python main.py show --file posts/2024-01-15_openai-launches.md

  python main.py review                     # Human-in-the-loop: approve or reject each draft
  python main.py mark-published 1           # Mark post #1 as published after posting to LinkedIn

  python main.py config                     # Show all editable config file paths
"""

import os
import re
import shutil
import sys
from pathlib import Path

import click
import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

console = Console()

BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
POSTS_DIR = BASE_DIR / "posts"

# Status values used in YAML frontmatter
_STATUSES = ("draft", "approved", "rejected", "published")

# Status → rich style for list display
_STATUS_STYLE = {
    "draft": "yellow",
    "approved": "bold green",
    "rejected": "dim red",
    "published": "bold blue",
}


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
@click.option(
    "--status",
    default=None,
    type=click.Choice(_STATUSES, case_sensitive=False),
    help="Filter by status: draft, approved, rejected, or published.",
)
def list_posts(status: str | None):
    """List all generated post drafts in the /posts directory."""
    all_posts = sorted(POSTS_DIR.glob("*.md"))

    if status:
        posts = [p for p in all_posts if _get_post_status(p) == status]
    else:
        posts = all_posts

    if not posts:
        if status:
            console.print(
                f"[yellow]No posts with status '{status}'.[/] "
                f"Run [bold]list-posts[/] (no filter) to see all posts."
            )
        else:
            console.print(
                "[yellow]No posts found.[/] "
                "Run [bold]python main.py run[/] to generate some."
            )
        return

    title = f"Saved Posts ({status})" if status else "Saved Posts"
    table = Table(title=title, box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="cyan", width=4, justify="right")
    table.add_column("Date", style="yellow", width=12)
    table.add_column("Status", width=11)
    table.add_column("Companies", style="magenta", width=30)
    table.add_column("Filename", style="white")

    for i, post_file in enumerate(all_posts, 1):
        post_status, date, companies = _read_post_meta(post_file)
        if status and post_status != status:
            continue
        style = _STATUS_STYLE.get(post_status, "white")
        table.add_row(
            str(i),
            date,
            f"[{style}]{post_status}[/]",
            companies,
            post_file.name,
        )

    console.print(table)
    console.print(
        f"\n[dim]Use [bold]python main.py show <number>[/bold] to read a post · "
        f"[bold]review[/bold] to approve/reject drafts · "
        f"[bold]mark-published <number>[/bold] after posting.[/]"
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

    _display_post_file(post_file)


# ── review ────────────────────────────────────────────────────────────────────

@cli.command()
def review():
    """Human-in-the-loop review: approve, reject, or skip each draft post."""
    all_posts = sorted(POSTS_DIR.glob("*.md"))
    drafts = [p for p in all_posts if _get_post_status(p) == "draft"]

    if not drafts:
        console.print(
            "[yellow]No draft posts to review.[/]\n"
            "Run [bold]python main.py run[/] to generate new posts."
        )
        return

    console.print(f"\n[bold]{len(drafts)} draft post(s) queued for review.[/]\n")

    for i, post_file in enumerate(drafts, 1):
        console.rule(f"[bold]Post {i} of {len(drafts)}[/]")
        _display_post_file(post_file)

        console.print(
            "\n[dim]  a[/] [green]approve[/]   "
            "[dim]r[/] [red]reject[/]   "
            "[dim]s[/] skip   "
            "[dim]q[/] quit\n"
        )

        action = Prompt.ask(
            "Your choice",
            choices=["a", "r", "s", "q"],
            default="s",
        )

        if action == "a":
            _set_post_status(post_file, "approved")
            console.print(
                "[bold green]✓ Approved.[/] [dim]Ready to copy to LinkedIn.[/]\n"
            )
        elif action == "r":
            _set_post_status(post_file, "rejected")
            console.print("[red]✗ Rejected.[/]\n")
        elif action == "q":
            console.print("[dim]Review session ended.[/]")
            return
        # "s" → skip, no status change

    console.print("\n[bold green]Review session complete.[/]")
    approved = sum(1 for p in drafts if _get_post_status(p) == "approved")
    console.print(
        f"[dim]{approved}/{len(drafts)} post(s) approved. "
        f"Run [bold]list-posts --status approved[/bold] to see them.[/]"
    )


# ── mark-published ────────────────────────────────────────────────────────────

@cli.command("mark-published")
@click.argument("number", type=int)
def mark_published(number: int):
    """Mark a post as published after you have posted it to LinkedIn."""
    posts = sorted(POSTS_DIR.glob("*.md"))
    if number < 1 or number > len(posts):
        console.print(
            f"[red]Post #{number} not found.[/] "
            f"Run [bold]list-posts[/] to see all {len(posts)} post(s)."
        )
        sys.exit(1)

    post_file = posts[number - 1]
    current = _get_post_status(post_file)

    if current == "published":
        console.print(f"[dim]Post #{number} is already marked as published.[/]")
        return

    _set_post_status(post_file, "published")
    console.print(f"[bold blue]✓ Post #{number} marked as published.[/]")
    console.print(f"[dim]{post_file.name}[/]")


# ── config ────────────────────────────────────────────────────────────────────

@cli.command()
def config():
    """Show the paths to all editable config files."""
    console.print("\n[bold]Editable Configuration Files[/]\n")
    files = {
        "Topics of Interest": CONFIG_DIR / "topics.yaml",
        "Brand Kit (who you are)": CONFIG_DIR / "brand_kit.yaml",
        "Tone of Voice (how you write)": CONFIG_DIR / "tone_of_voice.yaml",
        "News Sources (RSS feeds + APIs)": CONFIG_DIR / "sources.yaml",
        "Environment Variables": BASE_DIR / ".env",
    }
    for label, path in files.items():
        exists = "[green]✓[/]" if path.exists() else "[red]✗ missing[/]"
        console.print(f"  {exists}  [bold]{label}[/]")
        console.print(f"     [dim]{path}[/]\n")


# ── Shared display helpers ─────────────────────────────────────────────────────

def _display_post_file(post_file: Path) -> None:
    """Render a post file to the terminal with metadata panel + content panel."""
    raw = post_file.read_text(encoding="utf-8")

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        meta_str = parts[1] if len(parts) >= 2 else ""
        body = parts[2].strip() if len(parts) >= 3 else raw
        try:
            meta = yaml.safe_load(meta_str) or {}
        except Exception:
            meta = {}
    else:
        meta, body = {}, raw

    meta_lines = []
    if meta.get("primary_source_name"):
        meta_lines.append(f"Primary source: {meta['primary_source_name']}")
    if meta.get("date"):
        meta_lines.append(f"Generated: {meta['date']}")
    if meta.get("matched_companies"):
        meta_lines.append(f"Companies: {', '.join(meta['matched_companies'])}")
    if meta.get("matched_categories"):
        meta_lines.append(f"Categories: {', '.join(meta['matched_categories'])}")
    if meta.get("trending_keywords"):
        meta_lines.append(f"Trending: {', '.join(meta['trending_keywords'])}")
    if meta.get("source_count"):
        meta_lines.append(f"Sources cited: {meta['source_count']}")
    if meta.get("primary_source_url"):
        meta_lines.append(f"URL: {meta['primary_source_url']}")

    if meta_lines:
        console.print(
            Panel(
                "\n".join(meta_lines),
                title="[bold]Article Metadata[/]",
                border_style="dim blue",
                padding=(0, 2),
            )
        )

    post_status = str(meta.get("status", "draft"))
    style = _STATUS_STYLE.get(post_status, "white")
    console.print(
        Panel(
            body,
            title=f"[bold]{post_file.name}[/]",
            subtitle=f"[{style}]status: {post_status}[/]",
            border_style="green",
            padding=(1, 2),
        )
    )


# ── Frontmatter helpers ────────────────────────────────────────────────────────

def _read_post_meta(post_file: Path) -> tuple[str, str, str]:
    """Return (status, date, companies) from a post's YAML frontmatter."""
    try:
        raw = post_file.read_text(encoding="utf-8")
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 2:
                meta = yaml.safe_load(parts[1]) or {}
                status = str(meta.get("status", "draft"))
                date = str(meta.get("date", "—"))
                companies = ", ".join(meta.get("matched_companies", [])[:3]) or "—"
                return status, date, companies
    except Exception:
        pass
    return "draft", "—", "—"


def _get_post_status(post_file: Path) -> str:
    status, _, _ = _read_post_meta(post_file)
    return status


def _set_post_status(post_file: Path, new_status: str) -> None:
    """Rewrite the status field in a post's YAML frontmatter."""
    raw = post_file.read_text(encoding="utf-8")
    updated = re.sub(
        r"^(status:\s*).*$",
        f"\\g<1>{new_status}",
        raw,
        flags=re.MULTILINE,
    )
    if updated == raw:
        # No status field found — insert one after the opening ---
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            updated = f"---{parts[1].rstrip()}\nstatus: {new_status}\n---{parts[2]}"
    post_file.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    cli()
