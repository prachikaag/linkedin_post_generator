# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks trending topics, and writes research-backed LinkedIn posts in your voice — with cited sources. Built entirely on Claude agents. No code to run.

---

## What It Does

1. **Fetches fresh AI news** from 20+ RSS feeds (TechCrunch, Verge, company blogs, YouTube channels)
2. **Scores articles by relevance** using your watchlist of AI tools and topic keywords
3. **Finds trending keywords** from the last 7 days via web search
4. **Assigns a content pillar** to each post (AI tool launch, big tech, funding, or your personal experiments)
5. **Writes a branded LinkedIn draft** in your voice, with cited sources
6. **Saves to `posts/`** and optionally publishes to your Notion page
7. **Tracks post history** so you never repeat a topic

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

### Custom options

```
Run the pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Run the pipeline. Only post about AI startup funding this week.
```

---

## Editable Components

Everything is split into separate files you can tweak without touching any code:

```
config/
├── brand_kit.yaml         ← Your name, voice, tone, writing style, hashtags
├── content_pillars.yaml   ← The 4 content angles: launches, big tech, funding, experiments
├── ai_watchlist.yaml      ← The specific AI tools you follow closely (with scoring priority)
├── topics.yaml            ← All keywords and freshness settings for news scoring
└── sources.yaml           ← RSS feeds and APIs to pull news from

.claude/agents/
├── news-gatherer.md       ← Fetches + scores news articles
├── trending-tracker.md    ← Finds trending AI keyword phrases
├── post-generator.md      ← Writes the LinkedIn draft
└── notion-publisher.md    ← Publishes to Notion (optional)

data/
└── post_history.json      ← Tracks what's been generated/published (auto-updated)

posts/                     ← Generated draft posts (markdown files)
orchestrator.md            ← The pipeline controller (runs the agents in sequence)
```

---

## The 4 Content Pillars

Defined in `config/content_pillars.yaml`. Each post is automatically assigned to a pillar, which shapes the hook, framing, and CTA.

| Pillar | Covers | Your angle |
|--------|--------|------------|
| **AI Tool Launch** | New features, model releases, YouTube drops from ChatGPT, Claude, Gemini, ElevenLabs, Midjourney, Runway, etc. | What does this change for brands using or evaluating this tool? |
| **Big Tech AI** | Microsoft Copilot, Google Workspace AI, Apple Intelligence, Amazon Bedrock, Nvidia | What does this mean for the platforms brands already live in? |
| **AI Startup Funding** | Investment rounds, acquisitions, valuations, IPOs | What signal does this money send about where AI is heading? |
| **Human in the Loop** | Your personal AI experiments and workflow stories | What did I actually learn from doing this — not from reading about it? |

---

## Configuration Guide

### Your brand and voice — `config/brand_kit.yaml`

The most important file. Controls:
- Your name and professional tagline
- Tone traits (curious, pragmatic, opinionated — never corporate)
- Writing style rules (paragraph length, hook style, no buzzwords)
- Post structure blueprint (hook → context → evidence → take → so what → CTA → sources → hashtags)
- Hashtag strategy (always-include + rotation pool)
- Maximum post length (default: 1,457 characters / 251 words)
- Minimum sources per post (default: 4)

### What to write about — `config/content_pillars.yaml`

Edit pillar definitions to change:
- Which keywords trigger each pillar
- The framing angle for each pillar's "YOUR TAKE" section
- Hook starter templates
- CTA examples

### Tools you follow closely — `config/ai_watchlist.yaml`

Add or remove AI tools from your watchlist. `critical` tools get a `+5` relevance bonus in scoring — those articles always surface at the top. Edit freely as the AI landscape shifts.

### News sources — `config/sources.yaml`

Add any RSS feed:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high   # high | medium | low
      enabled: true
```

Disable any feed without deleting it: `enabled: false`

### Keywords and freshness — `config/topics.yaml`

Controls which companies and topics score articles, plus:
- `max_article_age_hours` — how fresh articles must be (default: 48h)
- `min_relevance_score` — minimum score to include (default: 2)
- `max_articles_per_run` — article cap per run (default: 25)

---

## Output

Posts are saved to `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file has YAML frontmatter (metadata) followed by the full post body. Update `status` to track what's gone live:

```yaml
status: "draft"      # just generated
status: "reviewed"   # you've read and approved it
status: "scheduled"  # queued to post
status: "published"  # live on LinkedIn
status: "archived"   # skipped / not posting
```

Post history is tracked automatically in `data/post_history.json`.

---

## Notion Integration (optional)

Set `NOTION_PAGE_ID` in your `.env` file to push every draft to a Notion page as a collapsible toggle block.

Setup steps:
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New integration (Internal)
2. Copy the token → paste as `NOTION_API_KEY` in `.env`
3. Open your LinkedIn Post Ideas Notion page → "..." → Connections → connect your integration
4. Copy the 32-char page ID from the URL → paste as `NOTION_PAGE_ID` in `.env`

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
NOTION_API_KEY=secret_xxx
NOTION_PAGE_ID=your_32char_page_id

# Optional: broader news coverage beyond RSS feeds
NEWSAPI_KEY=your_key_here
```

---

## Agents Reference

| Agent | Tools | Reads | Does |
|-------|-------|-------|------|
| `news-gatherer` | Read, WebFetch | `sources.yaml`, `topics.yaml`, `ai_watchlist.yaml` | Fetches RSS feeds, scores by relevance, deduplicates |
| `trending-tracker` | Read, WebSearch | `topics.yaml` | Finds 15–20 trending AI keyword phrases from the past 7 days |
| `post-generator` | Read, Write | `brand_kit.yaml`, `content_pillars.yaml` | Assigns a pillar, writes a branded draft, saves as `.md` |
| `notion-publisher` | Read, Notion MCP | `.env` | Appends draft to a Notion page as a toggle block |
