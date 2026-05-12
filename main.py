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
  python main.py config           # Show paths to all config files
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; set env vars manually if not installed

import yaml

BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config"
POSTS_DIR = BASE_DIR / "posts"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _read_frontmatter(post_file: Path) -> tuple:
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


def _hr(char="─", width=60):
    print(char * width)


# ── Commands ───────────────────────────────────────────────────────────────────

def cmd_run(args):
    """Run the full pipeline: fetch news → track trends → generate posts."""
    if not args.dry_run:
        has_claude_cli = shutil.which("claude") is not None
        has_api_key = bool(os.getenv("ANTHROPIC_API_KEY"))
        if not has_claude_cli and not has_api_key:
            print(
                "Error: No Claude access found.\n\n"
                "Either:\n"
                "  A) Run inside Claude Code — the 'claude' CLI is detected automatically.\n"
                "  B) Set ANTHROPIC_API_KEY in your .env file (copy from .env.example)."
            )
            sys.exit(1)
        if has_claude_cli:
            print("Using Claude Code CLI connection (no API key needed).")
        else:
            print("Using Anthropic API key from .env")

    from src.pipeline import Pipeline
    pipeline = Pipeline(CONFIG_DIR, POSTS_DIR)
    pipeline.run(max_posts=args.max_posts, dry_run=args.dry_run)


def cmd_list_posts(_args):
    """List all generated draft posts in the /posts directory."""
    posts = sorted(POSTS_DIR.glob("*.md"))
    if not posts:
        print("No posts found. Run 'python main.py run' to generate some.")
        return

    _hr()
    print(f"  {'#':>3}  {'Date':<12}  {'Status':<10}  {'Companies':<28}  Filename")
    _hr()
    for i, post_file in enumerate(posts, 1):
        date, status, companies = _read_frontmatter(post_file)
        print(f"  {i:>3}  {date:<12}  {status:<10}  {companies[:28]:<28}  {post_file.name}")
    _hr()
    print(f"\nUse 'python main.py show <number>' to read a post.")


def cmd_show(args):
    """Show a draft post by number or filename."""
    if args.file:
        post_file = POSTS_DIR / args.file
        if not post_file.exists():
            print(f"File not found: {args.file}")
            sys.exit(1)
    elif args.number:
        posts = sorted(POSTS_DIR.glob("*.md"))
        if args.number < 1 or args.number > len(posts):
            print(
                f"Invalid post number {args.number}. "
                f"There are {len(posts)} post(s). Run 'list-posts' to see them."
            )
            sys.exit(1)
        post_file = posts[args.number - 1]
    else:
        print("Provide a post number or --file <filename>.\nExample: python main.py show 1")
        sys.exit(1)

    raw = post_file.read_text(encoding="utf-8")

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

    _hr("═")
    print(f"  {post_file.name}")
    _hr("═")
    if meta.get("source_name"):
        print(f"  Source   : {meta['source_name']}")
    if meta.get("matched_companies"):
        print(f"  Companies: {', '.join(meta['matched_companies'])}")
    if meta.get("trending_keywords"):
        print(f"  Trending : {', '.join(meta['trending_keywords'])}")
    if meta.get("primary_source_url"):
        print(f"  URL      : {meta['primary_source_url']}")
    print(f"  Status   : {meta.get('status', 'draft')}")
    _hr()
    print()
    print(body)
    print()
    _hr("═")


def cmd_config(_args):
    """Show the paths to all editable config files."""
    print("\nEditable Configuration Files\n")
    files = {
        "Topics of Interest     ": CONFIG_DIR / "topics.yaml",
        "Brand Kit & Tone Voice ": CONFIG_DIR / "brand_kit.yaml",
        "News Sources (RSS)     ": CONFIG_DIR / "sources.yaml",
        "Environment Variables  ": BASE_DIR / ".env",
    }
    for label, path in files.items():
        exists = "✓" if path.exists() else "✗ missing"
        print(f"  [{exists}]  {label}  {path}")
    print()


# ── Argument parser ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="LinkedIn Post Generator — AI-powered drafts from trending AI news.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    # run
    p_run = sub.add_parser("run", help="Full pipeline: fetch news → track trends → generate posts")
    p_run.add_argument(
        "--max-posts", type=int, default=3, metavar="N",
        help="Maximum number of posts to generate (default: 3)",
    )
    p_run.add_argument(
        "--dry-run", action="store_true",
        help="Fetch and rank news only — skip post generation",
    )

    # list-posts
    sub.add_parser("list-posts", help="List all saved draft posts")

    # show
    p_show = sub.add_parser("show", help="Show a draft post by number or filename")
    p_show.add_argument("number", type=int, nargs="?", help="Post number from list-posts")
    p_show.add_argument("--file", "-f", metavar="FILENAME", help="Exact filename in posts/")

    # config
    sub.add_parser("config", help="Show paths to all config files")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "run": cmd_run,
        "list-posts": cmd_list_posts,
        "show": cmd_show,
        "config": cmd_config,
    }

    if args.command not in dispatch:
        parser.print_help()
        sys.exit(1)

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
