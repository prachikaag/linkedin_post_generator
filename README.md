# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

Built for: **Brand and marketing professionals** who want to stay visible as an AI-informed voice, without spending hours writing from scratch.

---

## What It Does

1. **Reads your topics of interest** from `config/topics.yaml` — companies, keywords, and categories you care about
2. **Fetches relevant news** from 20+ RSS feeds and company blogs across AI, BigTech, and startup funding
3. **Tracks trending keywords** from the past 7 days across the AI space
4. **Filters already-seen articles** using `memory/seen_articles.json` so you never get duplicate posts
5. **Writes custom LinkedIn posts** in your voice, citing real sources, following your brand guidelines
6. **Saves drafts** to `posts/` for your review before publishing
7. **Publishes to Notion** (optional) for easy review and editing

---

## Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles (+ memory filter)
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file. The orchestrator passes data between them — no Python glue code.

---

## The Editable Components

These are the files you'll edit to customise the generator:

| File | What It Controls | Edit When |
|------|-----------------|-----------|
| `config/topics.yaml` | Companies and keywords to track, freshness settings | You want to add/remove AI companies or topics |
| `config/sources.yaml` | RSS feeds and APIs to fetch from | You want new news sources |
| `config/brand_kit.yaml` | Your name, voice, tone, writing style, hashtags | You want to change how posts sound |
| `config/content_pillars.yaml` | The 4 post angles and when to use each | You want to refine your content strategy |
| `memory/seen_articles.json` | URLs of articles already turned into posts | Add URLs manually to exclude specific articles |

---

## How to Run

### Inside Claude Code (the only way to run this)

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with custom parameters:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

Claude Code will read `orchestrator.md` and run the full pipeline:
1. Loads seen article URLs from `memory/seen_articles.json`
2. Spawns **news-gatherer** → fetches RSS feeds, returns new unseen articles
3. Spawns **trending-tracker** → finds trending AI topics via web search
4. For each article cluster, spawns **post-generator** → writes and saves a draft
5. Updates `memory/seen_articles.json` with newly processed URLs
6. Spawns **notion-publisher** → pushes drafts to Notion (if configured)

---

## The Four Content Pillars

Every post follows one of four angles, chosen automatically based on the article type:

| Pillar | When Used | Example Hook |
|--------|-----------|--------------|
| **AI Tool Experiments** | New product launch, YouTube demo | "I tried [tool] for [brand task] — here's what actually happened." |
| **AI News for Brands** | BigTech announcements, funding rounds | "[Company] just made a move. Here's what brand teams need to know." |
| **The Pattern Behind the News** | Multiple related events in one cycle | "Three things happened in AI this week. They look unrelated. They're not." |
| **Contrarian Takes** | Overhyped announcements, misapplied trends | "Hot take: [mainstream view] is overstated. Here's the evidence." |

Edit `config/content_pillars.yaml` to customise these angles.

---

## What Gets Tracked (Topics of Interest)

From `config/topics.yaml`:

**AI Labs & Models**: OpenAI (ChatGPT, GPT-5, Sora), Anthropic (Claude), Google DeepMind (Gemini, Veo), Perplexity, ElevenLabs, Midjourney, Runway, xAI (Grok), Meta AI (LLaMA), Mistral, and more

**BigTech AI**: Microsoft Copilot, Apple Intelligence, Amazon Bedrock, Nvidia, Salesforce Einstein, Adobe Firefly

**AI Builders & Startups**: Cerebras, Groq, Harvey AI, Cognition AI, Scale AI, Writer, Cursor, Suno, Synthesia

**Topic Categories**: Product launches, startup funding, AI for marketing, research breakthroughs, regulation, productivity tools, YouTube video releases, human-in-the-loop workflows

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# Required for Notion publishing (optional feature)
NOTION_PAGE_ID=your_32char_page_id_here

# Optional: direct Notion REST API fallback
NOTION_API_KEY=secret_xxx

# Optional: NewsAPI for additional sources
NEWSAPI_KEY=your_key_here
```

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-08-12_10-30-00_openai-launches-new-feature.md
  2026-08-12_10-30-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Memory System

`memory/seen_articles.json` tracks every article URL that has been turned into a post.

On each run, the news-gatherer filters out already-seen URLs — so you never get a duplicate post across runs.

To manually exclude a specific article, add its URL to `seen_urls` in `memory/seen_articles.json`.

---

## Personalising Your Brand

Edit `config/brand_kit.yaml` to set:
- **Your name and title** — appears as the post author context
- **Tone traits** — curious, pragmatic, opinionated, etc.
- **Writing style rules** — paragraph length, hook style, etc.
- **Post structure preferences** — which sections appear and in what order
- **Hashtag strategy** — always-include vs. rotation pool
- **Signature phrases** — distinctive lines that are uniquely yours

The post-generator reads this file on every run — no restarts needed.

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`, `memory/seen_articles.json`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, filters already-seen URLs, returns top new articles as JSON

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days
- **Output**: JSON array of 15–20 keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/content_pillars.yaml`
- **Does**: Selects the right content pillar, synthesises a cluster of articles into a branded LinkedIn post, validates URLs, saves as `.md` draft

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page
- **Output**: `success` or `failed`

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
