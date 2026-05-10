#!/usr/bin/env python3
"""
LinkedIn Post Generator
-----------------------
Usage:
  python main.py run                   # Full pipeline: fetch news → trends → generate posts
  python main.py run --dry-run         # Fetch and score news only, skip generation
  python main.py run --max-posts 5     # Generate up to 5 posts per run
  python main.py run --force           # Ignore seen-article cache, regenerate from all news
  python main.py list-posts            # List all saved draft posts
  python main.py show 1                # Read post #1 from the list
  python main.py review                # Human-in-the-loop: step through drafts to approve
  python main.py approve 1             # Mark post #1 as approved (ready to publish)
  python main.py reset-cache           # Clear the seen-articles cache
  python main.py config                # Show paths to all editable config files
"""

import os
import shutil
import sys
from pathlib import Path

import click
import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

console = Console()

BASE_DIR   = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
POSTS_DIR  = BASE_DIR / "posts"


# ── CLI Entry Point ────────────────────────────────────────────────────────────

@click.group()
def cli():
    """LinkedIn Post Generator — AI-powered drafts from trending AI news."""
    pass


# ── run ───────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--max-posts", default=3, show_default=True,
              help="Maximum posts to generate per run.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Fetch and rank news only — skip generation.")
@click.option("--force", is_flag=True, default=False,
              help="Ignore the seen-articles cache and re-evaluate all news.")
def run(max_posts: int, dry_run: bool, force: bool):
    """Run the full pipeline: fetch news → track trends → generate posts."""
    if not dry_run:
        has_cli = shutil.which("claude") is not None
        has_key = bool(os.getenv("ANTHROPIC_API_KEY"))
        if not has_cli and not has_key:
            console.print(
                "[bold red]Error:[/] No Claude access found.\n\n"
                "Either:\n"
                "  [bold]A)[/] Run inside Claude Code — the [bold]claude[/] CLI is detected automatically.\n"
                "  [bold]B)[/] Set [bold]ANTHROPIC_API_KEY[/] in your [bold].env[/] file "
                "(copy from [bold].env.example[/])."
            )
            sys.exit(1)
        if has_cli:
            console.print("[dim]Using Claude Code CLI connection (no API key needed).[/]")
        else:
            console.print("[dim]Using Anthropic API key from .env[/]")

    from src.pipeline import Pipeline

    pipeline = Pipeline(CONFIG_DIR, POSTS_DIR)
    pipeline.run(max_posts=max_posts, dry_run=dry_run, force=force)


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
    table.add_column("#",         style="cyan",       width=4,  justify="right")
    table.add_column("Date",      style="yellow",     width=12)
    table.add_column("Status",    style="bold",       width=10)
    table.add_column("Companies", style="magenta",    width=28)
    table.add_column("Filename",  style="white")

    for i, post_file in enumerate(posts, 1):
        date, status, companies = _read_frontmatter_summary(post_file)
        status_style = (
            "[green]approved[/]" if status == "approved"
            else "[yellow]draft[/]" if status == "draft"
            else status
        )
        table.add_row(str(i), date, status_style, companies, post_file.name)

    console.print(table)
    console.print(
        "\n[dim]Commands: "
        "[bold]show <#>[/bold]  ·  "
        "[bold]review[/bold]  ·  "
        "[bold]approve <#>[/bold][/]"
    )


# ── show ──────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("number", type=int, required=False)
@click.option("--file", "-f", "filename", default=None, help="Exact filename to show.")
def show(number: int, filename: str):
    """Show a draft post. Pass the post number from list-posts, or --file <name>."""
    post_file = _resolve_post(number, filename)
    _print_post(post_file)


# ── review (human-in-the-loop) ────────────────────────────────────────────────

@cli.command()
def review():
    """
    Human-in-the-loop review: step through every draft post one by one.

    For each post you can: approve it, skip it, or delete it.
    Approved posts get their status updated to 'approved' in the frontmatter.
    """
    posts = [p for p in sorted(POSTS_DIR.glob("*.md")) if _get_status(p) == "draft"]
    if not posts:
        console.print("[green]No draft posts waiting for review.[/]")
        console.print("[dim]Run [bold]python main.py run[/bold] to generate new drafts.[/]")
        return

    console.print(
        f"\n[bold]Reviewing {len(posts)} draft post(s).[/]  "
        "[dim](a = approve, s = skip, d = delete, q = quit)[/]\n"
    )

    approved = skipped = deleted = 0
    for i, post_file in enumerate(posts, 1):
        console.rule(f"[bold cyan]Post {i} of {len(posts)}[/]")
        _print_post(post_file)

        while True:
            choice = Prompt.ask(
                "\n[bold]Action[/]",
                choices=["a", "s", "d", "q"],
                default="s",
            )
            if choice == "a":
                _set_status(post_file, "approved")
                console.print("[green]✓ Approved — ready to copy and post to LinkedIn.[/]")
                approved += 1
                break
            elif choice == "s":
                console.print("[dim]Skipped.[/]")
                skipped += 1
                break
            elif choice == "d":
                if Confirm.ask("[red]Delete this draft permanently?[/]", default=False):
                    post_file.unlink()
                    console.print("[red]Deleted.[/]")
                    deleted += 1
                    break
            elif choice == "q":
                console.print(
                    f"\n[dim]Review stopped early. "
                    f"Approved {approved}, skipped {skipped}, deleted {deleted}.[/]"
                )
                return

    console.print(
        f"\n[bold green]Review complete.[/] "
        f"Approved: [green]{approved}[/]  "
        f"Skipped: [yellow]{skipped}[/]  "
        f"Deleted: [red]{deleted}[/]\n"
    )
    if approved:
        console.print(
            "[dim]Run [bold]python main.py list-posts[/bold] to see all posts, "
            "then open the approved ones to copy to LinkedIn.[/]"
        )


# ── approve ───────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("number", type=int)
def approve(number: int):
    """Mark a post as approved and ready to publish. Pass the post number."""
    post_file = _resolve_post(number, None)
    _set_status(post_file, "approved")
    console.print(f"[green]✓ Approved:[/] {post_file.name}")


# ── reset-cache ───────────────────────────────────────────────────────────────

@cli.command("reset-cache")
def reset_cache():
    """Clear the seen-articles cache so the next run re-evaluates all news."""
    from src.post_tracker import PostTracker
    tracker = PostTracker(POSTS_DIR)
    count = tracker.seen_count()
    tracker.reset()
    console.print(f"[green]✓[/] Cache cleared — {count} article URL(s) removed.")
    console.print("[dim]Run [bold]python main.py run[/bold] to fetch fresh posts.[/]")


# ── config ────────────────────────────────────────────────────────────────────

@cli.command()
def config():
    """Show the paths to all editable config files."""
    console.print("\n[bold]Editable Configuration Files[/]\n")
    files = {
        "Topics of Interest":         CONFIG_DIR / "topics.yaml",
        "Brand Kit & Tone of Voice":  CONFIG_DIR / "brand_kit.yaml",
        "News Sources (RSS Feeds)":   CONFIG_DIR / "sources.yaml",
        "Environment Variables":      BASE_DIR   / ".env",
    }
    for label, path in files.items():
        exists = "[green]✓[/]" if path.exists() else "[red]✗ missing[/]"
        console.print(f"  {exists}  [bold]{label}[/]")
        console.print(f"     [dim]{path}[/]\n")

    console.print("[dim]Edit any file above, then run [bold]python main.py run[/bold].[/]\n")


# ── Helpers ────────────────────────────────────────────────────────────────────

def _resolve_post(number: int | None, filename: str | None) -> Path:
    if filename:
        p = POSTS_DIR / filename
        if not p.exists():
            console.print(f"[red]File not found:[/] {filename}")
            sys.exit(1)
        return p
    if number:
        posts = sorted(POSTS_DIR.glob("*.md"))
        if number < 1 or number > len(posts):
            console.print(
                f"[red]Invalid post number {number}.[/] "
                f"There are {len(posts)} post(s). "
                "Run [bold]list-posts[/bold] to see them."
            )
            sys.exit(1)
        return posts[number - 1]
    console.print(
        "[yellow]Provide a post number or --file <filename>.[/]\n"
        "Example: [bold]python main.py show 1[/]"
    )
    sys.exit(1)


def _print_post(post_file: Path) -> None:
    raw = post_file.read_text(encoding="utf-8")

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        meta_str, body = (parts[1], parts[2].strip()) if len(parts) >= 3 else ("", raw)
        try:
            meta = yaml.safe_load(meta_str) or {}
        except Exception:
            meta = {}
    else:
        meta, body = {}, raw

    meta_lines = []
    if meta.get("date"):
        meta_lines.append(f"Date: {meta['date']}")
    if meta.get("matched_companies"):
        meta_lines.append(f"Companies: {', '.join(meta['matched_companies'])}")
    if meta.get("trending_keywords"):
        meta_lines.append(f"Trending: {', '.join(meta['trending_keywords'])}")
    if meta.get("source_count"):
        meta_lines.append(f"Sources cited: {meta['source_count']}")
    url_val = meta.get("url_validation", {})
    if url_val.get("broken"):
        meta_lines.append(f"[red]⚠ {url_val['broken']} broken link(s) — fix before publishing[/]")

    if meta_lines:
        console.print(
            Panel(
                "\n".join(meta_lines),
                title="[bold]Metadata[/]",
                border_style="dim blue",
                padding=(0, 2),
            )
        )

    status = meta.get("status", "draft")
    status_colour = "green" if status == "approved" else "yellow"
    console.print(
        Panel(
            body,
            title=f"[bold]{post_file.name}[/]",
            subtitle=f"[{status_colour}]Status: {status}[/]",
            border_style="green",
            padding=(1, 2),
        )
    )


def _read_frontmatter_summary(post_file: Path) -> tuple[str, str, str]:
    try:
        raw = post_file.read_text(encoding="utf-8")
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 2:
                meta = yaml.safe_load(parts[1]) or {}
                date      = str(meta.get("date", "—"))
                status    = str(meta.get("status", "draft"))
                companies = ", ".join(meta.get("matched_companies", [])[:3]) or "—"
                return date, status, companies
    except Exception:
        pass
    return "—", "unknown", "—"


def _get_status(post_file: Path) -> str:
    date, status, _ = _read_frontmatter_summary(post_file)
    return status


def _set_status(post_file: Path, new_status: str) -> None:
    raw = post_file.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            meta_str, body = parts[1], parts[2]
            updated = _replace_yaml_field(meta_str, "status", new_status)
            post_file.write_text(f"---{updated}---{body}", encoding="utf-8")
            return
    # Fallback: prepend frontmatter
    post_file.write_text(
        f"---\nstatus: {new_status}\n---\n\n{raw}", encoding="utf-8"
    )


def _replace_yaml_field(meta_str: str, key: str, value: str) -> str:
    import re
    pattern = re.compile(rf"^({key}:\s*).*$", re.MULTILINE)
    if pattern.search(meta_str):
        return pattern.sub(rf"\g<1>{value}", meta_str)
    return meta_str + f"{key}: {value}\n"


if __name__ == "__main__":
    cli()
