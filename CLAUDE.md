# LinkedIn Post Generator

## What this project does

Fetches trending AI news, finds what's buzzing on the web, and writes research-backed LinkedIn draft posts — entirely through Claude agents. No Python or code steps.

## How to run the pipeline

When the user says anything like "run the pipeline", "generate posts", or "create LinkedIn posts", read `orchestrator.md` and follow it end-to-end.

Default run:
```
Run the LinkedIn Post Generator pipeline.
```

Custom runs:
```
Run the pipeline. Generate 3 posts. Use 5 articles per cluster.
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

## Project layout

```
orchestrator.md                        ← main pipeline definition (read this to run)
config/
  topics.yaml                          ← which companies and keywords to track
  brand_kit.yaml                       ← author voice, tone, post structure, hashtags
  sources.yaml                         ← RSS feeds and API sources to fetch from
.claude/agents/
  news-gatherer.md                     ← fetches RSS feeds, scores articles
  trending-tracker.md                  ← finds trending AI keyword phrases
  post-generator.md                    ← writes and saves LinkedIn draft posts
  notion-publisher.md                  ← publishes drafts to Notion (optional)
posts/                                 ← saved .md draft posts
.env.example                           ← copy to .env and fill in NOTION_PAGE_ID
```

## Configuration files the user can edit

| File | What to change |
|------|----------------|
| `config/topics.yaml` | Add/remove companies, keywords, freshness settings |
| `config/brand_kit.yaml` | Your name, tone of voice, writing rules, hashtags |
| `config/sources.yaml` | RSS feeds to monitor — add, remove, or disable |

## Important rules

- Never modify files in `.claude/agents/` unless the user explicitly asks to change pipeline logic
- Generated posts go to `posts/` — never delete them without asking
- Always read `orchestrator.md` before spawning subagents — it defines the full pipeline contract
- `config/brand_kit.yaml` → `author.name` and `author.title` are placeholder text — remind the user to fill these in on first run
