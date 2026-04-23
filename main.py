#!/usr/bin/env python3
"""
LinkedIn Post Generator — CLI entry point.

Usage examples:
  python main.py                          # Full pipeline, generate 3 posts
  python main.py --posts 5               # Generate 5 posts
  python main.py --dry-run               # Fetch news without calling Claude
  python main.py --no-trends             # Skip Google Trends (faster)
  python main.py --no-skip-seen          # Re-process previously seen articles
  python main.py fetch                   # Only fetch and display news articles
  python main.py trends                  # Only show trending keywords
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def cmd_run(args: argparse.Namespace) -> None:
    from src.orchestrator import run_pipeline
    from src.post_generator import format_post_for_display

    posts = run_pipeline(
        post_count=args.posts,
        max_articles=args.max_articles,
        skip_seen=not args.no_skip_seen,
        fetch_trends=not args.no_trends,
        model=args.model,
        dry_run=args.dry_run,
    )

    if posts:
        print("\n" + "=" * 60)
        print(f"GENERATED {len(posts)} LINKEDIN POST(S)")
        print("=" * 60)
        for i, post in enumerate(posts, 1):
            print(format_post_for_display(post, i))


def cmd_fetch(args: argparse.Namespace) -> None:
    from src.news_fetcher import fetch_all

    print("Fetching latest news articles...")
    articles = fetch_all(
        max_articles=args.max_articles,
        skip_seen=not args.no_skip_seen,
    )

    if not articles:
        print("No new articles found.")
        return

    print(f"\nFound {len(articles)} relevant articles:\n")
    for i, art in enumerate(articles, 1):
        print(f"{i:02d}. [{art['source']}] {art['title']}")
        print(f"    {art.get('url', '')}")
        cats = ", ".join(art.get("matched_categories", []))
        print(f"    Categories: {cats}")
        print()


def cmd_trends(args: argparse.Namespace) -> None:
    from src.trending_tracker import get_trending_keywords

    print("Fetching trending AI keywords from Google Trends...")
    trending = get_trending_keywords(top_n=20)

    if not trending:
        print("No trend data available.")
        return

    print(f"\nTop {len(trending)} trending keywords:\n")
    for t in trending:
        bar = "█" * (t["score"] // 5)
        print(f"  {t['keyword']:<30} {t['score']:3d}  {bar}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LinkedIn Post Generator — AI news → on-brand posts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- Shared arguments ---
    def add_shared(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--max-articles",
            type=int,
            default=30,
            help="Max articles to fetch (default: 30)",
        )
        p.add_argument(
            "--no-skip-seen",
            action="store_true",
            help="Re-process articles that were already seen",
        )

    # --- Default command: full pipeline ---
    parser.add_argument("--posts", type=int, default=3, help="Number of posts to generate (default: 3)")
    parser.add_argument("--max-articles", type=int, default=30, help="Max articles to fetch (default: 30)")
    parser.add_argument("--no-skip-seen", action="store_true", help="Re-process previously seen articles")
    parser.add_argument("--no-trends", action="store_true", help="Skip Google Trends lookup")
    parser.add_argument("--dry-run", action="store_true", help="Fetch news but don't call Claude")
    parser.add_argument(
        "--model",
        default="claude-opus-4-7",
        help="Claude model to use (default: claude-opus-4-7)",
    )

    # --- Subcommand: fetch only ---
    fetch_p = subparsers.add_parser("fetch", help="Fetch and display news articles only")
    add_shared(fetch_p)

    # --- Subcommand: trends only ---
    trends_p = subparsers.add_parser("trends", help="Show trending AI keywords only")

    args = parser.parse_args()

    if args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "trends":
        cmd_trends(args)
    else:
        cmd_run(args)


if __name__ == "__main__":
    main()
