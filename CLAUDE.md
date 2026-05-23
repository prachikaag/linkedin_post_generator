# LinkedIn Post Generator — Claude Code Guide

This project generates research-backed LinkedIn post drafts by fetching AI news, tracking trending keywords, and writing in a personalised brand voice. Everything runs as Claude subagents — no Python, no servers.

---

## How to Run the Pipeline

Tell Claude:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude reads `orchestrator.md` and executes the full pipeline automatically.

### Custom options

```
Run the LinkedIn Post Generator. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and score news only, don't write posts.
```

```
Run the pipeline and use 8 articles per post cluster.
```

---

## Pipeline Steps

When you say "run the pipeline", Claude executes these steps in order:

1. **News Gatherer** — fetches all enabled RSS feeds from `config/sources.yaml`, scores each article against the companies and keywords in `config/topics.yaml`, deduplicates, and returns the top articles ranked by relevance.

2. **Trending Tracker** — searches the web for the most-discussed AI topics from the past 7 days and returns 15–20 trending keyword phrases.

3. **Article Clustering** — groups the top articles into clusters (one cluster per post). Each cluster has a distinct anchor article.

4. **Post Generator** — for each cluster, writes a branded LinkedIn post following `config/tone_of_voice.yaml` and `config/brand_kit.yaml`, cites sources per `config/research_standards.yaml`, and saves a `.md` draft to `posts/`.

5. **Notion Publisher** *(optional)* — if `NOTION_PAGE_ID` is set in `.env`, appends each draft to your Notion page as a collapsible toggle block.

---

## Configuration Files

All settings live in `config/`. Edit any file — changes take effect on the next run.

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | AI companies, products, and keyword categories to track; freshness and scoring settings |
| `config/sources.yaml` | RSS feeds and optional APIs to fetch news from; enable/disable individual feeds |
| `config/brand_kit.yaml` | Your name, title, brand focus areas, content angles, hashtag strategy, post length |
| `config/tone_of_voice.yaml` | Writing style, post structure blueprint, dos and don'ts, banned words |
| `config/research_standards.yaml` | Citation rules, URL integrity, quote verification, time-reference rules |

### Most-edited settings

**To add a new AI company to track** → `config/topics.yaml` → `companies_to_track`

**To add a news source** → `config/sources.yaml` → `rss_feeds`

**To change how you sound** → `config/tone_of_voice.yaml` → `writing_style` or `post_structure`

**To update your name/title** → `config/brand_kit.yaml` → `author`

**To change hashtags** → `config/brand_kit.yaml` → `hashtags`

**To require more sources per post** → `config/research_standards.yaml` → `min_sources`

---

## Agent Files

The agents live in `.claude/agents/`. Each is a self-contained markdown file with its own role, tools, and input/output contract.

| Agent | Role |
|-------|------|
| `.claude/agents/news-gatherer.md` | Fetches + scores RSS articles |
| `.claude/agents/trending-tracker.md` | Finds trending keyword phrases via web search |
| `.claude/agents/post-generator.md` | Writes and saves LinkedIn post drafts |
| `.claude/agents/notion-publisher.md` | Publishes drafts to Notion |

The orchestrator is `orchestrator.md` in the project root.

---

## Output

Posts are saved to `posts/` as markdown files:

```
posts/
  2026-05-14_22-55-00_enterprise-ai-market-shift.md
  2026-05-14_23-10-00_vertical-ai-depth-over-horizontal.md
```

Each file has:
- **YAML frontmatter**: source metadata, matched companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and copy-paste

Change `status: draft` to `status: published` to track what's gone live.

---

## Notion Setup (Optional)

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New integration (Internal)
2. Copy the "Internal Integration Token"
3. Open your LinkedIn Post Ideas Notion page → "..." menu → Connections → connect your integration
4. Copy the 32-character page ID from the URL
5. Add both to `.env`:
   ```
   NOTION_API_KEY=secret_xxx
   NOTION_PAGE_ID=your32charpageid
   ```

---

## Troubleshooting

**"No relevant articles found"** → Increase `max_article_age_hours` or lower `min_relevance_score` in `config/topics.yaml`

**Post is too long** → Lower `max_words` or `max_characters` in `config/brand_kit.yaml`

**Wrong tone** → Edit `config/tone_of_voice.yaml` → `writing_style` and re-run

**Missing a company** → Add it to `config/topics.yaml` → `companies_to_track` with its keyword list

**RSS feed failing** → Set `enabled: false` for that feed in `config/sources.yaml` to skip it
