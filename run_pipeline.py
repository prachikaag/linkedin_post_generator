#!/usr/bin/env python3
"""
LinkedIn Post Generator — Pipeline Runner

Fetches trending AI news, tracks what's buzzing, and writes research-backed
LinkedIn draft posts in your brand voice. Optionally publishes to Notion.

Quick start:
  cp .env.example .env       # fill in ANTHROPIC_API_KEY
  python run_pipeline.py     # generate 2 posts (default)

Usage:
  python run_pipeline.py                    # generate 2 posts
  python run_pipeline.py --max-posts 3      # generate 3 posts
  python run_pipeline.py --dry-run          # score news only, skip post generation
  python run_pipeline.py --no-notion        # skip Notion even if configured

Configuration files (all in config/):
  config/topics.yaml    — companies, keywords, freshness settings
  config/brand_kit.yaml — your voice, tone, post structure, hashtags
  config/sources.yaml   — RSS feeds and news sources

Edit any of those files and rerun — no restart needed.

Dependencies: only Python stdlib + PyYAML (pip install pyyaml)
Optional: python-dotenv (pip install python-dotenv) for automatic .env loading
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# ── .env loader ───────────────────────────────────────────────────────────
# Uses python-dotenv if installed, falls back to a simple manual reader.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    _env_path = Path(__file__).parent / ".env"
    if _env_path.exists():
        for _line in _env_path.read_text(encoding="utf-8").splitlines():
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

import yaml

from pipeline.news_fetcher import fetch_feeds
from pipeline.article_scorer import score_articles
from pipeline.trending_tracker import get_trending_keywords
from pipeline.post_generator import generate_post, save_post
from pipeline.notion_publisher import publish_to_notion

ROOT = Path(__file__).parent
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def load_config() -> tuple[dict, dict, dict]:
    with open(ROOT / "config/sources.yaml", encoding="utf-8") as f:
        sources = yaml.safe_load(f)
    with open(ROOT / "config/topics.yaml", encoding="utf-8") as f:
        topics = yaml.safe_load(f)
    with open(ROOT / "config/brand_kit.yaml", encoding="utf-8") as f:
        brand = yaml.safe_load(f)
    return sources, topics, brand


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LinkedIn Post Generator — AI-powered pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--max-posts", type=int, default=2, metavar="N",
                        help="Number of posts to generate (default: 2)")
    parser.add_argument("--articles-per-post", type=int, default=6, metavar="N",
                        help="Articles per post cluster (default: 6)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and score news only — skip post generation")
    parser.add_argument("--no-notion", action="store_true",
                        help="Skip Notion publishing even if NOTION_PAGE_ID is configured")
    args = parser.parse_args()

    print()
    print("  LinkedIn Post Generator")
    print("  " + "─" * 40)

    # ── Config ────────────────────────────────────────────────
    sources, topics, brand = load_config()
    freshness = topics.get("freshness", {})
    max_age = freshness.get("max_article_age_hours", 48)
    min_score = freshness.get("min_relevance_score", 2)
    max_articles = freshness.get("max_articles_per_run", 25)

    # ── API key ───────────────────────────────────────────────
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6").strip()

    if not api_key and not args.dry_run:
        print()
        print("  ERROR: ANTHROPIC_API_KEY is not set.")
        print("  Copy .env.example → .env and add your key.")
        print("  (Inside Claude Code, use the orchestrator.md approach instead.)")
        sys.exit(1)

    # ── Step 1: Fetch and score news ──────────────────────────
    print()
    print("  [1/4]  Fetching news from RSS feeds...")
    try:
        raw = fetch_feeds(sources, max_age_hours=max_age)
    except Exception as exc:
        print(f"         WARNING: RSS fetch failed: {exc}")
        raw = []

    articles = score_articles(raw, topics, min_score, max_articles)
    print(f"         ✓ {len(articles)} relevant article(s) scored")

    if not articles:
        print()
        print("  No relevant articles found.")
        print("  Tip: increase max_article_age_hours or lower min_relevance_score")
        print("       in config/topics.yaml")
        sys.exit(0)

    if args.dry_run:
        print()
        print("  Top articles (dry run — no posts generated):")
        print()
        for a in articles[:15]:
            score = a.get("relevance_score", 0)
            title = a.get("title", "")[:72]
            src = a.get("source_name", "")
            date = (a.get("published") or "")[:10]
            print(f"  [{score:2d}]  {title}")
            print(f"         {src}  |  {date}")
        print()
        return

    # ── Step 2: Trending keywords ─────────────────────────────
    print()
    print("  [2/4]  Getting trending keywords...")
    seed_terms = topics.get("trending_keywords", {}).get("seed_terms", [])
    trending = get_trending_keywords(api_key, seed_terms, model=model)
    print(f"         ✓ {', '.join(trending[:8])}")

    # ── Step 3: Generate posts ────────────────────────────────
    n_posts = min(args.max_posts, len(articles))
    pool = args.articles_per_post
    posts_dir = ROOT / "posts"
    results: list[dict] = []

    print()
    print(f"  [3/4]  Generating {n_posts} post(s)...")

    for i in range(n_posts):
        start = min(i, max(0, len(articles) - pool))
        cluster = articles[start : start + pool]

        # Anchor article (articles[i]) goes first
        anchor = articles[i]
        cluster = [anchor] + [a for a in cluster if a.get("url") != anchor.get("url")]

        print()
        print(f"         Post {i + 1}/{n_posts}")
        print(f"         Anchor : {anchor.get('title', '')[:65]}")
        print(f"         Sources: {', '.join(a.get('source_name', '') for a in cluster[:4])}")

        result = generate_post(api_key, cluster, trending, brand, model=model)

        if result:
            saved = save_post(result, posts_dir)
            if saved:
                fname = result.get("filename", "?")
                srcs = result.get("source_count", 0)
                print(f"         ✓ Saved → {fname}  ({srcs} sources)")
                results.append(result)
            else:
                print("         ✗ Failed to save (missing filename or content in response)")
        else:
            print("         ✗ Post generation failed — skipping this cluster")

    # ── Step 4: Notion ────────────────────────────────────────
    notion_page_id = os.getenv("NOTION_PAGE_ID", "").strip()
    notion_api_key = os.getenv("NOTION_API_KEY", "").strip()

    print()
    print("  [4/4]  Notion publishing...")

    if results and not args.no_notion and notion_page_id and notion_api_key:
        success = 0
        for r in results:
            ok = publish_to_notion(
                article_title=r.get("article_title", "LinkedIn Post"),
                content=r.get("content", ""),
                source_count=r.get("source_count", 0),
                page_id=notion_page_id,
                api_key=notion_api_key,
            )
            if ok:
                success += 1
        print(f"         ✓ {success}/{len(results)} post(s) added to Notion")
    elif not notion_page_id:
        print("         Skipped — set NOTION_PAGE_ID + NOTION_API_KEY in .env to enable")
    elif not notion_api_key:
        print("         Skipped — NOTION_API_KEY not set in .env")
    else:
        print("         Skipped (--no-notion flag)")

    # ── Summary ───────────────────────────────────────────────
    print()
    print("  " + "═" * 52)
    print("  LinkedIn Post Generator — Run Complete")
    print("  " + "═" * 52)
    print(f"  Posts generated : {len(results)}")
    print(f"  Saved to        : posts/")
    if results:
        for r in results:
            fname = r.get("filename", "?")
            srcs = r.get("source_count", 0)
            print(f"  {fname}  ·  {srcs} sources")
    print("  " + "═" * 52)
    print()


if __name__ == "__main__":
    main()
