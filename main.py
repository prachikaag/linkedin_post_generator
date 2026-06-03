#!/usr/bin/env python3
"""
LinkedIn Post Generator
-----------------------
Fetches trending AI news, finds what's buzzing, and writes
research-backed LinkedIn post drafts in your voice.

Usage:
  python main.py                      # generate 2 posts (default)
  python main.py --max-posts 3        # generate 3 posts
  python main.py --dry-run            # fetch & score news only, no posts
  python main.py --skip-notion        # don't push to Notion

Configuration:
  config/topics.yaml   → what news to track
  config/brand_kit.yaml → your voice, tone, and style
  config/sources.yaml  → RSS feeds and news sources
  .env                 → API keys (copy from .env.example)
"""
import argparse
import sys
from pathlib import Path

# Make src/ importable when running as a script
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate research-backed LinkedIn posts from AI news.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=2,
        metavar="N",
        help="Number of posts to generate (default: 2)",
    )
    parser.add_argument(
        "--source-pool",
        type=int,
        default=6,
        metavar="N",
        help="Articles per post cluster (default: 6)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and rank news only — don't generate or save posts",
    )
    parser.add_argument(
        "--skip-notion",
        action="store_true",
        help="Skip Notion publishing even if NOTION_PAGE_ID is configured",
    )

    args = parser.parse_args()

    run(
        max_posts=args.max_posts,
        source_pool_size=args.source_pool,
        dry_run=args.dry_run,
        skip_notion=args.skip_notion,
    )


if __name__ == "__main__":
    main()
