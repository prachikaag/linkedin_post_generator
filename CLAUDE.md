# LinkedIn Post Generator — Claude Code Guide

## What this project does

An automated LinkedIn post pipeline that runs entirely inside Claude Code. It:
1. Fetches fresh AI news from RSS feeds and web search
2. Finds trending AI keyword phrases from the past 7 days
3. Writes research-backed LinkedIn draft posts in the author's exact voice
4. Saves drafts to `posts/` as markdown files
5. Optionally publishes drafts to a Notion page

## How to run the pipeline

Say this in Claude Code:

```
Run the LinkedIn Post Generator pipeline.
```

Or with custom parameters:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

The orchestrator is in `orchestrator.md`. It spawns four subagents in sequence.

## File structure

```
orchestrator.md                   ← Main pipeline runner (edit to change flow)
config/
  topics.yaml                     ← What companies and topics to track (edit freely)
  brand_kit.yaml                  ← Your voice, tone, post structure, hashtags (edit freely)
  sources.yaml                    ← RSS feeds and news APIs (add/remove feeds here)
.claude/agents/
  news-gatherer.md                ← Fetches + scores RSS articles
  trending-tracker.md             ← Finds trending AI phrases via web search
  post-generator.md               ← Writes + saves LinkedIn drafts
  notion-publisher.md             ← Publishes drafts to Notion
posts/                            ← Generated draft posts (markdown with YAML frontmatter)
  .gitkeep
  *.md                            ← Draft posts — edit status: "published" when live
```

## What to edit and when

| Want to... | Edit this file |
|---|---|
| Track a new AI company or keyword | `config/topics.yaml` → `companies_to_track` |
| Add a new content category (e.g. "AI in Healthcare") | `config/topics.yaml` → `topic_categories` |
| Add or remove an RSS feed | `config/sources.yaml` → `rss_feeds` |
| Change your writing style or tone | `config/brand_kit.yaml` → `tone_of_voice` |
| Update your hashtag strategy | `config/brand_kit.yaml` → `brand.hashtags` |
| Change post length (short/medium/long) | `config/brand_kit.yaml` → `brand.post_length` |
| Enable Notion publishing | `.env` → set `NOTION_PAGE_ID` |
| Change how many posts are generated per run | `orchestrator.md` → `MAX_POSTS` default |

## Environment variables

Copy `.env.example` to `.env` and fill in `NOTION_PAGE_ID` to enable Notion publishing.
The pipeline works without Notion — posts are always saved to `posts/` regardless.

## Post status tracking

Each post in `posts/` has a `status` field in its YAML frontmatter:
- `status: draft` — generated, not yet reviewed
- `status: reviewed` — reviewed, ready to schedule
- `status: published` — published on LinkedIn (update manually)

## Scheduling

To run this automatically every weekday:
- Use Claude Code's `/loop` command or set up a cron-style schedule
- The pipeline is stateless — safe to run multiple times
- Duplicate articles are avoided by the 48-hour freshness window in `topics.yaml`

## Key design decisions

- **No Python code** — the pipeline runs entirely through Claude agents reading markdown instructions
- **No API keys required** — uses Claude's built-in WebFetch and WebSearch tools
- **Editable config** — all behaviour lives in YAML files, not agent code
- **URLs never guessed** — the post-generator only uses URLs from actual fetched articles
