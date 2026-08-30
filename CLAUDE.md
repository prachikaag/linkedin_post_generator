# LinkedIn Post Generator — Claude Code Guide

## What this project does

This is a **multi-agent LinkedIn post generator** that:
1. Fetches fresh AI news from RSS feeds (news-gatherer agent)
2. Finds trending AI keyword phrases (trending-tracker agent)
3. Writes research-backed LinkedIn posts in the author's brand voice (post-generator agent)
4. Publishes drafts to Notion (notion-publisher agent, optional)

## How to run the pipeline

To generate new LinkedIn post drafts, say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code will read `orchestrator.md` and execute the full pipeline.

Custom options:
```
Run the LinkedIn Post Generator. Generate 3 posts.
Run the pipeline in dry-run mode — fetch news only.
```

## Editable configuration (edit these files to customise)

| File | What to edit |
|------|-------------|
| `config/brand_kit.yaml` | Your name, title, tone of voice, writing style, hashtags |
| `config/topics.yaml` | Companies and keywords to track, trending seed terms |
| `config/sources.yaml` | RSS feeds and news sources |

## Output

Generated posts are saved to `posts/` as `.md` files with YAML frontmatter.
Change `status: draft` to `status: published` once a post goes live.

## Agent files (edit to change agent behaviour)

- `.claude/agents/news-gatherer.md` — RSS fetching and scoring logic
- `.claude/agents/trending-tracker.md` — Trending keyword search logic
- `.claude/agents/post-generator.md` — Post writing rules and structure
- `.claude/agents/notion-publisher.md` — Notion publishing logic

## Environment variables

Copy `.env.example` to `.env` and fill in:
- `NOTION_PAGE_ID` — your Notion page ID (optional, enables Notion publishing)
- `NOTION_API_KEY` — your Notion integration token (optional)
- `NEWSAPI_KEY` — NewsAPI key for broader coverage (optional)
