# LinkedIn Post Generator

## What This Does
Fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts. Runs entirely through Claude agents and subagents — no traditional code.

## How to Run

Say this to Claude:

```
Run the LinkedIn Post Generator pipeline.
```

Or with options:
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
Run the LinkedIn Post Generator pipeline in dry-run mode.
```

The orchestrator is in `orchestrator.md`. Claude reads it and spawns four specialised subagents in sequence.

## Configuration — Edit These Files

| File | What it Controls |
|------|-----------------|
| `config/topics.yaml` | Companies, keywords, and freshness settings |
| `config/sources.yaml` | RSS feeds and news APIs to fetch from |
| `config/brand_kit.yaml` | Your name, title, focus areas, hashtags |
| `config/tone_of_voice.yaml` | Writing style, post structure, content angles, dos/don'ts |

## Generated Posts

Saved to `posts/` as markdown files with YAML frontmatter.

- `status: draft` — ready to review
- `status: published` — mark this after you publish to LinkedIn

## Pipeline Flow

```
orchestrator.md
├── news-gatherer      → reads RSS feeds, scores articles by relevance
├── trending-tracker   → searches web for trending AI phrases
├── post-generator     → writes post draft, saves to posts/
└── notion-publisher   → appends draft to Notion page (if NOTION_PAGE_ID is set)
```
