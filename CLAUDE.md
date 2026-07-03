# LinkedIn Post Generator

A multi-agent pipeline that watches AI news, tracks what's trending, and writes branded LinkedIn drafts ready to review and publish.

---

## How to Run

To generate LinkedIn posts, say:

```
Run the LinkedIn Post Generator pipeline.
```

To control how many posts are generated:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

To preview news without generating posts:

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

The orchestrator is defined in `orchestrator.md`.

---

## Component Map — Edit Any of These

| File | What it controls | When to edit |
|------|-----------------|--------------|
| `config/topics.yaml` | Which companies, products, and keyword categories to track | Add a new AI company, change freshness window, adjust scoring |
| `config/brand_kit.yaml` | Your name, voice, post structure, hashtags, length limits | Change your tone, writing style, or how posts are structured |
| `config/sources.yaml` | RSS feeds and API sources | Add a new news site, disable a source, add a YouTube channel |
| `data/seen_articles.json` | Memory of already-used article URLs | Clear this to reset memory and allow re-use of old articles |
| `.claude/agents/news-gatherer.md` | How articles are fetched, scored, and filtered | Adjust scoring weights or filtering logic |
| `.claude/agents/trending-tracker.md` | How trending keywords are discovered | Change search angles or number of phrases returned |
| `.claude/agents/post-generator.md` | How posts are written — structure, rules, length | Change post format, add/remove sections, adjust rules |
| `.claude/agents/notion-publisher.md` | How drafts are pushed to Notion | Adjust block structure or Notion page layout |

---

## Setup Checklist

- [ ] Fill in `config/brand_kit.yaml` — set your `name`, `title`, and `location`
- [ ] (Optional) Set `NOTION_PAGE_ID` in `.env` to push drafts to Notion automatically
- [ ] (Optional) Set `NEWSAPI_KEY` in `.env` for broader news coverage, then set `enabled: true` in `config/sources.yaml → optional_apis.newsapi`

---

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter.

Each file contains:
- **YAML frontmatter** — source metadata, matched companies, categories, status
- **Post body** — the full LinkedIn draft, ready to review

Change `status: draft` to `status: published` to track what's gone live.

---

## Memory

`data/seen_articles.json` tracks article URLs used in previous runs.
The pipeline automatically skips articles that have already been drafted to avoid duplicates.

To reset and allow re-use of old articles:
```
Clear the seen articles memory.
```
Or manually edit `data/seen_articles.json` and set it to `[]`.
