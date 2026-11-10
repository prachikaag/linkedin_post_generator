# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing across platforms, and writes research-backed LinkedIn draft posts in your brand voice — entirely through Claude agents and subagents. No traditional code steps.

---

## Quick Start (5 minutes)

### 1 — Personalise your brand kit

Open `config/brand_kit.yaml` and fill in:

```yaml
author:
  name: "Your Name"           # ← Your full name
  title: "Your LinkedIn Title" # ← e.g. "Brand Strategist & AI Experimentalist"
  location: "City, Country"   # ← e.g. "London, UK"
```

Everything else in `brand_kit.yaml` is already tuned for an AI + marketing voice — but read through it and adjust your `signature_phrases`, `tools_you_use`, and `content_angles` to match how you actually write.

### 2 — Set up Notion (optional)

```bash
cp .env.example .env
```

Open `.env` and set `NOTION_PAGE_ID` (the 32-char ID from your Notion page URL).

### 3 — Run the pipeline

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude reads `orchestrator.md` and executes the full pipeline automatically.

---

## How to Run

### Inside Claude Code

```
Run the LinkedIn Post Generator pipeline.
```

```
Run the pipeline and generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and score news only, no posts.
```

The pipeline:
1. Spawns **news-gatherer** → reads RSS feeds, scores articles by keyword relevance, skips already-seen articles
2. Spawns **trending-tracker** → searches the web for trending AI topics this week
3. For each article cluster → spawns **post-generator** → writes and saves a draft
4. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

---

## Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles, tracks seen URLs
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases via web search
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and input/output contract. The orchestrator passes data between them. No Python required.

---

## Editable Components

All settings live in `config/`. Edit these files directly — changes take effect on the next run.

### `config/topics.yaml` — What to watch

Controls **which news gets tracked**. Three sections:

| Section | Purpose |
|---------|---------|
| `companies_to_track.ai_labs` | AI companies (OpenAI, Anthropic, Google, Perplexity, ElevenLabs, Midjourney...) |
| `companies_to_track.ai_builders` | AI infrastructure & tooling companies |
| `companies_to_track.big_tech` | Microsoft, Apple, Amazon, Nvidia, Adobe... |
| `topic_categories` | Event types: launches, funding, marketing, research, regulation, tools |
| `trending_keywords.seed_terms` | Seed phrases used to find what's trending on the web |
| `freshness` | How old articles can be, minimum score, max articles per run |

**To add a company:**
```yaml
companies_to_track:
  ai_labs:
    - name: "New Company"
      keywords:
        - "New Company"
        - "their product name"
```

**To change how fresh articles must be:**
```yaml
freshness:
  max_article_age_hours: 72   # ← Increase from 48 if you want older news
  min_relevance_score: 2      # ← Lower to get more (but less relevant) articles
```

---

### `config/brand_kit.yaml` — How you write

Controls **every aspect of your writing voice**. Key sections:

| Section | Purpose |
|---------|---------|
| `author` | Your name, title, tagline, location |
| `tone_of_voice.primary_traits` | How you come across to your audience |
| `tone_of_voice.writing_style` | Rules applied to every post |
| `tone_of_voice.post_structure` | The ordered blueprint: HOOK → CONTEXT → EVIDENCE → YOUR TAKE → SO WHAT → CTA → SOURCES → HASHTAGS |
| `tone_of_voice.dos` | What makes a great post from you |
| `tone_of_voice.donts` | What undermines your credibility |
| `brand.focus_areas` | The lenses you write through |
| `brand.content_angles` | Preferred post angles (e.g. "I tried X for Y — here's what happened") |
| `brand.tools_you_use` | AI tools you personally experiment with (mentioned in first-person posts) |
| `brand.hashtags` | Always-include tags + rotation pool |
| `brand.post_length` | "short" / "medium" / "long" |
| `research_standards` | Minimum sources, citation format |

---

### `config/sources.yaml` — Where to look

Controls **which RSS feeds are fetched**. Sections:

| Section | Feeds included |
|---------|---------------|
| `rss_feeds.ai_news` | TechCrunch AI, The Verge, VentureBeat, Wired, MIT Technology Review, Ars Technica... |
| `rss_feeds.company_blogs` | OpenAI, Anthropic, Google AI, DeepMind, Meta AI, Microsoft AI, Hugging Face... |
| `rss_feeds.funding_news` | TechCrunch Startups, Crunchbase News, SiliconAngle |
| `rss_feeds.youtube_channels` | Google DeepMind YouTube, OpenAI YouTube, Anthropic YouTube, Two Minute Papers |
| `optional_apis.newsapi` | Broader NewsAPI coverage (requires free API key) |

**To add a source:**
```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high   # high / medium / low
      enabled: true
```

**To disable a feed without deleting it:**
```yaml
    - name: "The Information AI"
      url: "..."
      enabled: false   # ← set to false
```

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-01-15_10-30-00_openai-launches-gpt5.md
  2026-01-15_10-32-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies matched, categories, trending keywords used, status
- **Post body**: the full LinkedIn draft, ready to review and edit before posting

Change `status: draft` to `status: published` to track what's gone live.

---

## Deduplication

The pipeline tracks which article URLs it has already processed in `data/seen_articles.json`. On each run, the news-gatherer skips any article it has seen in the past 30 days. This prevents duplicate posts being generated for the same news story across runs.

The `data/seen_articles.json` file is excluded from git (see `.gitignore`) so it stays local to your machine.

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, Write, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`, `data/seen_articles.json`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, skips previously seen URLs, deduplicates, returns top articles as JSON. Updates `data/seen_articles.json` after each run.
- **Output**: JSON array of scored article objects

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days across model launches, funding, and research angles
- **Output**: JSON array of 15–20 keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post, validates URLs (only uses URLs verbatim from source articles), saves as `.md` draft with YAML frontmatter
- **Output**: JSON object with filename, filepath, content, and source metadata

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page, with a "Draft" callout and all source lines as paragraphs
- **Output**: `success` or `failed`

---

## Customising Your Brand Voice

The post-generator reads `config/brand_kit.yaml` on every run — no restarts needed.

Key things to personalise:
1. **`author.name`** — your name appears in first-person framing
2. **`brand.tools_you_use`** — the AI tools you actually experiment with; these get mentioned authentically
3. **`brand.content_angles`** — your preferred post angles (e.g. "I tried [X] for [Y] — here's what happened")
4. **`brand.signature_phrases`** — your distinctive phrases, used to end posts
5. **`tone_of_voice.donts`** — add any phrases or patterns you want the AI to avoid

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `NOTION_API_KEY` | Optional | Notion integration token (for Notion publishing) |
| `NOTION_PAGE_ID` | Optional | 32-char ID of your Notion page — enables Notion publishing |
| `NEWSAPI_KEY` | Optional | Free key from newsapi.org for broader coverage |
| `ANTHROPIC_API_KEY` | Optional | Only needed outside of Claude Code |

```bash
cp .env.example .env   # then fill in your values
```
