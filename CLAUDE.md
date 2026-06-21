# LinkedIn Post Generator

## What this project does

A multi-agent Claude pipeline that:
1. Fetches AI news from 20+ RSS feeds (company blogs, TechCrunch, VentureBeat, YouTube channels)
2. Finds trending AI keyword phrases via web search
3. Clusters related articles and writes branded LinkedIn post drafts with cited sources
4. Optionally publishes drafts to Notion for review

## How to run

Say any of these inside Claude Code:

```
Run the LinkedIn Post Generator pipeline.
Run the pipeline. Generate 3 posts.
Run the pipeline in dry-run mode — fetch and rank news only.
```

Claude reads `orchestrator.md` and executes the full pipeline end-to-end.

## Files to edit (all config, no code)

| File | What to change |
|------|---------------|
| `config/topics.yaml` | Add/remove companies and keywords to track |
| `config/sources.yaml` | Add/remove RSS feeds and news sources |
| `config/brand_kit.yaml` | Your name, tone of voice, writing rules, hashtags |
| `prompts/post_angles.yaml` | Story angle templates and hook guidance |
| `prompts/scoring_weights.yaml` | Which news categories score higher |
| `prompts/writing_constraints.yaml` | Hard style rules (length, banned words, citations) |

## Agent files (advanced — edit if you want to change pipeline logic)

```
orchestrator.md                         ← master controller (reads, spawns agents, saves posts)
.claude/agents/news-gatherer.md         ← fetches RSS, scores by relevance
.claude/agents/trending-tracker.md      ← finds trending keywords via WebSearch
.claude/agents/post-generator.md        ← writes LinkedIn drafts
.claude/agents/notion-publisher.md      ← publishes to Notion
```

## Environment setup

Copy `.env.example` to `.env` and fill in:
- `NOTION_PAGE_ID` — your Notion page ID (for publishing drafts)
- `NOTION_API_KEY` — your Notion integration token (optional fallback)
- `NEWSAPI_KEY` — broader news coverage (optional, free at newsapi.org)

## Output

Posts are saved to `posts/` as markdown files:
```
posts/YYYY-MM-DD_HH-MM-SS_slug.md
```

Change `status: draft` to `status: published` to track what's gone live.

## Key design decisions

- **No Python code** — the entire pipeline runs as Claude agent instructions
- **URL safety** — the post-generator only uses URLs that appear verbatim in the fetched articles; it never constructs or guesses URLs
- **Brand fidelity** — every post is validated against the rules in `config/brand_kit.yaml` before saving
- **Modular** — every config file can be edited independently; changes take effect on the next run
