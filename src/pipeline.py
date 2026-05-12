from pathlib import Path

import yaml

from .news_gatherer import Article, NewsGatherer
from .notion_publisher import NotionPublisher
from .post_generator import PostGenerator
from .trending_tracker import TrendingTracker

# Each post is generated from this many articles (ensures 4+ citable sources)
SOURCE_POOL_SIZE = 6


def _rule(label="", width=60):
    if label:
        pad = max(0, width - len(label) - 2)
        print(f"{'─' * (pad // 2)} {label} {'─' * (pad - pad // 2)}")
    else:
        print("─" * width)


class Pipeline:
    """Orchestrates the full news → trends → post generation workflow."""

    def __init__(self, config_dir: Path, posts_dir: Path):
        self.config_dir = config_dir
        self.posts_dir = posts_dir
        self.topics = self._load_yaml("topics.yaml")
        self.brand_kit = self._load_yaml("brand_kit.yaml")
        self.sources = self._load_yaml("sources.yaml")

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self, max_posts: int = 3, dry_run: bool = False) -> list:
        """
        Full pipeline:
          1. Fetch and score news articles from RSS feeds
          2. Fetch trending keywords from Google Trends / WebSearch
          3. Build article clusters (SOURCE_POOL_SIZE articles each)
          4. Generate one research-style post per cluster (min 4 sources each)
          5. Save all posts as markdown drafts for human review
        """
        _rule("LinkedIn Post Generator")

        # ── Step 1: News ────────────────────────────────────────────────────
        print("\n[Step 1 / 3] Fetching news...")
        gatherer = NewsGatherer(self.sources, self.topics)
        articles = gatherer.fetch_all()

        if not articles:
            print(
                "No relevant articles found.\n"
                "Try increasing max_article_age_hours in config/topics.yaml "
                "or lowering min_relevance_score."
            )
            return []

        print(f"  ✓ {len(articles)} relevant articles fetched and scored.")
        self._display_articles(articles[: SOURCE_POOL_SIZE * 2])

        if dry_run:
            print("\nDry-run mode — skipping post generation.")
            return []

        # ── Step 2: Trending keywords ───────────────────────────────────────
        print("\n[Step 2 / 3] Fetching trending keywords...")
        tracker = TrendingTracker(self.topics)
        trending = tracker.get_trending_keywords()
        if trending:
            print(f"  ✓ Trending: {', '.join(trending[:8])}")
        else:
            print("  No trending data — using seed terms.")

        # ── Step 3: Generate posts ──────────────────────────────────────────
        clusters = _build_clusters(articles, max_posts, SOURCE_POOL_SIZE)
        print(
            f"\n[Step 3 / 3] Generating {len(clusters)} research post(s) "
            f"({SOURCE_POOL_SIZE} sources each)..."
        )

        generator = PostGenerator(self.brand_kit, self.posts_dir)
        generated = []

        for i, cluster in enumerate(clusters, 1):
            anchor = cluster[0]
            title_preview = anchor.title[:65] + ("…" if len(anchor.title) > 65 else "")
            print(f"\n  Post {i} — anchor: {title_preview}")
            print(
                f"  Sources: "
                + ", ".join(a.source_name for a in cluster[:4])
                + ("…" if len(cluster) > 4 else "")
            )
            result = generator.generate_post(cluster, trending)
            if result:
                generated.append(result)
                print(f"  ✓ Saved → {result['filename']} ({result['source_count']} sources cited)")
            else:
                print("  ✗ Generation failed — skipping.")

        self._display_posts(generated)

        # ── Step 4: Push to Notion (if configured) ──────────────────────────
        notion = NotionPublisher()
        if notion.is_configured():
            print("\n[Step 4 / 4] Publishing to Notion...")
            pushed = notion.publish_batch(generated)
            print(f"  ✓ {pushed}/{len(generated)} post(s) added to Notion.")
        else:
            print(
                "\nNotion not configured — set NOTION_API_KEY + NOTION_PAGE_ID in .env to enable."
            )

        return generated

    # ── Display helpers ────────────────────────────────────────────────────────

    def _display_articles(self, articles: list) -> None:
        _rule()
        print(f"  {'Score':>5}  {'Source':<22}  {'Companies':<22}  Title")
        _rule()
        for a in articles:
            companies = ", ".join(a.matched_companies[:2])[:22]
            title = a.title[:50] + ("…" if len(a.title) > 50 else "")
            print(f"  {a.relevance_score:>5}  {a.source_name[:22]:<22}  {companies:<22}  {title}")
        _rule()

    def _display_posts(self, generated: list) -> None:
        if not generated:
            print("\nNo posts were generated.")
            return
        print(f"\n✓ {len(generated)} research post(s) saved to /posts/\n")
        for post in generated:
            _rule("─", 60)
            print(f"File   : {post['filename']}")
            print(f"Sources: {post['source_count']} cited")
            if post.get("broken_urls"):
                print(f"⚠️  WARNING: {post['broken_urls']} broken link(s) — fix before publishing")
            print()
            # Print a trimmed preview
            preview = post["content"][:600]
            print(preview)
            if len(post["content"]) > 600:
                print("\n  [...truncated — open the file for the full post]")
        _rule("═")

    # ── Internal ───────────────────────────────────────────────────────────────

    def _load_yaml(self, filename: str) -> dict:
        path = self.config_dir / filename
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)


def _build_clusters(
    articles: list, max_posts: int, pool_size: int
) -> list:
    """
    Build article clusters for post generation.

    Each cluster anchors on a different article (giving each post a distinct focus)
    while drawing from the surrounding pool to guarantee SOURCE_POOL_SIZE sources.

    Example with 10 articles, max_posts=3, pool_size=6:
      Cluster 1: articles[0:6]  → anchor=articles[0]
      Cluster 2: articles[1:7]  → anchor=articles[1]
      Cluster 3: articles[2:8]  → anchor=articles[2]
    """
    clusters = []
    for i in range(min(max_posts, len(articles))):
        start = min(i, max(0, len(articles) - pool_size))
        cluster = articles[start : start + pool_size]
        if articles[i] in cluster and cluster[0] != articles[i]:
            cluster.remove(articles[i])
            cluster.insert(0, articles[i])
        clusters.append(cluster)
    return clusters
