# LinkedIn Post Generator — Claude Code Project

## What This Does

Automated LinkedIn post drafting pipeline. When run, it:
1. Fetches fresh AI news from 20+ RSS feeds
2. Finds what's trending in AI right now (web search)
3. Writes 2 fully-researched LinkedIn post drafts in your brand voice
4. Optionally saves them to Notion for review

All generated posts go to `posts/` as `.md` files with YAML frontmatter.

---

## How to Run

To run the full pipeline, the user just needs to say:
```
Run the LinkedIn Post Generator pipeline.
```

When they say this, read `orchestrator.md` and follow it exactly. Do not summarise or skip steps — it is the executable spec for the pipeline.

**Shortcut variants the user may say:**
- "Run the post generator" → full pipeline, default parameters
- "Generate LinkedIn posts" → full pipeline
- "Run in dry-run mode" → fetch + rank news only, skip post generation
- "Generate [N] posts" → set MAX_POSTS = N

The pipeline reads all config from `config/` — no code to run.

---

## Project Layout

```
orchestrator.md              ← MAIN PIPELINE — read this to run
.claude/agents/
  news-gatherer.md           ← fetches & scores RSS articles
  trending-tracker.md        ← finds trending AI keywords (web search)
  post-generator.md          ← writes the LinkedIn post draft
  notion-publisher.md        ← pushes draft to Notion (optional)
config/
  topics.yaml                ← AI companies & keywords to track ← EDIT THIS
  brand_kit.yaml             ← your voice, tone, post structure  ← EDIT THIS
  sources.yaml               ← RSS feeds to fetch from           ← EDIT THIS
posts/                       ← generated drafts land here
.env                         ← NOTION_PAGE_ID, NEWSAPI_KEY (optional)
```

---

## First-Time Setup

### 1. Fill in your brand identity

Open `config/brand_kit.yaml` and replace the placeholder fields:

```yaml
author:
  name: "Your Name"        ← replace with your real name
  title: "Your Title"      ← replace with your LinkedIn headline
  tagline: "..."           ← replace with your tagline
  location: "City, Country"
```

Everything else in `brand_kit.yaml` (tone traits, writing style, hashtags) is ready to use out of the box. Tweak to taste.

### 2. (Optional) Connect Notion

1. Go to https://www.notion.so/my-integrations → create an Internal integration
2. Copy your Notion page ID from the page URL (32-char hex)
3. Add to `.env`:
   ```
   NOTION_PAGE_ID=your_32char_page_id
   NOTION_API_KEY=secret_xxx
   ```
4. Connect the integration to your Notion page ("..." → Connections)

If `.env` has no `NOTION_PAGE_ID`, the pipeline skips Notion and saves locally only.

---

## Customising the Pipeline

| File | What to edit |
|------|-------------|
| `config/topics.yaml` | Add companies, products, or keywords to watch |
| `config/brand_kit.yaml` | Change your name, tone, hashtags, post length |
| `config/sources.yaml` | Add or disable RSS feeds |
| `orchestrator.md` | Change MAX_POSTS, SOURCE_POOL_SIZE defaults |

Each file is self-documenting with comments. Changes take effect on the next run — no restarts needed.

---

## Output Format

Each post is saved as:
```
posts/YYYY-MM-DD_HH-MM-SS_article-slug.md
```

The file starts with YAML frontmatter (title, sources, companies, status) followed by the full post body. Change `status: draft` to `status: published` to track what has gone live.

---

## Pipeline Agents

| Agent | Role | Tools |
|-------|------|-------|
| `news-gatherer` | Fetches RSS, scores articles by keyword | Read, WebFetch |
| `trending-tracker` | Finds trending AI topics via web search | Read, WebSearch |
| `post-generator` | Writes & saves the LinkedIn draft | Read, Write |
| `notion-publisher` | Appends draft to Notion page | Read, Notion MCP |
