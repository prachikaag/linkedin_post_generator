"""LinkedIn Post Generator — main pipeline runner."""
import argparse
import json
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = Path(__file__).parent / "config"
POSTS_DIR = Path(__file__).parent / "posts"


def load_yaml(filename: str) -> dict:
    path = CONFIG_DIR / filename
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def make_cluster(articles: list, anchor_idx: int, pool_size: int) -> list[dict]:
    """Return up to pool_size articles centred on the anchor article."""
    anchor = articles[anchor_idx]
    pool = [anchor.to_dict()]
    candidates = [a for i, a in enumerate(articles) if i != anchor_idx]

    # Prefer articles that share a matched company or category with the anchor
    anchor_companies = set(anchor.matched_companies)
    anchor_categories = set(anchor.matched_categories)

    def score(a):
        shared = len(set(a.matched_companies) & anchor_companies)
        shared += len(set(a.matched_categories) & anchor_categories)
        return shared

    candidates.sort(key=score, reverse=True)
    for candidate in candidates:
        if len(pool) >= pool_size:
            break
        pool.append(candidate.to_dict())

    return pool


def main():
    parser = argparse.ArgumentParser(description="Generate LinkedIn posts from AI news")
    parser.add_argument("--max-posts", type=int, default=2, help="Number of posts to generate (default: 2)")
    parser.add_argument("--pool-size", type=int, default=6, help="Articles per post cluster (default: 6)")
    parser.add_argument("--dry-run", action="store_true", help="Fetch news and show articles but skip post generation")
    parser.add_argument("--no-notion", action="store_true", help="Skip Notion publishing even if configured")
    args = parser.parse_args()

    print("=== LinkedIn Post Generator ===\n")

    # Load configs
    sources_config = load_yaml("sources.yaml")
    topics_config = load_yaml("topics.yaml")
    brand_config = load_yaml("brand_kit.yaml")

    # Step 1: Fetch news
    print("Step 1/3 — Fetching news from RSS feeds...")
    from src.news_gatherer import NewsGatherer
    gatherer = NewsGatherer(sources_config, topics_config)
    articles = gatherer.fetch_all()
    print(f"  Found {len(articles)} relevant articles\n")

    if not articles:
        print("No relevant articles found. Try expanding topics.yaml or increasing max_article_age_hours.")
        sys.exit(0)

    if args.dry_run:
        print("--- DRY RUN: top articles ---")
        for i, a in enumerate(articles[:10], 1):
            print(f"  [{i}] (score={a.relevance_score}) {a.source_name}: {a.title}")
        sys.exit(0)

    # Step 2: Trending keywords
    print("Step 2/3 — Fetching trending keywords...")
    from src.trend_tracker import TrendingTracker
    tracker = TrendingTracker(topics_config)
    trending = tracker.get_trending_keywords()
    print(f"  {len(trending)} trending phrases found")
    print(f"  Top 5: {', '.join(trending[:5])}\n")

    # Step 3: Generate posts
    print(f"Step 3/3 — Generating up to {args.max_posts} post(s)...")
    from src.post_generator import PostGenerator
    generator = PostGenerator(brand_config, POSTS_DIR)

    generated_posts = []
    anchors_used: set[int] = set()

    for post_num in range(args.max_posts):
        # Pick next anchor — highest-scoring article not yet used
        anchor_idx = None
        for i in range(len(articles)):
            if i not in anchors_used:
                anchor_idx = i
                break
        if anchor_idx is None:
            break

        anchors_used.add(anchor_idx)
        cluster = make_cluster(articles, anchor_idx, args.pool_size)

        print(f"\n[Post {post_num + 1}/{args.max_posts}] Anchor: {cluster[0]['title'][:60]}...")
        print(f"  Cluster size: {len(cluster)} articles")

        result = generator.generate_post(cluster, trending)
        if result:
            generated_posts.append(result)
            print(f"  Saved → {result['filepath']}")

    # Summary
    print(f"\n=== Done: {len(generated_posts)} post(s) generated ===")
    for post in generated_posts:
        print(f"  - {post['filename']} ({post['source_count']} sources)")

    # Notion publishing
    if generated_posts and not args.no_notion:
        from src.notion_publisher import NotionPublisher
        publisher = NotionPublisher()
        if publisher.is_configured():
            print(f"\nPublishing {len(generated_posts)} post(s) to Notion...")
            published = publisher.publish_batch(generated_posts)
            print(f"  Published {published}/{len(generated_posts)} to Notion")
        else:
            print("\nNotion not configured — skipping. Set NOTION_API_KEY and NOTION_PAGE_ID in .env to enable.")


if __name__ == "__main__":
    main()
