# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## What It Does

1. Reads your **topics of interest** file to know which companies and keywords matter
2. Fetches **live AI news** from 20+ RSS feeds (TechCrunch, The Verge, VentureBeat, company blogs, YouTube channels, and more)
3. Tracks **trending keyword phrases** from the past 7 days using web search
4. Writes **branded LinkedIn posts** with cited sources, following your tone of voice exactly
5. Optionally **publishes drafts to Notion** for review before posting

Coverage includes: ChatGPT / OpenAI, Claude / Anthropic, Gemini / Google DeepMind, Perplexity, ElevenLabs, Midjourney, Runway, xAI/Grok, Meta AI, big tech AI (Microsoft, Apple, Amazon, Nvidia), AI startup funding rounds, and more.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and input/output contract. The orchestrator passes data between them — no Python glue code required.

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude reads `orchestrator.md` and executes the full pipeline automatically.

**Custom options:**
```
Run the LinkedIn Post Generator. Generate 3 posts.
Run the pipeline in dry-run mode — fetch and score news only, don't generate posts.
Run the pipeline and use 8 articles per post cluster.
```

---

## Configuration

All settings live in `config/` — five separate files, each controlling a different aspect:

| File | What to edit here |
|------|------------------|
| `config/topics.yaml` | AI companies and products to track, keyword categories, freshness settings |
| `config/sources.yaml` | RSS feeds and APIs; enable or disable individual sources |
| `config/brand_kit.yaml` | Your name, title, brand focus areas, content angles, hashtags, post length |
| `config/tone_of_voice.yaml` | Writing style rules, post structure blueprint, dos and don'ts, banned words |
| `config/research_standards.yaml` | Citation rules, minimum sources, URL integrity, quote verification |

Edit any file directly — changes take effect on the next pipeline run.

### Quick-start edits

**1. Set your name and title** → `config/brand_kit.yaml` → `author`

**2. Add a company you want to track** → `config/topics.yaml` → `companies_to_track`

**3. Add a news source** → `config/sources.yaml` → `rss_feeds`

**4. Change your writing tone** → `config/tone_of_voice.yaml` → `writing_style`

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in optional values:

```
NOTION_API_KEY=secret_xxx        # for Notion publishing
NOTION_PAGE_ID=your32charpageid  # your LinkedIn drafts Notion page
NEWSAPI_KEY=your_key_here        # optional broader news coverage
```

---

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-05-14_22-55-00_enterprise-ai-market-shift.md
  2026-05-14_23-10-00_vertical-ai-depth-over-horizontal.md
```

Each file contains:
- **YAML frontmatter**: source metadata, matched companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON
- **Output**: JSON array of scored article objects

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml` (seed terms)
- **Does**: Searches the web for trending AI topics from the past 7 days
- **Output**: JSON array of 15–20 keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/tone_of_voice.yaml`, `config/research_standards.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post, validates URLs, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, and source metadata

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page
- **Output**: `success` or `failed`

---

## Customising Your Voice

The post-generator reads three files on every run:

**`config/brand_kit.yaml`** — *Who you are and what you stand for*
Set your name, professional focus areas, content angles, and hashtag strategy here.

**`config/tone_of_voice.yaml`** — *How you write*
Writing style rules, post structure, dos and don'ts, banned words. This is the most powerful lever — changing these rules changes how every post sounds.

**`config/research_standards.yaml`** — *How you cite sources*
Minimum sources per post, quote format, URL rules. Raise `min_sources` if you want posts backed by more evidence.

---

## Adding News Sources

Edit `config/sources.yaml` to add any RSS feed:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

Set `enabled: false` to pause a feed without deleting it.
