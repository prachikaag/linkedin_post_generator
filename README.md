# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks trending topics, and writes research-backed LinkedIn draft posts in your brand voice — entirely through Claude agents. No code required to run.

---

## What It Does

1. **Scans AI news** — fetches the latest from 25+ RSS feeds covering AI companies, startup funding, big tech moves, and YouTube video launches
2. **Tracks what's trending** — finds the keyword phrases generating the most buzz this week across AI topics
3. **Writes in your voice** — uses your brand kit to draft posts with proper tone, structure, citations, and hashtags
4. **Remembers what it's covered** — tracks published stories so it never writes the same post twice
5. **Sends drafts to Notion** — optionally pushes generated drafts to your LinkedIn Post Ideas Notion page

---

## Architecture

```
orchestrator.md                         ← Run this to start
├── .claude/agents/news-gatherer.md     → Fetches + scores RSS articles
├── .claude/agents/trending-tracker.md  → Finds trending AI keyword phrases
├── .claude/agents/post-generator.md    → Writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md  → Publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role and instructions. The orchestrator passes data between them — no Python code required.

---

## Components You Can Edit

All configuration lives in `config/` — edit any file and changes take effect on the next run:

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Companies to track, keywords, freshness settings |
| `config/brand_kit.yaml` | Your name, voice, tone rules, post structure, hashtags |
| `config/sources.yaml` | RSS feeds and news sources (add/remove/enable/disable) |
| `config/content_themes.yaml` | Weekly editorial themes, post frequency, priority topics |
| `data/published_memory.yaml` | Auto-updated: URLs of articles already turned into posts |

### Agent files (advanced edits)

| File | What it controls |
|------|-----------------|
| `.claude/agents/news-gatherer.md` | How articles are fetched, scored, and filtered |
| `.claude/agents/trending-tracker.md` | How trending keywords are discovered |
| `.claude/agents/post-generator.md` | Post types, structure rules, writing instructions |
| `.claude/agents/notion-publisher.md` | How drafts are formatted and sent to Notion |

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

### With custom parameters:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Setup

### 1. Fill in your brand kit

Edit `config/brand_kit.yaml` — find the `author:` section at the top and fill in:
- Your name
- Your professional title
- Your LinkedIn tagline
- Your location

Everything else in the brand kit already has sensible defaults — tweak as you go.

### 2. Set up Notion (optional but recommended)

Copy `.env.example` to `.env` and fill in:

```bash
NOTION_PAGE_ID=your_32char_page_id_here   # From your Notion page URL
NOTION_API_KEY=secret_xxx                  # From Notion integration settings
```

Setup steps:
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New integration
2. Copy the token → `NOTION_API_KEY`
3. Open your LinkedIn Post Ideas Notion page
4. Connect your integration via "..." → Connections
5. Copy the 32-char ID from the page URL → `NOTION_PAGE_ID`

### 3. Adjust your weekly themes (optional)

Edit `config/content_themes.yaml` to set which AI topics you want to focus on each week.

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2026-08-11_10-30-00_openai-launches-gpt5-model.md
  2026-08-11_10-30-00_anthropic-raises-series-e.md
```

Each file contains YAML frontmatter (metadata) + the full LinkedIn post body, ready to review and copy-paste.

Change `status: draft` to `status: published` in the frontmatter to track what's gone live.

---

## Post Types

The pipeline generates two types of posts based on the news:

**Research-backed news posts** — for funding rounds, big tech moves, AI regulation, market shifts:
- Hook → Context → Evidence (multi-source) → Your Take → So What → CTA → Sources → Hashtags

**AI Experimentation / Human-in-the-loop posts** — for new tool launches, model releases, YouTube videos from tracked AI companies:
- Hook → What's New → Practitioner's Take → Brand Implications → CTA → Sources → Hashtags

The post type is chosen automatically based on the anchor article.

---

## Content Focus

The generator is tuned to watch for:
- **AI tool launches**: ChatGPT, Claude, Perplexity, Gemini, ElevenLabs, Midjourney, Runway, Pika
- **Big Tech AI moves**: Google, Microsoft, Apple, Amazon, Meta, Nvidia, Salesforce, Adobe
- **AI startup funding**: Series A/B/C rounds, acquisitions, IPOs, notable valuations
- **YouTube videos**: New video releases from tracked AI company channels
- **AI for marketing/brands**: How AI is changing creative work, campaigns, and strategy
- **Research breakthroughs**: New models, benchmarks, capability milestones

Adjust `config/topics.yaml` to add or remove any company or keyword category.

---

## Preventing Duplicate Posts

After each run, `data/published_memory.yaml` is updated with the URLs of articles used as anchor sources. On the next run, the news-gatherer skips any article whose URL is already in this file. This prevents re-writing posts on the same stories.

To reset the memory (e.g. if you want to re-cover a topic), edit `data/published_memory.yaml` and remove the relevant URL entries.
