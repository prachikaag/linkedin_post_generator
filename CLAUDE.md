# LinkedIn Post Generator

A multi-agent pipeline that fetches fresh AI news, tracks trending keywords, and writes research-backed LinkedIn post drafts — entirely through Claude subagents. No code to run.

## How to Run

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code reads `orchestrator.md` and executes the full pipeline automatically.

### Options

```
Run the LinkedIn Post Generator. Generate 3 posts.
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
Run the LinkedIn Post Generator. Use 8 articles per cluster.
```

## Entry Point

`orchestrator.md` — the master pipeline. It spawns four subagents in sequence:

| Step | Agent | What it does |
|------|-------|-------------|
| 1 | `news-gatherer` | Fetches RSS feeds, scores articles by keyword relevance |
| 2 | `trending-tracker` | Searches web for trending AI phrases from the last 7 days |
| 3 | `post-generator` | Writes a branded LinkedIn draft, saves to `posts/` |
| 4 | `notion-publisher` | Appends drafts to a Notion page (optional, requires `.env`) |

Subagent definitions live in `.claude/agents/`.

## Customise

| File | What to edit |
|------|-------------|
| `config/topics.yaml` | Companies, keywords, and freshness settings — controls what news gets tracked |
| `config/brand_kit.yaml` | Author name/title, tone of voice, writing style rules, hashtag strategy |
| `config/sources.yaml` | RSS feeds, YouTube channels, optional NewsAPI |
| `.env` | `NOTION_PAGE_ID`, `NOTION_API_KEY`, `NEWSAPI_KEY` |

## Output

Generated posts save to `posts/` as markdown files with YAML frontmatter.
Set `status: published` in a post's frontmatter to track what's gone live.

## First-time Setup

1. Copy the environment file: `cp .env.example .env`
2. Fill in your Notion page ID in `.env` (see `.env.example` for instructions)
3. Edit `config/brand_kit.yaml` — update `author.name`, `author.title`, and `author.tagline`
4. Optionally add a NewsAPI key for broader coverage (`https://newsapi.org/`)
5. Say: `Run the LinkedIn Post Generator pipeline.`
