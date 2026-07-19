# LinkedIn Post Generator — Claude Code Guide

This project is a **multi-agent AI pipeline** that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn drafts — all through Claude agents.

## How to Run

Say any of these in Claude Code:

```
Run the LinkedIn Post Generator pipeline.
```
```
Run the LinkedIn pipeline. Generate 3 posts.
```
```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

Claude will read `orchestrator.md` and execute the full pipeline end-to-end.

## Architecture

```
orchestrator.md                                ← Start here (or .claude/agents/linkedin-pipeline.md)
├── .claude/agents/news-gatherer.md            ← Fetches + scores RSS articles via WebFetch
├── .claude/agents/trending-tracker.md         ← Searches trending AI topics via WebSearch
├── .claude/agents/post-generator.md           ← Writes and saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md         ← Publishes drafts to Notion (optional)
```

## Configuration — Edit These Files

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Companies to track, keywords, freshness settings |
| `config/brand_kit.yaml` | **Your name, tone of voice, writing style, hashtags** |
| `config/sources.yaml` | RSS feeds and API sources |

**Before your first run**, open `config/brand_kit.yaml` and fill in:
- `author.name` — your full name
- `author.title` — your professional title
- `author.location` — your city/country

## Notion Setup (Optional)

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Copy `.env.example` → `.env`
3. Set `NOTION_PAGE_ID` (already pre-filled in `.env.example` if you've done this before)
4. Set `NOTION_API_KEY` to your integration token

If `NOTION_PAGE_ID` is not set, posts are saved locally to `posts/` only.

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
```

Change `status: draft` → `status: published` to track what's gone live.
