# LinkedIn Post Generator — Claude Code Guide

This project runs entirely inside Claude Code. No Python, no scripts, no manual steps.
The orchestrator spawns specialised subagents that fetch news, find trends, and write posts.

---

## Quick Start

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. The full pipeline runs and saves draft posts to `posts/`.

---

## What the Pipeline Does

1. **Fetches AI news** from RSS feeds and company blogs (see `config/sources.yaml`)
2. **Scores articles** by relevance to your tracked companies and topics (`config/topics.yaml`)
3. **Finds trending keywords** by searching the web for what's buzzing in AI right now
4. **Assigns a content pillar** to each article cluster:
   - New AI feature or product launch
   - Big tech AI news
   - AI startup funding
   - Human in the loop (your experiments)
5. **Writes LinkedIn post drafts** in your voice using your brand kit (`config/brand_kit.yaml`)
6. **Saves drafts** to `posts/` as markdown files with YAML frontmatter
7. **Publishes to Notion** (if `NOTION_PAGE_ID` is set in `.env`)

---

## Controlling the Run

### Generate more or fewer posts

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

### Fetch-only (no post writing)

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

### Focus on one content pillar

```
Run the LinkedIn Post Generator pipeline. Focus on product launches only.
```

### Specific topic

```
Run the LinkedIn Post Generator pipeline. Focus on ElevenLabs news only.
```

---

## Files to Edit

Everything is a config file — edit directly, changes take effect on the next run.

| File | What it controls |
|------|-----------------|
| `config/brand_kit.yaml` | Your name, tone, voice, writing style, hashtags |
| `config/content_pillars.yaml` | Your four content angles and how to write each |
| `config/topics.yaml` | Companies and keywords to track |
| `config/sources.yaml` | RSS feeds, company blogs, YouTube channels |
| `.env` | API keys (Notion, NewsAPI) |

---

## Your Four Content Pillars

Defined in `config/content_pillars.yaml`. Each post maps to one:

### 1. New AI Feature or Product Launch
When ChatGPT, Claude, Gemini, Perplexity, ElevenLabs, Midjourney, Runway, or others
ship a new feature, model, or a notable YouTube video. Write what brands should know.

### 2. Big Tech AI News
Microsoft, Google, Apple, Amazon, Nvidia, Salesforce, Meta — strategic moves that
signal where enterprise AI is heading. Translate it for brand and marketing leaders.

### 3. AI Startup Funding
Funding rounds, acquisitions, IPOs. Decode what money flowing into AI tells us about
where the market is heading and what it means for the vendor landscape.

### 4. Human in the Loop — My AI Experiments
First-person accounts of using AI tools in real work. You direct, edit, and test.
Share honest results — what worked, what didn't, what you changed, what you learned.

---

## Personalising Your Brand Kit

Edit `config/brand_kit.yaml`:

```yaml
author:
  name: "Prachi"          # ← your name
  title: "Your title"     # ← your LinkedIn title
  tagline: "..."          # ← your LinkedIn headline
  location: "City, Country"
```

The post-generator reads this file on every run — no restarts needed.

---

## Reviewing Draft Posts

Posts are saved to `posts/` as markdown files:

```
posts/
  2026-09-03_09-00-00_elevenlabs-launches-voice-design.md
  2026-09-03_09-00-00_anthropic-raises-4b-series-e.md
```

Each file has YAML frontmatter (metadata) followed by the post body.

To publish: copy the post body into LinkedIn directly.
To track what's live: change `status: draft` to `status: published` in the frontmatter.

---

## Notion Integration (Optional)

If you have a Notion page where you store post ideas:

1. Create a Notion integration at https://www.notion.so/my-integrations
2. Copy `.env.example` to `.env`
3. Add your `NOTION_API_KEY` and `NOTION_PAGE_ID` to `.env`
4. Connect your integration to the Notion page

Each generated post will appear as a collapsible toggle block on your Notion page.

---

## Adding a New News Source

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  company_blogs:
    - name: "New Source Name"
      url: "https://example.com/blog/rss"
      priority: high   # high | medium | low
      enabled: true
```

---

## Adding a Company to Track

Edit `config/topics.yaml`:

```yaml
companies_to_track:
  ai_labs:
    - name: "New Company"
      keywords:
        - "Company Name"
        - "Product Name"
        - "Alternative Name"
```

---

## Troubleshooting

**No articles found:**
In `config/topics.yaml`, increase `max_article_age_hours` or decrease `min_relevance_score`.

**Posts too long / too short:**
In `config/brand_kit.yaml`, change `post_length` to `short`, `medium`, or `long`.

**A source keeps failing:**
Set `enabled: false` in `config/sources.yaml` for that source.

**Notion not publishing:**
Check that `NOTION_PAGE_ID` is set in `.env` and your integration is connected to the page.
