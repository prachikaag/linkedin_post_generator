"""
Orchestrator: ties together news fetching, trend tracking,
and post generation into a single pipeline run.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from .news_fetcher import fetch_all
from .post_generator import format_post_for_display, generate_posts
from .trending_tracker import get_trending_keywords, summarise_trends

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


def _save_run(articles: list[dict], trending: list[dict], posts: list[dict]) -> Path:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_file = OUTPUTS_DIR / f"run_{timestamp}.json"
    with open(run_file, "w") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "articles_fetched": len(articles),
                "trending_keywords": trending,
                "posts": posts,
                "articles": articles,
            },
            f,
            indent=2,
            default=str,
        )
    return run_file


def _save_posts_markdown(posts: list[dict], timestamp: str) -> Path:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    md_file = OUTPUTS_DIR / f"posts_{timestamp}.md"
    lines = [f"# LinkedIn Posts — {timestamp}\n"]
    for i, post in enumerate(posts, 1):
        lines += [
            f"## Post {i}",
            f"**Angle:** {post.get('content_angle', '')}",
            f"**Headline:** {post.get('headline', '')}",
            "",
            post.get("post", ""),
            "",
            f"**Sources:** {', '.join(post.get('sources_cited', []))}",
            f"**Image prompt:** {post.get('suggested_image_prompt', '')}",
            "\n---\n",
        ]
    md_file.write_text("\n".join(lines))
    return md_file


def run_pipeline(
    post_count: int = 3,
    max_articles: int = 30,
    skip_seen: bool = True,
    fetch_trends: bool = True,
    model: str = "claude-opus-4-7",
    dry_run: bool = False,
) -> list[dict]:
    """
    Full pipeline: fetch news → get trends → generate posts → save output.
    Returns list of generated post dicts.
    """
    DATA_DIR.mkdir(exist_ok=True)

    # Step 1: Fetch news
    print("\n[1/3] Fetching relevant news articles...")
    articles = fetch_all(max_articles=max_articles, skip_seen=skip_seen)
    if not articles:
        print("  No new articles found. Try running with --no-skip-seen to re-process all articles.")
        return []
    print(f"  Selected {len(articles)} articles for post generation")

    # Step 2: Get trending keywords
    print("\n[2/3] Checking trending keywords...")
    trending = []
    if fetch_trends:
        trending = get_trending_keywords(top_n=15)
        print(f"  {summarise_trends(trending)}")
    else:
        print("  Skipped (--no-trends flag set)")

    if dry_run:
        print("\n[DRY RUN] Would generate posts for these articles:")
        for i, art in enumerate(articles[:5], 1):
            print(f"  {i}. {art['title']} [{art['source']}]")
        return []

    # Step 3: Generate posts
    print(f"\n[3/3] Generating {post_count} LinkedIn post(s) with Claude...")
    posts = generate_posts(articles, trending, post_count=post_count, model=model)

    # Step 4: Save outputs
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_file = _save_run(articles, trending, posts)
    md_file = _save_posts_markdown(posts, timestamp)

    print(f"\n  Saved full run data → {run_file.relative_to(Path.cwd()) if run_file.is_relative_to(Path.cwd()) else run_file}")
    print(f"  Saved posts markdown → {md_file.relative_to(Path.cwd()) if md_file.is_relative_to(Path.cwd()) else md_file}")

    return posts
