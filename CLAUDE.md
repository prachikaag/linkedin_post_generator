# LinkedIn Post Generator — Claude Code Instructions

This project is a multi-agent pipeline that generates research-backed LinkedIn posts about AI news.
It runs entirely inside Claude Code — no Python or scripts required.

---

## How to Run the Pipeline

Tell Claude:

> "Run the LinkedIn Post Generator pipeline."

Claude reads `orchestrator.md` and executes the full pipeline in four steps:

1. **News Gatherer** — fetches AI news from RSS feeds, scores articles by keyword relevance
2. **Trending Tracker** — finds what's generating buzz in AI this week via web search
3. **Post Generator** — synthesises articles into a branded LinkedIn draft with cited sources
4. **Notion Publisher** — pushes drafts to Notion as toggle blocks (if configured)

### Custom Run Options

```
"Run the pipeline. Generate 3 posts."
"Run the pipeline. Use 8 articles per post."
"Run in dry-run mode — show top articles only, don't generate posts."
```

---

## Before Your First Run — Required Setup

Edit `config/brand_kit.yaml` and fill in your personal details:

```yaml
author:
  name: "Your Full Name"            # ← CHANGE THIS
  title: "Your Job Title"           # ← CHANGE THIS
  tagline: "Your LinkedIn tagline"  # ← CHANGE THIS
  location: "City, Country"         # ← CHANGE THIS
```

Everything else in `brand_kit.yaml` (tone, writing style, post structure, hashtags) is
already calibrated for an AI-curious brand and marketing voice — tweak as you go.

---

## Config Files — What Each One Controls

| File | What to Edit |
|------|-------------|
| `config/brand_kit.yaml` | Your voice, tone, writing rules, post structure, hashtag strategy |
| `config/topics.yaml` | AI companies to track, keywords per company, freshness window |
| `config/sources.yaml` | RSS feeds and API sources (add, disable, or reprioritise any feed) |

### Adding a new company to track

In `config/topics.yaml`, add a block under the relevant section:

```yaml
- name: "Company Name"
  keywords:
    - "Primary Keyword"
    - "Secondary Keyword"
```

### Adding a new RSS feed

In `config/sources.yaml`, add a block under the relevant category:

```yaml
- name: "Publication Name"
  url: "https://example.com/feed.xml"
  priority: high   # high | medium | low
  enabled: true
```

---

## Notion Integration (Optional)

To publish post drafts directly to a Notion page:

1. Create a Notion internal integration at https://www.notion.so/my-integrations
2. Connect the integration to your target Notion page
3. Copy `.env.example` → `.env` in this directory
4. Fill in `NOTION_PAGE_ID` (32-char page ID from the Notion URL) and `NOTION_API_KEY`
5. Connect the Notion MCP connector in your Claude Code settings

---

## Output

Generated posts are saved to `posts/` as `.md` files with YAML frontmatter:

```
posts/
  2026-07-17_10-30-00_openai-launches-new-feature.md
  2026-07-17_10-30-00_anthropic-funding-round.md
```

**Workflow:**
- Open the file, review, and edit the draft
- Change `status: draft` → `status: published` after you post on LinkedIn
- This status is how the pipeline tracks what's already live — so it won't re-cover it

---

## Agents Reference

| Agent | File | Role |
|-------|------|------|
| Orchestrator | `orchestrator.md` | Runs the full pipeline, coordinates all subagents |
| News Gatherer | `.claude/agents/news-gatherer.md` | Fetches RSS feeds, scores articles, skips already-covered stories |
| Trending Tracker | `.claude/agents/trending-tracker.md` | Web-searches for trending AI topics and keywords |
| Post Generator | `.claude/agents/post-generator.md` | Writes the branded LinkedIn draft, saves to `posts/` |
| Notion Publisher | `.claude/agents/notion-publisher.md` | Appends the draft to a Notion page as a toggle block |

---

## Scheduled Runs

This pipeline can be set on a recurring schedule via Claude Code scheduled tasks.
The `.claude/scheduled_tasks.lock` file is managed automatically — do not edit it manually.

To set up a daily run, tell Claude:
> "Schedule the LinkedIn Post Generator to run every weekday morning."
