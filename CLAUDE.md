# LinkedIn Post Generator

## What This Is

A multi-agent pipeline that automatically:
1. Fetches fresh AI news from RSS feeds and scored against your topics
2. Finds trending AI keywords from the last 7 days via web search
3. Writes branded LinkedIn post drafts with cited sources
4. (Optional) Publishes drafts to a Notion page for review

## How to Run the Pipeline

To generate LinkedIn posts, say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code will read `orchestrator.md` and execute all four agents in sequence.

### Custom options:
- `Generate 3 posts` — controls how many posts to create (default: 2)
- `Use 8 articles per cluster` — controls how many articles to synthesise per post (default: 6)
- `Dry run — fetch and rank news only` — runs steps 1–2 only, no post generation

## Project Layout

```
config/
  topics.yaml       ← EDIT: companies, keywords, freshness rules
  brand_kit.yaml    ← EDIT: your name, tone, writing style, hashtags
  sources.yaml      ← EDIT: RSS feeds, YouTube channels, NewsAPI

.claude/agents/
  news-gatherer.md       ← fetches & scores RSS articles
  trending-tracker.md    ← finds trending AI keyword phrases
  post-generator.md      ← writes & saves LinkedIn draft posts
  notion-publisher.md    ← publishes drafts to Notion (optional)

orchestrator.md     ← master pipeline instructions (do not edit unless changing flow)
posts/              ← generated draft posts saved here as .md files
```

## Editing Your Config

All personalisation lives in `config/` — edit any file and re-run the pipeline.

| Task | File to edit |
|------|-------------|
| Add/remove companies or AI tools to track | `config/topics.yaml` — `companies_to_track` |
| Add/remove RSS feeds | `config/sources.yaml` — `rss_feeds` |
| Change your tone, writing style, or post length | `config/brand_kit.yaml` — `tone_of_voice` |
| Update your author name/title/tagline | `config/brand_kit.yaml` — `author` |
| Add/remove hashtags | `config/brand_kit.yaml` — `brand.hashtags` |
| Adjust how fresh articles must be | `config/topics.yaml` — `freshness` |

## Notion Setup (Optional)

If you want posts pushed to Notion automatically:

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New Integration
2. Copy the integration token → add to `.env` as `NOTION_API_KEY`
3. Open your LinkedIn drafts Notion page → `...` → Connections → connect your integration
4. Copy the 32-char page ID from the URL → add to `.env` as `NOTION_PAGE_ID`

Without these, posts are saved as local `.md` files in `posts/` only.

## Reviewing and Publishing Posts

Each generated post is saved as a markdown file in `posts/` with YAML frontmatter:

```yaml
---
title: "Post title"
date: "2024-01-15"
status: "draft"         ← change to "published" when you post it live
source_count: 6
matched_companies:
  - OpenAI
  - Anthropic
---
```

To track what you've published, change `status: draft` → `status: published` in the file.

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
NOTION_API_KEY=         # Internal integration token (optional)
NOTION_PAGE_ID=         # 32-char page ID from Notion URL (optional)
NEWSAPI_KEY=            # Free key from newsapi.org (optional, broader coverage)
```

`ANTHROPIC_API_KEY` is not needed when running inside Claude Code — it uses OAuth automatically.
