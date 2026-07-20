# LinkedIn Post Generator

An AI-native pipeline that turns your topic watchlist into research-backed LinkedIn draft posts — no code, no external APIs required beyond Claude Code.

## How to run

Say any of the following:

```
Run the LinkedIn Post Generator pipeline.
```

```
Run the pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't write posts.
```

Claude will read `orchestrator.md` and execute the full pipeline automatically.

---

## What happens each run

1. **News Gatherer** — fetches enabled RSS feeds in `config/sources.yaml`, scores articles against your topic keywords in `config/topics.yaml`, filters by freshness (default: last 48 hours), skips URLs already seen in `posts/memory.json`
2. **Trending Tracker** — searches the web for the most-discussed AI topics from the past 7 days
3. **Post Generator** — for each article cluster, writes a branded LinkedIn post following `config/brand_kit.yaml` exactly and saves it as a YAML-frontmatter markdown file in `posts/`
4. **Memory Update** — records processed URLs in `posts/memory.json` so the same articles are never re-used
5. **Notion Publisher** — if `NOTION_PAGE_ID` is set in `.env`, appends each draft as a collapsible toggle block to your Notion page

---

## Files to customise (priority order)

| File | What to edit |
|------|-------------|
| `config/brand_kit.yaml` | **Start here.** Fill in your name, title, tagline, location. Adjust tone traits and writing style to match your real voice. |
| `config/topics.yaml` | Add or remove companies, keywords, and topic categories. Tune freshness settings. |
| `config/sources.yaml` | Enable/disable RSS feeds. Add new sources. Set `enabled: false` to skip any feed. |
| `.env` | Set `NOTION_PAGE_ID` to push drafts to Notion automatically. |

---

## Output

Posts are saved to `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md   ← status: draft
  posts/memory.json                               ← seen article URLs (do not delete)
```

Each post has YAML frontmatter (sources, companies, categories, status) followed by the full post body. Change `status: draft` → `status: published` to track what's live.

---

## Configuration quick reference

**Tune `config/topics.yaml`**
- `freshness.max_article_age_hours` — how old articles can be (default 48)
- `freshness.min_relevance_score` — minimum keyword match score to include (default 2)
- `freshness.max_articles_per_run` — cap on articles fetched per run (default 25)

**Tune `config/brand_kit.yaml`**
- `brand.post_length` — `short` / `medium` / `long`
- `brand.max_hashtags` — total hashtags per post (default 5)
- `research_standards.min_sources` — minimum sources cited per post (default 4)

**Tune `orchestrator.md` parameters**
- `MAX_POSTS` — posts to generate per run (default 2)
- `SOURCE_POOL_SIZE` — articles per post cluster (default 6)

---

## Adding a new RSS source

Edit `config/sources.yaml` and add to the appropriate category:

```yaml
rss_feeds:
  ai_news:
    - name: "My Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

---

## Agents reference

All agents live in `.claude/agents/` and are self-contained — edit them independently:

| Agent | Role |
|-------|------|
| `news-gatherer.md` | Fetches + scores RSS articles, filters seen URLs |
| `trending-tracker.md` | Finds trending AI keyword phrases via web search |
| `post-generator.md` | Writes branded post, validates URLs, saves draft |
| `notion-publisher.md` | Publishes draft to Notion as a toggle block |
