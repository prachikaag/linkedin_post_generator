from pathlib import Path

import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .news_gatherer import Article, NewsGatherer
from .notion_publisher import NotionPublisher
from .post_generator import PostGenerator
from .post_tracker import PostTracker
from .trending_tracker import TrendingTracker

console = Console()

# Each post is generated from this many articles (guarantees 4+ citable sources)
SOURCE_POOL_SIZE = 6


class Pipeline:
    """Orchestrates the full news → trends → post generation workflow."""

    def __init__(self, config_dir: Path, posts_dir: Path):
        self.config_dir = config_dir
        self.posts_dir  = posts_dir
        self.topics    = self._load_yaml("topics.yaml")
        self.brand_kit = self._load_yaml("brand_kit.yaml")
        self.sources   = self._load_yaml("sources.yaml")

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(
        self,
        max_posts: int = 3,
        dry_run: bool  = False,
        force: bool    = False,
    ) -> list[dict]:
        """
        Full pipeline:
          1. Fetch and score news articles from RSS feeds
          2. Filter out already-seen articles (unless --force)
          3. Fetch trending keywords
          4. Build article clusters (SOURCE_POOL_SIZE articles each)
          5. Generate one research-style post per cluster (min 4 sources)
          6. Mark source articles as seen so they won't re-trigger next run
          7. Save posts as markdown drafts for human review
          8. Optionally publish drafts to Notion
        """
        console.rule("[bold blue]LinkedIn Post Generator[/]")

        tracker = PostTracker(self.posts_dir)

        # ── Step 1: News ────────────────────────────────────────────────────
        console.print("\n[bold cyan]Step 1 / 3 — Fetching news[/]")
        gatherer = NewsGatherer(self.sources, self.topics)
        articles = gatherer.fetch_all()

        if not articles:
            console.print(
                "[yellow]No relevant articles found.\n"
                "Try increasing [bold]max_article_age_hours[/] in config/topics.yaml "
                "or lowering [bold]min_relevance_score[/].[/]"
            )
            return []

        console.print(f"[green]✓[/] {len(articles)} relevant articles fetched and scored.")

        # ── Step 1b: De-duplicate against seen cache ────────────────────────
        if force:
            console.print("[dim]--force: skipping seen-articles cache.[/]")
            fresh_articles = articles
        else:
            fresh_articles = tracker.filter_unseen(articles)
            skipped = len(articles) - len(fresh_articles)
            if skipped:
                console.print(
                    f"[dim]{skipped} article(s) already used in previous runs — skipped. "
                    "(Run with [bold]--force[/bold] to override.)[/]"
                )
            if not fresh_articles:
                console.print(
                    "[yellow]All fetched articles have already been used to generate posts.\n"
                    "Run [bold]python main.py run --force[/bold] to regenerate from existing news, "
                    "or wait for fresh articles to appear.[/]"
                )
                return []

        console.print(f"[green]✓[/] {len(fresh_articles)} new article(s) ready for post generation.")
        self._display_articles(fresh_articles[: SOURCE_POOL_SIZE * 2])

        if dry_run:
            console.print("\n[yellow]Dry-run mode — skipping post generation.[/]")
            return []

        # ── Step 2: Trending keywords ───────────────────────────────────────
        console.print("\n[bold cyan]Step 2 / 3 — Fetching trending keywords[/]")
        trend_tracker = TrendingTracker(self.topics)
        trending = trend_tracker.get_trending_keywords()
        console.print(
            f"[green]✓[/] Trending: {', '.join(trending[:8])}"
            if trending
            else "[yellow]No trending data — using seed terms.[/]"
        )

        # ── Step 3: Generate posts ──────────────────────────────────────────
        clusters = _build_clusters(fresh_articles, max_posts, SOURCE_POOL_SIZE)
        console.print(
            f"\n[bold cyan]Step 3 / 3 — Generating {len(clusters)} research post(s) "
            f"({SOURCE_POOL_SIZE} sources each)[/]"
        )

        generator  = PostGenerator(self.brand_kit, self.posts_dir)
        generated: list[dict] = []

        for i, cluster in enumerate(clusters, 1):
            anchor = cluster[0]
            label = anchor.title[:65] + ("…" if len(anchor.title) > 65 else "")
            console.print(f"\n  [bold]Post {i}[/] — anchor: {label}")
            console.print(
                f"  [dim]Drawing on {len(cluster)} sources: "
                + ", ".join(a.source_name for a in cluster[:4])
                + ("…" if len(cluster) > 4 else "")
                + "[/]"
            )

            result = generator.generate_post(cluster, trending)
            if result:
                generated.append(result)
                console.print(
                    f"  [green]✓[/] Saved → {result['filename']} "
                    f"[dim]({result['source_count']} sources cited)[/]"
                )
                # Mark all cluster URLs as seen so this news won't re-trigger
                tracker.mark_seen([a.url for a in cluster])
            else:
                console.print("  [red]✗[/] Generation failed — skipping.")

        self._display_posts(generated)

        # ── Step 4: Push to Notion (if configured) ──────────────────────────
        notion = NotionPublisher()
        if notion.is_configured():
            console.print("\n[bold cyan]Step 4 / 4 — Publishing to Notion[/]")
            pushed = notion.publish_batch(generated)
            console.print(
                f"[green]✓[/] {pushed}/{len(generated)} post(s) added to Notion."
            )
        else:
            console.print(
                "\n[dim]Notion not configured — "
                "set NOTION_API_KEY + NOTION_PAGE_ID in .env to enable.[/]"
            )

        if generated:
            console.print(
                "\n[bold]Next step:[/] Run [bold cyan]python main.py review[/bold] "
                "to step through the drafts and approve the ones you want to post.\n"
            )

        return generated

    # ── Display helpers ────────────────────────────────────────────────────────

    def _display_articles(self, articles: list[Article]) -> None:
        table = Table(
            title="Top Relevant Articles (source pool)",
            box=box.ROUNDED,
            show_lines=True,
        )
        table.add_column("Score",      style="cyan",    width=6,  justify="right")
        table.add_column("Title",      style="white",   max_width=52)
        table.add_column("Source",     style="yellow",  max_width=22)
        table.add_column("Companies",  style="green",   max_width=28)
        table.add_column("Categories", style="magenta", max_width=28)

        for article in articles:
            table.add_row(
                str(article.relevance_score),
                article.title[:52] + ("…" if len(article.title) > 52 else ""),
                article.source_name[:22],
                ", ".join(article.matched_companies[:3]),
                ", ".join(article.matched_categories[:2]),
            )

        console.print()
        console.print(table)

    def _display_posts(self, generated: list[dict]) -> None:
        if not generated:
            console.print("\n[red]No posts were generated.[/]")
            return

        console.print(
            f"\n[bold green]✓ {len(generated)} research post(s) saved to /posts/[/]\n"
        )
        for post in generated:
            sources_note = f"{post['source_count']} sources cited"
            broken_note  = (
                f" · [red]⚠ {post['broken_urls']} broken link(s)[/]"
                if post.get("broken_urls") else ""
            )
            console.print(
                Panel(
                    post["content"],
                    title=f"[bold]{post['article_title'][:55]}[/]",
                    subtitle=f"[dim]{post['filename']} · {sources_note}[/]{broken_note}",
                    border_style="green",
                    padding=(1, 2),
                )
            )
            console.print()

    # ── Internal ───────────────────────────────────────────────────────────────

    def _load_yaml(self, filename: str) -> dict:
        path = self.config_dir / filename
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)


def _build_clusters(
    articles: list[Article], max_posts: int, pool_size: int
) -> list[list[Article]]:
    """
    Build article clusters for post generation.

    Each cluster anchors on a different top article (distinct post focus)
    while drawing from nearby articles to guarantee pool_size sources.

      Cluster 1: articles[0:6]  → anchor = articles[0]
      Cluster 2: articles[1:7]  → anchor = articles[1]
      ...
    """
    clusters: list[list[Article]] = []
    for i in range(min(max_posts, len(articles))):
        start   = min(i, max(0, len(articles) - pool_size))
        cluster = articles[start : start + pool_size]
        anchor  = articles[i]
        if anchor in cluster and cluster[0] != anchor:
            cluster.remove(anchor)
            cluster.insert(0, anchor)
        clusters.append(cluster)
    return clusters
