from pathlib import Path

import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .news_gatherer import Article, NewsGatherer
from .post_generator import PostGenerator
from .trending_tracker import TrendingTracker

console = Console()


class Pipeline:
    """Orchestrates the full news → trends → post generation workflow."""

    def __init__(self, config_dir: Path, posts_dir: Path):
        self.config_dir = config_dir
        self.posts_dir = posts_dir
        self.topics = self._load_yaml("topics.yaml")
        self.brand_kit = self._load_yaml("brand_kit.yaml")
        self.sources = self._load_yaml("sources.yaml")

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self, max_posts: int = 3, dry_run: bool = False) -> list[dict]:
        """
        Full pipeline run:
          1. Fetch and score news articles
          2. Get trending keywords from Google Trends
          3. Generate LinkedIn posts (unless dry_run)
          4. Save posts as markdown drafts for human review
        """
        console.rule("[bold blue]LinkedIn Post Generator[/]")

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

        console.print(f"[green]✓[/] {len(articles)} relevant articles found.")
        self._display_articles(articles[:max_posts * 2])

        if dry_run:
            console.print("\n[yellow]Dry-run mode — skipping post generation.[/]")
            return []

        # ── Step 2: Trending keywords ───────────────────────────────────────
        console.print("\n[bold cyan]Step 2 / 3 — Fetching trending keywords[/]")
        tracker = TrendingTracker(self.topics)
        trending = tracker.get_trending_keywords()
        if trending:
            console.print(f"[green]✓[/] Trending: {', '.join(trending[:8])}")
        else:
            console.print("[yellow]No trending data — using seed terms.[/]")

        # ── Step 3: Generate posts ──────────────────────────────────────────
        console.print(f"\n[bold cyan]Step 3 / 3 — Generating {min(max_posts, len(articles))} post(s)[/]")
        generator = PostGenerator(self.brand_kit, self.posts_dir)
        generated: list[dict] = []

        for article in articles[:max_posts]:
            console.print(f"  Drafting: {article.title[:70]}...")
            result = generator.generate_post(article, trending)
            if result:
                generated.append(result)
                console.print(f"  [green]✓[/] Saved → {result['filename']}")
            else:
                console.print("  [red]✗[/] Generation failed — skipping.")

        self._display_posts(generated)
        return generated

    # ── Display helpers ────────────────────────────────────────────────────────

    def _display_articles(self, articles: list[Article]) -> None:
        table = Table(title="Top Relevant Articles", box=box.ROUNDED, show_lines=True)
        table.add_column("Score", style="cyan", width=6, justify="right")
        table.add_column("Title", style="white", max_width=55)
        table.add_column("Source", style="yellow", max_width=22)
        table.add_column("Companies", style="green", max_width=28)
        table.add_column("Categories", style="magenta", max_width=30)

        for article in articles:
            table.add_row(
                str(article.relevance_score),
                article.title[:55] + ("…" if len(article.title) > 55 else ""),
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

        console.print(f"\n[bold green]✓ {len(generated)} post(s) generated and saved to /posts[/]\n")
        for post in generated:
            console.print(
                Panel(
                    post["content"],
                    title=f"[bold]{post['article_title'][:55]}[/]",
                    subtitle=f"[dim]{post['filename']}[/]",
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
