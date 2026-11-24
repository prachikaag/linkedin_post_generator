# LinkedIn Post Generator — Claude Instructions

## Quick Start

To run the full pipeline and generate LinkedIn post drafts:

```
Run the LinkedIn Post Generator pipeline.
```

Claude will read `orchestrator.md` and execute the full 4-step pipeline automatically.

## Custom Run Options

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

## What the pipeline does

1. **news-gatherer** — fetches RSS feeds from `config/sources.yaml`, scores articles by relevance against `config/topics.yaml`, returns top scored articles
2. **trending-tracker** — searches the web for the most-discussed AI topics this week
3. **post-generator** — synthesises each article cluster into a branded LinkedIn draft saved to `posts/`
4. **notion-publisher** — appends drafts to Notion (if `NOTION_PAGE_ID` is set in `.env`)

## Key config files to personalise

| File | What to change |
|------|---------------|
| `config/brand_kit.yaml` | **Your name, title, tone of voice, writing style** — update `author.name` and `author.title` |
| `config/topics.yaml` | Companies and keywords to track; freshness window; max articles per run |
| `config/sources.yaml` | RSS feeds to fetch; enable/disable individual sources |
| `.env` | `NOTION_PAGE_ID` for Notion publishing; `NEWSAPI_KEY` for broader coverage |

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter.
Change `status: draft` to `status: published` to track what has gone live.
