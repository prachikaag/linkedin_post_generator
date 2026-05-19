from pathlib import Path

from .config_loader import BASE_DIR, load_brand_kit, load_sources, load_topics
from .news_gatherer import NewsGatherer
from .notion_publisher import NotionPublisher
from .post_generator import PostGenerator
from .trend_tracker import TrendingTracker

SOURCE_POOL_SIZE = 6  # articles per post cluster — ensures 4+ citable sources


class Pipeline:
    """Orchestrates the full news → trends → post generation workflow."""

    def __init__(self, config_dir: Path = None, posts_dir: Path = None):
        self.config_dir = config_dir or BASE_DIR / "config"
        self.posts_dir = posts_dir or BASE_DIR / "posts"
        self.topics = load_topics()
        self.brand_kit = load_brand_kit()
        self.sources = load_sources()

    def run(
        self,
        max_posts: int = 2,
        dry_run: bool = False,
        model: str = "claude-sonnet-4-6",
    ) -> list[dict]:
        _hr()
        print("  LinkedIn Post Generator")
        _hr()

        # ── Step 1: Fetch and score news ───────────────────────────────────────
        print("\n[1/3] Fetching news from RSS feeds...")
        gatherer = NewsGatherer(self.sources, self.topics)
        articles = gatherer.fetch_all()

        if not articles:
            print("  No relevant articles found.")
            print(
                "  → Try increasing max_article_age_hours or lowering min_relevance_score"
                " in config/topics.yaml"
            )
            return []

        print(f"  ✓ {len(articles)} relevant articles fetched and scored.")

        if dry_run:
            print("\n  Top articles (dry run — stopping before post generation):\n")
            for a in articles[:12]:
                print(f"  [{a.relevance_score:2d}] {a.title[:72]}")
                print(f"       {a.source_name}")
            return []

        # ── Step 2: Trending keywords ──────────────────────────────────────────
        print("\n[2/3] Getting trending keywords...")
        tracker = TrendingTracker(self.topics)
        keywords = tracker.get_trending_keywords()
        print(f"  ✓ Trending: {', '.join(keywords[:8])}")

        # ── Step 3: Generate posts ─────────────────────────────────────────────
        n_posts = min(max_posts, len(articles))
        print(f"\n[3/3] Generating {n_posts} post(s)...")
        generator = PostGenerator(self.brand_kit, self.posts_dir, model=model)

        results: list[dict] = []
        for i in range(n_posts):
            start = min(i, max(0, len(articles) - SOURCE_POOL_SIZE))
            cluster = list(articles[start : start + SOURCE_POOL_SIZE])

            # Ensure the anchor article is first in the cluster
            if articles[i] not in cluster:
                cluster.insert(0, articles[i])
            cluster = cluster[:SOURCE_POOL_SIZE]

            anchor = cluster[0].title[:65]
            sources_str = ", ".join(a.source_name for a in cluster[:4])
            print(f"\n  Post {i + 1} — {anchor}")
            print(f"  Sources: {sources_str}")

            result = generator.generate_post(cluster, keywords)
            if result:
                print(f"  ✓ Saved → {result['filename']} ({result['source_count']} sources)")
                results.append(result)
            else:
                print(f"  ✗ Post {i + 1} failed — skipping")

        # ── Step 4: Notion publishing (optional) ──────────────────────────────
        publisher = NotionPublisher()
        if publisher.is_configured:
            success = 0
            for r in results:
                try:
                    ok = publisher.publish(
                        r["article_title"], r["content"], r["source_count"]
                    )
                    if ok:
                        success += 1
                except Exception as exc:
                    print(f"  [warn] Notion: {exc}")
            print(f"\n  ✓ {success}/{len(results)} post(s) added to Notion.")
        else:
            print(
                "\n  Notion not configured."
                " Set NOTION_PAGE_ID and NOTION_API_KEY in .env to enable."
            )

        # ── Summary ────────────────────────────────────────────────────────────
        print()
        _hr()
        print(f"  Posts generated : {len(results)}")
        print(f"  Saved to        : posts/")
        _hr()
        for r in results:
            print(f"  {r['filename']}  ·  {r['source_count']} sources")
        _hr()

        # Print each post for immediate review
        if results:
            print()
            for r in results:
                print(f"\n{'─' * 56}")
                print(f"  {r['filename']}")
                print(f"{'─' * 56}\n")
                print(r["content"])
                print()

        return results


def _hr() -> None:
    print("═" * 56)
