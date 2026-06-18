# LinkedIn Post Generator

An agentic pipeline that watches AI news, tracks trending keywords, and writes research-backed LinkedIn drafts in your brand voice — all running through Claude Code subagents.

## Running the pipeline

Say to Claude:
> Run the LinkedIn Post Generator pipeline.

Or with options:
> Run the pipeline. Generate 3 posts. Dry-run mode only (fetch news, don't write posts).

## What the pipeline does

1. **news-gatherer** — Fetches RSS feeds from `config/sources.yaml`, scores articles against keywords in `config/topics.yaml`, skips articles already used in `posts/`
2. **trending-tracker** — Web-searches for the most-discussed AI topics across the past 7 days
3. **post-generator** — Writes a LinkedIn post per article cluster, following `config/brand_kit.yaml` exactly, saves to `posts/`
4. **notion-publisher** — Pushes each draft to Notion (only if `NOTION_PAGE_ID` is set in `.env`)

## Files to personalise first

| File | What to edit |
|------|-------------|
| `config/brand_kit.yaml` | Fill in `author.name`, `author.title`, `author.tagline`, `author.location` |
| `config/topics.yaml` | Add/remove companies and keywords you care about |
| `config/sources.yaml` | Add RSS feeds; set `enabled: false` to pause any source |
| `.env` | Copy `.env.example` → `.env`; add `NOTION_PAGE_ID` to enable Notion push |

## Output

Posts land in `posts/` as markdown files with YAML frontmatter.
Set `status: published` in the frontmatter once a post goes live — a future version will skip those.

## Pipeline parameters (say these to Claude)

- `MAX_POSTS` — number of posts to generate per run (default 2)
- `SOURCE_POOL_SIZE` — articles per post cluster (default 6)
- `DRY_RUN` — fetch and rank news only, skip post generation

## Agent files (edit to change pipeline behaviour)

- `orchestrator.md` — master pipeline; controls sequencing and parameters
- `.claude/agents/news-gatherer.md` — scoring logic, freshness window
- `.claude/agents/trending-tracker.md` — what trending sources to search
- `.claude/agents/post-generator.md` — post structure, length, tone rules
- `.claude/agents/notion-publisher.md` — Notion block layout
