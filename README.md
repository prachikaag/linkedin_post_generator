# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## What it does

1. **Reads your topics** from `config/topics.yaml` — every AI company, product, and theme you care about
2. **Fetches news** from 25+ RSS feeds (TechCrunch, The Verge, VentureBeat, company blogs, YouTube channels, and more)
3. **Tracks trending keywords** across the web for the past 7 days
4. **Scores and ranks articles** by relevance to your topics
5. **Skips stories you've already covered** (memory system tracks seen articles across runs)
6. **Writes LinkedIn posts** in your exact brand voice — with cited sources, your hook style, and your hashtags
7. **Saves drafts** to `posts/` as markdown files
8. **Optionally pushes to Notion** for review before publishing

---

## First-time setup

### 1. Fill in your brand kit

Edit `config/brand_kit.yaml` and replace the placeholder values at the top:

```yaml
author:
  name: "Your Full Name"           # ← your name
  title: "Your LinkedIn Title"     # ← e.g. "Brand Strategist & AI Consultant"
  tagline: "..."                   # ← your one-liner value prop
  location: "City, Country"        # ← optional
```

Everything else in that file is already tuned for an opinionated AI + brands voice — tweak it to match your style.

### 2. Configure Notion (optional but recommended)

To get drafts pushed straight to Notion:

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New Integration
2. Copy the token → set `NOTION_API_KEY` in `.env`
3. Open your LinkedIn Post Ideas page in Notion
4. `...` menu → Connections → connect your integration
5. Copy the 32-char page ID from the URL → set `NOTION_PAGE_ID` in `.env`

The `.env` file is already created (gitignored). Just open it and fill in the values.

### 3. Optionally add NewsAPI

For broader news coverage beyond RSS feeds, get a free key at [newsapi.org](https://newsapi.org/), set `NEWSAPI_KEY` in `.env`, then set `enabled: true` in `config/sources.yaml` under `optional_apis.newsapi`.

---

## How to run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code reads `orchestrator.md` and runs the full pipeline automatically.

### Custom run options

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Run the pipeline. Generate 1 post focused on funding news.
```

---

## Architecture

The pipeline is a multi-agent system where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles (filters seen)
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases via web search
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
├── .claude/agents/memory-updater.md     → records seen URLs + post history
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and input/output contract.

---

## Configuration files

| File | What to edit |
|------|-------------|
| `config/topics.yaml` | Companies, products, and keywords to track. Add or remove entries here. |
| `config/brand_kit.yaml` | Your name, tone of voice, writing style, post structure, hashtags. |
| `config/sources.yaml` | RSS feeds and news sources. Enable/disable feeds, add custom ones. |

All changes take effect on the next run — no restart needed.

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: all source metadata, companies matched, categories, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Once you've published a post on LinkedIn, change `status: draft` to `status: published` to keep track.

---

## Memory system

After each run, the pipeline automatically updates:

| File | Purpose |
|------|---------|
| `memory/seen_articles.json` | URLs of articles already used — skipped on future runs |
| `memory/post_history.json` | Log of every post ever generated |

To reset and allow re-coverage of old topics, delete entries from `memory/seen_articles.json`.

---

## Agents reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`, `memory/seen_articles.json`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, filters already-seen URLs, deduplicates, returns top articles as JSON

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post, validates all URLs, saves as `.md` draft

### `memory-updater`
- **Tools**: Read, Write
- **Does**: Appends used article URLs to `memory/seen_articles.json` and logs the new posts to `memory/post_history.json`

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a collapsible toggle block on a Notion page

---

## Adding news sources

Edit `config/sources.yaml` to add any RSS feed:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

YouTube channel RSS URLs follow this pattern:
```
https://www.youtube.com/feeds/videos.xml?channel_id=<CHANNEL_ID>
```

---

## Topics already tracked

The following companies and products are tracked by default in `config/topics.yaml`. Edit the file to add more.

**AI Labs**: OpenAI / ChatGPT, Anthropic / Claude, Google DeepMind / Gemini, Perplexity, ElevenLabs, Midjourney, xAI / Grok, Meta AI / LLaMA, Mistral, Runway, Stability AI, Pika Labs, Cohere, HuggingFace

**AI Builders**: Cerebras, Groq, Harvey AI, Cognition / Devin, Cursor, Suno, Synthesia, Scale AI, Glean, Writer

**Big Tech**: Microsoft Copilot, Apple Intelligence, Amazon / AWS AI, Nvidia, Salesforce Agentforce, Adobe Firefly

**Topic categories**: Feature launches, Startup funding, AI for marketing, Research breakthroughs, AI regulation, AI productivity tools
