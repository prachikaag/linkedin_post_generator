#!/usr/bin/env python3
"""
LinkedIn Post Generator
-----------------------
Fetches trending AI news from RSS feeds, identifies what's buzzing across the
space, then uses Claude to write branded LinkedIn post drafts — all saved to
posts/ for your review before publishing.

Usage:
    python main.py                    # generate 2 posts
    python main.py --max-posts 3      # generate 3 posts
    python main.py --dry-run          # fetch + score news only, skip generation
    python main.py --model claude-opus-4-7   # use a different Claude model

Setup:
    1. cp .env.example .env
    2. Add your ANTHROPIC_API_KEY to .env
    3. Edit config/brand_kit.yaml — fill in your name, title, and tagline
    4. pip install -r requirements.txt
    5. python main.py
"""
import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional — set env vars directly or export them before running


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LinkedIn Post Generator — news → trends → branded post drafts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=2,
        metavar="N",
        help="Number of posts to generate (default: 2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and score news only — skip post generation",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        help="Claude model to use (default: claude-sonnet-4-6)",
    )
    args = parser.parse_args()

    from src.pipeline import Pipeline

    pipeline = Pipeline()
    results = pipeline.run(
        max_posts=args.max_posts,
        dry_run=args.dry_run,
        model=args.model,
    )

    sys.exit(0 if (results or args.dry_run) else 1)


if __name__ == "__main__":
    main()
