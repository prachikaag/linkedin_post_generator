#!/usr/bin/env python3
"""
LinkedIn Post Generator — Standalone runner
Calls the orchestrator pipeline via the Anthropic Claude API.

Usage:
  python run_pipeline.py
  python run_pipeline.py --posts 3
  python run_pipeline.py --dry-run
  python run_pipeline.py --post-type startup_funding
  python run_pipeline.py --posts 2 --post-type feature_launch

Environment:
  Set ANTHROPIC_API_KEY in .env (or export it in your shell).
  Optionally set NOTION_PAGE_ID in .env for Notion publishing.
"""

import os
import sys
import argparse
from pathlib import Path

# ── Resolve project root ────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()

def load_env():
    """Load .env file from project root into os.environ."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

def read_orchestrator_prompt() -> str:
    """Read orchestrator.md and return its content."""
    path = PROJECT_ROOT / "orchestrator.md"
    if not path.exists():
        sys.exit("ERROR: orchestrator.md not found. Run from the project root.")
    return path.read_text()

def build_user_prompt(max_posts: int, source_pool: int, dry_run: bool, post_type: str | None) -> str:
    """Build the natural-language instruction for the orchestrator."""
    parts = [f"Run the LinkedIn Post Generator pipeline. Generate {max_posts} post(s)."]
    parts.append(f"Use {source_pool} articles per post cluster.")
    if dry_run:
        parts.append("Run in dry-run mode — fetch and rank news only, do not generate posts.")
    if post_type:
        valid = {"feature_launch", "startup_funding", "big_tech_ai", "youtube_release", "personal_experiment"}
        if post_type not in valid:
            sys.exit(f"ERROR: --post-type must be one of: {', '.join(sorted(valid))}")
        parts.append(f"Force post type: {post_type}")
    return " ".join(parts)

def run(max_posts: int = 2, source_pool: int = 6, dry_run: bool = False, post_type: str | None = None):
    """Run the pipeline via the Claude API SDK."""
    load_env()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "ERROR: ANTHROPIC_API_KEY is not set.\n"
            "  1. Copy .env.example to .env\n"
            "  2. Add your key: ANTHROPIC_API_KEY=sk-ant-...\n"
            "  Or export it in your shell: export ANTHROPIC_API_KEY=sk-ant-..."
        )

    try:
        import anthropic
    except ImportError:
        sys.exit(
            "ERROR: anthropic package not installed.\n"
            "  Run: pip install anthropic"
        )

    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    orchestrator_prompt = read_orchestrator_prompt()
    user_prompt = build_user_prompt(max_posts, source_pool, dry_run, post_type)

    client = anthropic.Anthropic(api_key=api_key)

    print("=" * 60)
    print("  LinkedIn Post Generator")
    print("=" * 60)
    print(f"  Model      : {model}")
    print(f"  Posts      : {max_posts}")
    print(f"  Pool size  : {source_pool} articles per cluster")
    print(f"  Dry run    : {dry_run}")
    print(f"  Post type  : {post_type or 'auto-detect'}")
    print("=" * 60)
    print()

    with client.messages.stream(
        model=model,
        max_tokens=8192,
        system=orchestrator_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print()
    print()
    print("=" * 60)
    print("  Done. Check posts/ for generated drafts.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Post Generator — run the full AI news-to-draft pipeline"
    )
    parser.add_argument(
        "--posts", "-n",
        type=int,
        default=2,
        metavar="N",
        help="Number of posts to generate (default: 2)",
    )
    parser.add_argument(
        "--pool",
        type=int,
        default=6,
        metavar="N",
        help="Articles per post cluster (default: 6)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and score news only — do not generate posts",
    )
    parser.add_argument(
        "--post-type",
        choices=["feature_launch", "startup_funding", "big_tech_ai", "youtube_release", "personal_experiment"],
        default=None,
        metavar="TYPE",
        help="Force a specific post type for all posts this run",
    )
    args = parser.parse_args()
    run(
        max_posts=args.posts,
        source_pool=args.pool,
        dry_run=args.dry_run,
        post_type=args.post_type,
    )


if __name__ == "__main__":
    main()
