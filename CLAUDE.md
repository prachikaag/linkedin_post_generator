# LinkedIn Post Generator — Claude Code Guide

A multi-agent LinkedIn post pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed draft posts in your voice — entirely through Claude agents. No code to run.

---

## Quick Start

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude will orchestrate the full pipeline and save 2 draft posts to `posts/`.

---

## What the Pipeline Does

```
[news-gatherer]      → fetches RSS feeds, scores articles by relevance
[trending-tracker]   → searches what's buzzing in AI right now
[post-generator]     → writes 2 LinkedIn drafts synthesising articles + trends
[experiment-writer]  → (optional) turns your experiment journal into posts
[notion-publisher]   → (optional) pushes drafts to your Notion page
```

All output lands in `posts/` as `.md` files with YAML frontmatter you can track.

---

## How to Run (Common Commands)

**Full pipeline — news + drafts:**
```
Run the LinkedIn Post Generator pipeline.
```

**More posts:**
```
Run the LinkedIn Post Generator pipeline. Generate 4 posts.
```

**Dry run — fetch news only, no post writing:**
```
Run the pipeline in dry-run mode.
```

**Experiments only — posts from your personal AI experiment journal:**
```
Run the experiment-writer agent to generate posts from my experiment journal.
```

**News + experiments together:**
```
Run the LinkedIn Post Generator pipeline and include any unposted experiments.
```

---

## Configuration Files (Edit These)

All settings are in `config/`. Changes take effect on the next run — no restarts needed.

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Companies, keywords, and freshness settings to track |
| `config/brand_kit.yaml` | Your name, voice, tone, post structure, hashtags |
| `config/sources.yaml` | RSS feeds and news sources to fetch |
| `config/my_experiments.md` | Your personal AI experiment log — turned into "human in the loop" posts |
| `config/post_history.yaml` | Tracks published posts to avoid duplicates |

---

## Your Personal Experiments — The Human-in-the-Loop Posts

The pipeline has a special mode for posts about **your own AI experiments** — the "I tried [tool] for [use case] — here's what actually happened" format.

**How it works:**
1. Open `config/my_experiments.md`
2. Add an entry every time you try something interesting with an AI tool
3. Mark it `post_ready: true` when you want a post written
4. Run: `Run the experiment-writer agent`
5. The agent writes a post in your voice and marks the entry as `status: posted`

This produces your most authentic content — personal observations, real outcomes, your honest take.

---

## Agents Reference

| Agent | File | What it does |
|-------|------|-------------|
| Orchestrator | `orchestrator.md` | Master pipeline — reads this to run everything |
| News Gatherer | `.claude/agents/news-gatherer.md` | Fetches RSS feeds, scores + ranks articles |
| Trending Tracker | `.claude/agents/trending-tracker.md` | Finds what's buzzing in AI this week |
| Post Generator | `.claude/agents/post-generator.md` | Writes news-based LinkedIn drafts |
| Experiment Writer | `.claude/agents/experiment-writer.md` | Writes posts from your personal experiments |
| Notion Publisher | `.claude/agents/notion-publisher.md` | Pushes drafts to Notion (requires NOTION_PAGE_ID) |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
NOTION_PAGE_ID=your_32char_page_id   # Required for Notion publishing
NOTION_API_KEY=secret_xxx            # Required for Notion publishing
NEWSAPI_KEY=your_key_here            # Optional — broader news coverage
```

Notion publishing is skipped automatically if `NOTION_PAGE_ID` is not set.

---

## Output Format

Posts are saved to `posts/` as:
```
posts/2026-08-13_10-30-00_openai-launches-gpt5.md
```

Each file has YAML frontmatter (title, sources, status) and the full post body.

Change `status: draft` → `status: published` to track what's gone live.

---

## Customising Your Brand

Edit `config/brand_kit.yaml`:

- **Your name and title** — `author.name`, `author.title`, `author.tagline`
- **Tone traits** — what `primary_traits` list under `tone_of_voice`
- **Writing rules** — `writing_style` list
- **Post structure** — `post_structure` list
- **Hashtag strategy** — `brand.hashtags`
- **Post length** — `brand.post_length` (short / medium / long)

---

## Adding News Sources

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

Any valid RSS 2.0 or Atom feed works.

---

## Tracking What's Been Published

`config/post_history.yaml` keeps a list of published posts. The pipeline reads this to avoid generating duplicate content.

Mark a post published by updating its `status` in the `.md` file frontmatter, then adding it to `post_history.yaml`.
