# LinkedIn Post Generator

A multi-agent pipeline that fetches AI news, tracks trends, and writes research-backed LinkedIn draft posts — entirely through Claude agents.

## How to run the pipeline

```
Run the LinkedIn Post Generator pipeline.
```

Claude reads `orchestrator.md` and spawns four subagents in sequence.

Custom runs:
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

## Pipeline overview

```
news-gatherer  →  RSS feeds + topics.yaml  →  scored articles JSON
trending-tracker  →  web search  →  keyword phrases JSON
post-generator  →  brand_kit.yaml + articles  →  posts/*.md draft
notion-publisher  →  Notion page (if NOTION_PAGE_ID is set in .env)
```

## Files to edit

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Companies, keywords, and topic categories to track; freshness settings |
| `config/brand_kit.yaml` | Author name, tone, writing style, hashtags, post length |
| `config/sources.yaml` | RSS feeds and optional NewsAPI queries |
| `.env` | NOTION_PAGE_ID, NEWSAPI_KEY (copy from .env.example) |

## Output

Posts are saved to `posts/` as `.md` files with YAML frontmatter.  
Change `status: draft` → `status: published` to mark what has gone live.

## Agents

- `.claude/agents/news-gatherer.md` — fetches and scores RSS articles
- `.claude/agents/trending-tracker.md` — finds trending AI keyword phrases
- `.claude/agents/post-generator.md` — writes and saves LinkedIn post drafts
- `.claude/agents/notion-publisher.md` — publishes drafts to Notion
