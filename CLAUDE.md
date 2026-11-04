# LinkedIn Post Generator — Claude Code Guide

## What This Project Does

An AI-powered pipeline that:
1. Fetches fresh AI news from RSS feeds and company blogs
2. Tracks trending keyword phrases from the last 7 days
3. Writes branded LinkedIn posts in your voice, with cited sources
4. Optionally publishes drafts to Notion for review

Target content: AI tool launches, big-tech AI news, startup funding rounds, and personal AI experimentation angles — all filtered through a marketing and brand strategy lens.

---

## How to Run the Pipeline

Say this to Claude Code:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude reads `orchestrator.md` and runs the full pipeline end-to-end.

### Options

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
Run the pipeline in dry-run mode — fetch news only, don't generate posts.
Run the pipeline. Use 8 articles per post cluster.
```

---

## Pipeline Steps

```
orchestrator.md
  ├── [Step 1] .claude/agents/news-gatherer.md      → fetches + scores RSS articles
  ├── [Step 2] .claude/agents/trending-tracker.md   → finds trending keyword phrases
  ├── [Step 3] .claude/agents/post-generator.md     → writes + saves LinkedIn drafts
  └── [Step 4] .claude/agents/notion-publisher.md   → pushes drafts to Notion
```

Each agent is a self-contained markdown file you can edit without touching any code.

---

## Configuration Files

All settings live in `config/`. Edit these files to change how the pipeline behaves.

### `config/brand_kit.yaml` — YOUR MOST IMPORTANT CONFIG

This is what makes every post sound like you. Edit:

- `author.name`, `author.title`, `author.tagline` — fill these in with your real details
- `tone_of_voice.primary_traits` — how you come across to your audience
- `tone_of_voice.writing_style` — your writing rules
- `tone_of_voice.post_structure` — the blueprint every post follows
- `brand.focus_areas` — the lenses you write through
- `brand.hashtags` — always-on + rotation hashtags
- `brand.signature_phrases` — phrases that are distinctly yours

### `config/topics.yaml` — What to Track

- `companies_to_track` → AI labs, builders, and big-tech companies to monitor
- `topic_categories` → types of stories: launches, funding, research, regulation, etc.
- `freshness.max_article_age_hours` → how fresh articles need to be (default 48h)
- `freshness.min_relevance_score` → minimum score to include (default 2)

### `config/sources.yaml` — Where to Fetch News

- `rss_feeds.ai_news` → general AI news publications
- `rss_feeds.company_blogs` → official blogs from AI companies
- `rss_feeds.funding_news` → startup and funding coverage
- `rss_feeds.youtube_channels` → YouTube channel update feeds from AI companies
- `optional_apis.newsapi` → enable for broader coverage (requires free NEWSAPI_KEY in .env)

---

## Customising Your Voice (Most Important Step)

Open `config/brand_kit.yaml` and update `author:` with your real details:

```yaml
author:
  name: "Your Full Name"
  title: "Your LinkedIn Headline"
  tagline: "One-line description of what you help people with"
  location: "City, Country"
```

The post-generator reads this file on every run — no restart needed.

---

## Generated Posts

Drafts are saved to `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file has:
- **YAML frontmatter** — sources, companies, categories, trending keywords, `status: draft`
- **Post body** — the full LinkedIn draft, ready to copy and publish

Change `status: draft` → `status: published` to track what's gone live.

---

## Notion Integration (Optional)

Set in `.env`:

```
NOTION_PAGE_ID=your_32char_page_id
NOTION_API_KEY=secret_xxx  (only needed for direct REST fallback)
```

The pipeline uses the Notion MCP connector (no key needed if signed in via Claude Code). Posts appear as toggle blocks on your Notion page, one per run.

---

## Adding a New RSS Feed

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My New Source"
      url: "https://example.com/feed.xml"
      priority: high   # high | medium | low
      enabled: true
```

## Adding a YouTube Channel

```yaml
rss_feeds:
  youtube_channels:
    - name: "Channel Name"
      url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE"
      priority: medium
      enabled: true
```

Find a channel's ID by visiting the channel page and checking the URL, or use a YouTube Channel ID finder tool.
