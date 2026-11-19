# LinkedIn Post Generator — Claude Code Instructions

## How to Run the Pipeline

Say this in Claude Code:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude reads `orchestrator.md` and executes the full pipeline automatically.

### Optional parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## What the Pipeline Does

1. **News Gatherer** — fetches RSS feeds from `config/sources.yaml`, scores articles by keyword relevance from `config/topics.yaml`, returns top articles
2. **Trending Tracker** — searches the web for what's buzzing in AI this week
3. **Post Generator** — writes LinkedIn drafts using your brand voice from `config/brand_kit.yaml`, saves to `posts/`
4. **Notion Publisher** — pushes drafts to your Notion page (if `NOTION_PAGE_ID` is set in `.env`)

---

## First-Time Setup

### 1. Update your brand kit — the most important step

Open `config/brand_kit.yaml` and update the `author:` section:

```yaml
author:
  name: "Your Full Name"
  title: "Your LinkedIn Title"
  tagline: "One-line description of what you do"
  location: "City, Country"
```

The tone, style rules, and hashtags are already set to match the brief. Adjust anything you want to change.

### 2. Copy `.env.example` to `.env`

```bash
cp .env.example .env
```

Fill in `NOTION_PAGE_ID` if you want posts sent to Notion. Leave it blank to only save locally to `posts/`.

### 3. Run it

```
Run the LinkedIn Post Generator pipeline.
```

---

## Component Guide — What to Edit and Why

| File | What it controls | How often to edit |
|------|-----------------|-------------------|
| `config/brand_kit.yaml` | Your voice, tone, post structure, hashtags | Occasionally — when your brand evolves |
| `config/topics.yaml` | Companies to track, keyword scoring, freshness window | As new companies emerge |
| `config/sources.yaml` | RSS feeds and YouTube channels to pull from | When adding new sources |
| `orchestrator.md` | Pipeline flow, number of posts, clustering logic | Rarely |
| `.claude/agents/news-gatherer.md` | How articles are fetched and scored | Rarely |
| `.claude/agents/trending-tracker.md` | How trending keywords are found | Rarely |
| `.claude/agents/post-generator.md` | Post writing rules, structure, word limits | When refining post quality |
| `.claude/agents/notion-publisher.md` | Notion block format | Only if Notion layout changes |

---

## Customising Topics

Edit `config/topics.yaml` to track new companies:

```yaml
companies_to_track:
  ai_labs:
    - name: "New Company Name"
      keywords:
        - "New Company Name"
        - "Their product name"
        - "Their CEO's name"
```

Adjust the freshness window to fetch older or newer articles:

```yaml
freshness:
  max_article_age_hours: 72   # increase to 72 or 168 (7 days) for more articles
  min_relevance_score: 2      # lower to 1 to get more articles; raise to 4 for fewer but higher quality
```

---

## Adding YouTube Channels

Find a channel's ID: go to the channel on YouTube → View Page Source → search for `"channelId"`. Then add to `config/sources.yaml`:

```yaml
youtube_channels:
  - name: "Channel Name"
    url: "https://www.youtube.com/feeds/videos.xml?channel_id=YOUR_CHANNEL_ID_HERE"
    priority: medium
    enabled: true
```

---

## Output

Posts are saved to `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file has:
- YAML frontmatter with source metadata and status
- Full LinkedIn post body ready to copy-paste

Change `status: draft` → `status: published` to track what's gone live.

---

## Scheduled Runs

This pipeline can be scheduled to run automatically.
To set up a recurring run, say:

```
Schedule the LinkedIn Post Generator pipeline to run every weekday at 9am.
```
