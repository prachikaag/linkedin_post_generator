# LinkedIn Post Generator

## How to run

Say: **"Run the LinkedIn Post Generator pipeline."**

Claude Code reads `orchestrator.md` and executes the full pipeline end-to-end.

### Variant run commands

```
Run the LinkedIn Post Generator pipeline.
Run the pipeline and generate 3 posts.
Run the pipeline in dry-run mode — show me the news without writing posts.
Run the pipeline. Skip Notion publishing.
```

---

## Pipeline stages (in order)

| Stage | Agent | What it does |
|-------|-------|--------------|
| 1 | `news-gatherer` | Fetches RSS feeds from `config/sources.yaml`, scores articles against `config/topics.yaml`, returns ranked articles |
| 2 | `trending-tracker` | Searches the web for trending AI topics, returns 15–20 keyword phrases |
| 3 | `post-deduplicator` | Scans `posts/` for already-covered stories, filters them so every run is fresh |
| 4 | `post-generator` | Writes a branded LinkedIn draft using voice from `config/brand_kit.yaml` and angles from `config/content_pillars.yaml` |
| 5 | `notion-publisher` | Pushes drafts to Notion (only if `NOTION_PAGE_ID` is set in `.env`) |

---

## Files you edit to customise the pipeline

| File | Controls |
|------|---------|
| `config/topics.yaml` | Companies and keywords to track — add new AI tools here |
| `config/sources.yaml` | RSS feeds — add any publication or YouTube channel |
| `config/brand_kit.yaml` | Your name, voice, tone, post structure, hashtags |
| `config/content_pillars.yaml` | Your content strategy: angles, themes, human-in-loop prompts |
| `.env` | API keys and Notion page ID |

---

## Output

Posts are saved to `posts/` as `.md` files with YAML frontmatter.

```
posts/
  2024-09-14_09-00-00_chatgpt-launches-new-voice-mode.md
  2024-09-14_09-00-00_anthropic-funding-round-series-d.md
```

Each file has:
- **YAML frontmatter** — source URLs, companies, categories, status
- **Post body** — the full LinkedIn draft, ready to copy-paste and publish

Change `status: draft` → `status: published` to track what's gone live.

---

## Setup checklist

- [ ] Fill in your name, title, and tagline in `config/brand_kit.yaml` (search for `YOUR_`)
- [ ] Copy `.env.example` to `.env` — set `NOTION_PAGE_ID` if you want Notion publishing
- [ ] Review `config/topics.yaml` — add or remove companies and keywords
- [ ] Review `config/content_pillars.yaml` — customise your content angles

---

## Adding a new AI tool to track

In `config/topics.yaml` under `companies_to_track.ai_labs`:

```yaml
- name: "New Tool Name"
  keywords:
    - "New Tool Name"
    - "specific product name"
    - "related keyword"
```

## Adding a new news source

In `config/sources.yaml` under the appropriate category:

```yaml
- name: "Source Display Name"
  url: "https://example.com/feed.rss"
  priority: high   # high / medium / low
  enabled: true
```
