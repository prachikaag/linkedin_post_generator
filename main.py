#!/usr/bin/env python3
"""
LinkedIn Post Generator
=======================
Fetches trending AI news, finds what's buzzing, and writes research-backed
LinkedIn draft posts in your brand voice — saved to posts/ as markdown files.

Usage:
  python main.py                    # Generate 2 posts (default)
  python main.py --posts 3          # Generate 3 posts
  python main.py --dry-run          # Fetch and rank news only, no post generation
  python main.py --no-notion        # Skip Notion even if configured
  python main.py --pool-size 8      # Articles per post cluster (default: 6)

Setup:
  cp .env.example .env
  # then fill in ANTHROPIC_API_KEY (required) and optionally NOTION_* keys
"""

import argparse
import os
import sys
from typing import Dict, List


# ── .env loader ─────────────────────────────────────────────────────────────
# Reads key=value pairs from .env without requiring python-dotenv.

def _load_dotenv(path: str = ".env") -> None:
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, raw_value = line.partition("=")
                key = key.strip()
                value = raw_value.strip().strip('"').strip("'")
                # Never overwrite values already set in the real environment
                if key and key not in os.environ:
                    os.environ[key] = value
    except FileNotFoundError:
        pass  # .env is optional


_load_dotenv()


# ── Clustering ───────────────────────────────────────────────────────────────

def _cluster_articles(
    articles: List[Dict], n_posts: int, pool_size: int
) -> List[List[Dict]]:
    """
    Divide the article list into n_posts clusters.
    Each cluster has a distinct anchor article placed first.
    """
    clusters = []
    for i in range(min(n_posts, len(articles))):
        start = min(i, max(0, len(articles) - pool_size))
        cluster = list(articles[start : start + pool_size])
        anchor = articles[i]
        if anchor in cluster:
            cluster.remove(anchor)
        cluster.insert(0, anchor)
        clusters.append(cluster)
    return clusters


# ── Pipeline steps ────────────────────────────────────────────────────────────

def _step_fetch_news(verbose: bool = True) -> List[Dict]:
    from src.news_gatherer import NewsGatherer

    return NewsGatherer().fetch(verbose=verbose)


def _step_trending(verbose: bool = True) -> List[str]:
    from src.trending_tracker import TrendingTracker

    return TrendingTracker().fetch(verbose=verbose)


def _step_generate(
    articles: List[Dict],
    trending: List[str],
    n_posts: int,
    pool_size: int,
    verbose: bool = True,
) -> List[Dict]:
    from src.post_generator import PostGenerator

    generator = PostGenerator()
    clusters = _cluster_articles(articles, n_posts, pool_size)
    results = []

    for i, cluster in enumerate(clusters, 1):
        anchor = cluster[0]
        if verbose:
            print(f"\n  Post {i}/{len(clusters)}")
            print(f"    Anchor : {anchor['title'][:72]}")
            print(f"    Sources: {', '.join(a['source_name'] for a in cluster[:4])}")

        result = generator.generate(cluster, trending)
        results.append(result)

        if verbose:
            print(f"    Saved  → {result['filepath']}  ({result['source_count']} sources)")

    return results


def _step_notion(results: List[Dict], verbose: bool = True) -> None:
    from src.notion_publisher import NotionPublisher

    publisher = NotionPublisher()
    if not publisher.is_configured():
        if verbose:
            print(
                "  Notion not configured.\n"
                "  Add NOTION_API_KEY and NOTION_PAGE_ID to .env to enable."
            )
        return

    success = 0
    for result in results:
        if publisher.publish(result):
            success += 1
        elif verbose:
            print(f"  [warn] Notion publish failed for: {result['filename']}")

    if verbose:
        print(f"  {success}/{len(results)} post(s) added to Notion.")


# ── Summary ───────────────────────────────────────────────────────────────────

def _print_summary(results: List[Dict]) -> None:
    w = 58
    print("\n" + "═" * w)
    print("  LinkedIn Post Generator — Run Complete")
    print("─" * w)
    print(f"  Posts generated : {len(results)}")
    print(f"  Saved to        : posts/")
    print("─" * w)
    for r in results:
        print(f"  {r['filename']}")
        print(f"    {r['source_count']} sources  ·  {r['source_name']}")
    print("═" * w)

    for i, r in enumerate(results, 1):
        print(f"\n{'─' * w}")
        print(f"POST {i}:  {r['article_title'][:68]}")
        print("─" * w)
        print(r["content"])


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate research-backed LinkedIn posts from AI news.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--posts", type=int, default=2, metavar="N",
        help="Number of posts to generate (default: 2)",
    )
    parser.add_argument(
        "--pool-size", type=int, default=6, metavar="N",
        help="Articles per post cluster (default: 6)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fetch + rank news only — no post generation",
    )
    parser.add_argument(
        "--no-notion", action="store_true",
        help="Skip Notion publishing even if configured",
    )
    args = parser.parse_args()

    print("\nLinkedIn Post Generator")
    print("=" * 58)

    # ── Step 1 ──────────────────────────────────────────────
    print("\n[1/4] Fetching news from RSS feeds...")
    articles = _step_fetch_news()

    if not articles:
        print(
            "\nNo relevant articles found.\n"
            "Try:\n"
            "  - Raising max_article_age_hours in config/topics.yaml\n"
            "  - Lowering min_relevance_score in config/topics.yaml\n"
            "  - Enabling more feeds in config/sources.yaml"
        )
        sys.exit(0)

    print(f"  → {len(articles)} relevant article(s) fetched and scored.")

    if args.dry_run:
        print("\nTop articles (dry-run — no posts generated):\n")
        for a in articles[:15]:
            print(f"  [{a['relevance_score']:2d}]  {a['title'][:72]}")
            print(f"        {a['source_name']}")
        sys.exit(0)

    # ── Step 2 ──────────────────────────────────────────────
    print("\n[2/4] Getting trending keywords...")
    trending = _step_trending()
    print(f"  → {', '.join(trending[:8])}")

    # ── Step 3 ──────────────────────────────────────────────
    print(f"\n[3/4] Generating {args.posts} post(s) with Claude...")
    results = _step_generate(articles, trending, args.posts, args.pool_size)

    # ── Step 4 ──────────────────────────────────────────────
    print("\n[4/4] Publishing to Notion...")
    if args.no_notion:
        print("  Skipped (--no-notion flag).")
    else:
        _step_notion(results)

    _print_summary(results)


if __name__ == "__main__":
    main()
