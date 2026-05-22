# LinkedIn Post Generator

An AI pipeline that fetches trending AI news, spots what's buzzing, and writes
research-backed LinkedIn post drafts — in your voice, with cited sources.

---

## How to Run

Say any of these to start the pipeline:

```
Run the LinkedIn Post Generator pipeline.
```

```
Run the LinkedIn Post Generator. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't write posts.
```

The orchestrator (`orchestrator.md`) runs automatically and spawns four agents in sequence.

---

## What the Pipeline Does

1. **news-gatherer** — fetches all enabled RSS feeds from `config/sources.yaml`,
   scores articles by keyword relevance using `config/topics.yaml`, deduplicates,
   returns the top 25 articles as scored JSON

2. **trending-tracker** — searches the web for the hottest AI topics from the past
   7 days, returns 15–20 keyword phrases to weave into posts

3. **post-generator** — for each article cluster, reads your brand kit, tone of voice,
   and post angle templates, then writes a full LinkedIn draft saved to `posts/`

4. **notion-publisher** — if `NOTION_PAGE_ID` is set in `.env`, pushes each draft to
   your Notion page as a collapsible toggle block for review

---

## Config Files (edit these to customise everything)

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Which AI companies and keywords to track; freshness settings |
| `config/brand_kit.yaml` | Your name, title, brand focus, hashtags, post length, citation rules |
| `config/tone_of_voice.yaml` | Voice traits, writing style rules, post structure, dos and don'ts |
| `config/post_angles.yaml` | Post type templates: hooks, narrative frames, CTAs for each angle |
| `config/sources.yaml` | RSS feeds and API sources to fetch from; enable/disable per feed |

---

## Personalising Your Brand

Open `config/brand_kit.yaml` and set:
- `author.name` — your full name
- `author.title` — your professional title
- `author.tagline` — your one-line value proposition

Open `config/tone_of_voice.yaml` to adjust:
- `primary_traits` — how you want to come across
- `writing_style` — specific rules for every post
- `post_structure` — the section order and guidance

These files are read fresh on every pipeline run — no restart needed.

---

## Adding or Removing News Sources

Edit `config/sources.yaml`. To add a feed:

```yaml
rss_feeds:
  ai_news:
    - name: "My Source"
      url: "https://example.com/feed.xml"
      priority: high   # high | medium | low
      enabled: true
```

To pause a feed without deleting it, set `enabled: false`.

---

## Output

Generated drafts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-31-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, post angle, trending keywords, status
- **Post body**: the full LinkedIn draft — ready to review, edit, and publish

Change `status: draft` → `status: published` to track what's gone live.

---

## Notion Setup (optional)

1. Go to https://www.notion.so/my-integrations → New integration (Internal)
2. Copy the Integration Token → paste as `NOTION_API_KEY` in `.env`
3. Open your LinkedIn Post Ideas Notion page
4. "..." menu → Connections → connect your integration
5. Copy the 32-char page ID from the URL → paste as `NOTION_PAGE_ID` in `.env`

When set, every generated draft is pushed to Notion as a toggle block for easy review.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in what you need:

```bash
cp .env.example .env
```

| Variable | Required? | Purpose |
|----------|-----------|---------|
| `NOTION_PAGE_ID` | Optional | Pushes drafts to Notion |
| `NOTION_API_KEY` | Optional | Notion REST API fallback |
| `NEWSAPI_KEY` | Optional | Broader news coverage beyond RSS |
| `ANTHROPIC_API_KEY` | Not needed inside Claude Code | Auto-handled via OAuth |
