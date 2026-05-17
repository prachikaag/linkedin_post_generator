# LinkedIn Post Generator

This project is a multi-agent LinkedIn post pipeline. When the user asks to run
the pipeline, generate posts, or fetch news — execute the full orchestrator
instructions below.

---

## How to trigger

Any of these prompts should start the pipeline:
- "Run the LinkedIn Post Generator"
- "Generate posts"
- "Fetch news and write posts"
- "Run the pipeline"

Default run: **2 posts**, **6 articles per cluster**, Notion publishing enabled if `NOTION_PAGE_ID` is set in `.env`.

The user can also say:
- "Generate 3 posts" → set MAX_POSTS=3
- "Dry run" → fetch and rank news only, no post generation
- "5 articles per cluster" → set SOURCE_POOL_SIZE=5

---

## Pipeline — run these steps in order

### Step 1 — Gather News

Spawn the **news-gatherer** subagent (`use_subagent: .claude/agents/news-gatherer.md`).

Task:
> "Fetch AI news articles from the RSS feeds and topics config and return a scored JSON array."

On empty result → print: `No relevant articles found. Try increasing max_article_age_hours or lowering min_relevance_score in config/topics.yaml.` and stop.

Print: `✓ {N} relevant articles fetched and scored.`

If dry-run → print top 12 articles (title, score, source) and stop.

---

### Step 2 — Get Trending Keywords

Spawn the **trending-tracker** subagent (`use_subagent: .claude/agents/trending-tracker.md`).

Task:
> "Search the web for trending AI keyword phrases from the past 7 days."

Print: `✓ Trending keywords: {first 8 keywords}`

---

### Step 3 — Build Article Clusters

- `n_posts = min(MAX_POSTS, len(articles))`
- For post `i`: `cluster = articles[i : i + SOURCE_POOL_SIZE]`, move `articles[i]` to position 0

---

### Step 4 — Generate Posts

For each cluster, spawn the **post-generator** subagent (`use_subagent: .claude/agents/post-generator.md`).

Pass inline JSON:
```
Generate a LinkedIn post draft from the following data and save it to posts/.

Input:
{
  "articles": [<cluster articles>],
  "trending_keywords": [<trending keywords>],
  "posts_dir": "posts/"
}
```

Print per post:
```
Post {i+1} — anchor: {cluster[0].title[:65]}
  Sources: {first 4 source names}
  ✓ Saved → {filename} ({source_count} sources cited)
```

---

### Step 5 — Publish to Notion (optional)

Check `.env` for `NOTION_PAGE_ID`. If set and non-empty, for each post spawn
the **notion-publisher** subagent (`use_subagent: .claude/agents/notion-publisher.md`).

Pass inline JSON:
```json
{
  "article_title": "<result.article_title>",
  "content": "<result.content>",
  "source_count": <result.source_count>,
  "page_id": "<NOTION_PAGE_ID>"
}
```

Print: `✓ {N}/{total} post(s) added to Notion.`
If not configured: `Notion not configured — set NOTION_PAGE_ID in .env to enable.`

---

### Step 6 — Final Summary

```
╔══════════════════════════════════════════════════════╗
║  LinkedIn Post Generator — Run Complete              ║
╠══════════════════════════════════════════════════════╣
║  Posts generated : {N}                               ║
║  Saved to        : posts/                            ║
╠══════════════════════════════════════════════════════╣
║  {filename}  ·  {source_count} sources               ║
╚══════════════════════════════════════════════════════╝
```

Print each post's full content so the author can review immediately.

---

## Project structure

| Path | What to edit |
|------|-------------|
| `config/topics.yaml` | Companies and keywords to track; freshness settings |
| `config/brand_kit.yaml` | Your name, title, tone of voice, writing rules, hashtags |
| `config/sources.yaml` | RSS feeds and optional NewsAPI config |
| `.env` | `NOTION_PAGE_ID`, `NOTION_API_KEY`, `NEWSAPI_KEY` |
| `posts/` | Generated draft posts (Markdown with YAML frontmatter) |
| `data/seen_articles.json` | URLs already used — prevents duplicate posts across runs |

---

## First-time setup checklist

1. Edit `config/brand_kit.yaml` → fill in `author.name`, `author.title`, `author.location`
2. Copy `.env.example` → `.env` and set `NOTION_PAGE_ID` if you want Notion sync
3. Say: **"Run the LinkedIn Post Generator"**

---

## Error handling

- If any subagent fails, log a warning and continue
- If one post cluster fails, skip and continue to the next
- Never halt the entire pipeline for a single failure
