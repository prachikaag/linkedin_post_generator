"""
pipeline.py
Orchestrates the full news-to-LinkedIn-draft pipeline:
  1. Fetch and score AI news from RSS feeds
  2. Get trending AI keyword phrases
  3. Build article clusters (one per post)
  4. Generate each post via Claude API
  5. Optionally publish drafts to Notion
"""
from .config_loader import load_all
from .news_fetcher import fetch_articles
from .notion_publisher import publish_to_notion
from .post_generator import generate_post
from .trending_tracker import get_trending_keywords


def run(
    max_posts: int = 2,
    source_pool_size: int = 6,
    dry_run: bool = False,
    skip_notion: bool = False,
) -> list[dict]:
    """
    Run the full pipeline end-to-end.
    Returns a list of result dicts for each post generated.
    """
    config = load_all()

    # ── Step 1: Fetch news ─────────────────────────────────────────────────────
    print("Fetching AI news from RSS feeds...")
    articles = fetch_articles(config)

    if not articles:
        print(
            "No relevant articles found.\n"
            "Try increasing max_article_age_hours or lowering min_relevance_score "
            "in config/topics.yaml."
        )
        return []

    print(f"✓ {len(articles)} relevant articles fetched and scored.")

    if dry_run:
        print("\nDRY RUN — top articles (no posts generated):\n")
        for a in articles[:12]:
            print(f"  [{a['relevance_score']:>3}]  {a['title'][:68]}  ({a['source_name']})")
        return []

    # ── Step 2: Trending keywords ──────────────────────────────────────────────
    print("Finding trending AI keywords...")
    trending = get_trending_keywords(config)
    print(f"✓ Trending: {', '.join(trending[:8])}")

    # ── Step 3: Build article clusters ────────────────────────────────────────
    clusters = _build_clusters(articles, max_posts, source_pool_size)

    # ── Step 4 & 5: Generate posts + optional Notion ───────────────────────────
    notion_key = config.get("notion_api_key", "")
    notion_page = config.get("notion_page_id", "")
    results: list[dict] = []

    for i, cluster in enumerate(clusters):
        anchor = cluster[0]
        print(f"\nPost {i + 1} — {anchor['title'][:68]}")
        print(f"  Sources: {', '.join(a['source_name'] for a in cluster[:4])}")

        try:
            result = generate_post(cluster, trending, config)
            results.append(result)
            print(f"  ✓ Saved → {result['filename']}  ({result['source_count']} sources)")
        except Exception as exc:
            print(f"  ✗ Post generation failed: {exc}")
            continue

        if not skip_notion and notion_key and notion_page:
            ok = publish_to_notion(result, notion_page, notion_key)
            if ok:
                print("  ✓ Published to Notion")
        elif not skip_notion and notion_page and not notion_key:
            print("  ⚠  NOTION_PAGE_ID is set but NOTION_API_KEY is missing — skipping Notion.")

    # ── Summary ────────────────────────────────────────────────────────────────
    _print_summary(results)
    return results


# ── Clustering ────────────────────────────────────────────────────────────────

def _build_clusters(
    articles: list[dict], max_posts: int, pool_size: int
) -> list[list[dict]]:
    """
    Build one article cluster per post.
    Each cluster has a distinct anchor article at position 0,
    filled with the most relevant surrounding articles.
    """
    n_posts = min(max_posts, len(articles))
    clusters: list[list[dict]] = []

    for i in range(n_posts):
        start = min(i, max(0, len(articles) - pool_size))
        pool = articles[start : start + pool_size]
        anchor = articles[i]
        cluster = [anchor] + [a for a in pool if a["url"] != anchor["url"]]
        clusters.append(cluster)

    return clusters


# ── Summary ───────────────────────────────────────────────────────────────────

def _print_summary(results: list[dict]) -> None:
    w = 54
    print(f"\n{'═' * w}")
    print(f"  LinkedIn Post Generator — Run Complete")
    print(f"{'─' * w}")
    print(f"  Posts generated : {len(results)}")
    print(f"  Saved to        : posts/")
    if results:
        print(f"{'─' * w}")
        for r in results:
            print(f"  {r['filename']}  ·  {r['source_count']} sources")
    print(f"{'═' * w}\n")
