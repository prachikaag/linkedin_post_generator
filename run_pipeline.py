"""Minimal runner — no click/rich required. Uses Claude MCP connectors."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path
import yaml

BASE = Path(__file__).parent
CONFIG = BASE / "config"
POSTS  = BASE / "posts"

def load(name):
    with open(CONFIG / name) as f:
        return yaml.safe_load(f)

def main():
    print("=" * 60)
    print("LinkedIn Post Generator — MCP Edition")
    print("=" * 60)

    sources  = load("sources.yaml")
    topics   = load("topics.yaml")
    brand    = load("brand_kit.yaml")

    # ── Step 1: fetch news via Claude WebFetch ──────────────────────────────
    print("\n[Step 1] Fetching news via Claude WebFetch MCP...")
    from src.article_history import ArticleHistory
    from src.news_gatherer import NewsGatherer

    history = ArticleHistory()
    expired = history.purge_expired()
    if expired:
        print(f"  → Purged {expired} expired history entries")

    gatherer = NewsGatherer(sources, topics)
    articles = gatherer.fetch_all()

    # Filter articles already used in previous runs
    fresh = [a for a in articles if not history.is_used(a.url)]
    skipped = len(articles) - len(fresh)
    if skipped:
        print(f"  → Skipped {skipped} article(s) already used in prior runs")
    articles = fresh

    if not articles:
        print("No new articles found. Try lowering min_relevance_score in config/topics.yaml")
        return

    print(f"  → {len(articles)} fresh articles found")
    for a in articles[:6]:
        print(f"     [{a.relevance_score}] {a.title[:70]} ({a.source_name})")

    # ── Step 2: trending keywords via Claude WebSearch ──────────────────────
    print("\n[Step 2] Fetching trending keywords via Claude WebSearch MCP...")
    from src.trending_tracker import TrendingTracker
    tracker = TrendingTracker(topics)
    trending = tracker.get_trending_keywords()
    print(f"  → Trending: {', '.join(trending[:8])}")

    # ── Step 3: generate posts ──────────────────────────────────────────────
    from src.post_generator import PostGenerator

    SOURCE_POOL = 6
    MAX_POSTS   = 2

    def make_cluster(articles, anchor_idx, pool):
        start = min(anchor_idx, max(0, len(articles) - pool))
        cluster = articles[start : start + pool]
        anchor  = articles[anchor_idx]
        if anchor in cluster and cluster[0] != anchor:
            cluster.remove(anchor)
            cluster.insert(0, anchor)
        return cluster

    POSTS.mkdir(exist_ok=True)
    generator = PostGenerator(brand, POSTS)
    generated = []

    n_posts = min(MAX_POSTS, len(articles))
    print(f"\n[Step 3] Generating {n_posts} research post(s) ({SOURCE_POOL} sources each)...")

    for i in range(n_posts):
        cluster = make_cluster(articles, i, SOURCE_POOL)
        anchor  = cluster[0]
        print(f"\n  Post {i+1} — anchor: {anchor.title[:65]}")
        print(f"  Sources: {', '.join(a.source_name for a in cluster[:4])}")

        result = generator.generate_post(cluster, trending)
        if result:
            generated.append(result)
            history.mark_used([a.url for a in cluster])
            print(f"  ✓ Saved → {result['filename']} ({result['source_count']} sources)")
        else:
            print("  ✗ Generation failed")

    # ── Step 4: push to Notion ──────────────────────────────────────────────
    from src.notion_publisher import NotionPublisher
    notion = NotionPublisher()
    if notion.is_configured():
        print("\n[Step 4] Publishing to Notion...")
        pushed = notion.publish_batch(generated)
        print(f"  → {pushed}/{len(generated)} post(s) added to Notion")
    else:
        print("\n[Step 4] Notion not configured — set NOTION_PAGE_ID in .env to enable")

    # ── Summary ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"Done — {len(generated)} post(s) saved to /posts/")
    for r in generated:
        print(f"\n--- {r['filename']} ---")
        print(r["content"][:800])
        if len(r["content"]) > 800:
            print("  [... truncated — open the file for the full post]")
    print("=" * 60)

if __name__ == "__main__":
    main()
