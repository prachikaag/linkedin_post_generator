# LinkedIn Post Generator — Claude Code Project

## What this project does

An AI pipeline that:
1. Fetches fresh AI news from RSS feeds (`config/sources.yaml`)
2. Scores articles against tracked companies and topics (`config/topics.yaml`)
3. Finds trending keyword phrases from the past 7 days
4. Writes branded LinkedIn post drafts (`config/brand_kit.yaml`)
5. Saves drafts to `posts/` and optionally publishes to Notion

## How to run the pipeline

Say any of the following:

```
Run the LinkedIn Post Generator pipeline.
Run the pipeline. Generate 3 posts.
Run the pipeline in dry-run mode.
```

Claude Code will read `orchestrator.md` and execute the full multi-agent pipeline.

## Configuration files (edit these freely)

| File | What to change |
|------|---------------|
| `config/topics.yaml` | Companies to track, keywords, freshness settings |
| `config/brand_kit.yaml` | Author name, tone of voice, writing rules, hashtags |
| `config/sources.yaml` | RSS feeds — add/remove/disable sources |

## Memory & deduplication

`memory/seen_urls.txt` — article URLs already covered in previous runs.
The news-gatherer skips these so each run surfaces genuinely new stories.

`memory/run_log.jsonl` — one record per pipeline run (posts generated, companies covered).

## Output

Posts are saved to `posts/` as `.md` files with YAML frontmatter.
Change `status: draft` → `status: published` to mark a post as live.

## Notion integration

Set `NOTION_PAGE_ID` in `.env` to push drafts directly to your Notion review page.
The Notion MCP connector must be authorised in Claude Code settings.

## Agent architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      # WebFetch → scored article JSON
├── .claude/agents/trending-tracker.md   # WebSearch → trending keyword phrases
├── .claude/agents/post-generator.md     # Writes + saves the LinkedIn draft
└── .claude/agents/notion-publisher.md   # Pushes draft to Notion (optional)
```
