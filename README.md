# LinkedIn Post Generator

An AI-powered pipeline that reads your topics of interest, fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts in your exact brand voice — with cited sources, saved to `posts/` as markdown files.

---

## How it works

```
config/topics.yaml      ──→  what news to look for
config/sources.yaml     ──→  which RSS feeds to fetch
         ↓
[news_gatherer]         ──→  fetches + scores articles by relevance
[trending_tracker]      ──→  finds trending AI keywords this week
         ↓
[post_generator]        ──→  Claude writes branded LinkedIn drafts
         ↓
[notion_publisher]      ──→  saves drafts to Notion (optional)
config/brand_kit.yaml   ──→  your voice, tone, structure, hashtags
```

Every component is a separate, editable file. Change a config → the next run uses it.

---

## Quick start

```bash
# 1. Clone and enter the repo
git clone https://github.com/prachikaag/linkedin_post_generator
cd linkedin_post_generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your environment
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY (required)

# 4. Fill in your details in config/brand_kit.yaml
#    Set: author.name, author.title, author.tagline

# 5. Run
python main.py
```

---

## Running options

```bash
python main.py                    # generate 2 posts (default)
python main.py --posts 3          # generate 3 posts
python main.py --posts 1          # quick single post
python main.py --dry-run          # fetch + rank news only, no generation
python main.py --pool-size 8      # use 8 articles per post (default: 6)
python main.py --no-notion        # skip Notion even if configured
```

---

## Configuration

All settings live in `config/`. Edit any file — changes take effect on the next run.

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Companies to track, keywords, freshness window |
| `config/sources.yaml` | RSS feeds (enabled/disabled, priority) |
| `config/brand_kit.yaml` | Your name, tone, writing style, post structure, hashtags |

### `config/topics.yaml` — what news to track

Add or remove companies, keywords, and topic categories:

```yaml
companies_to_track:
  ai_labs:
    - name: "OpenAI"
      keywords:
        - "OpenAI"
        - "ChatGPT"
        - "GPT-5"
```

Adjust freshness and volume:

```yaml
freshness:
  max_article_age_hours: 48   # only articles this recent
  min_relevance_score: 2      # minimum score to include
  max_articles_per_run: 25    # cap articles fetched per run
```

### `config/sources.yaml` — where to get news

Includes:
- Direct RSS feeds from TechCrunch, The Verge, VentureBeat, company blogs, etc.
- Google News RSS (topic-specific queries, no API key needed)
- YouTube channel feeds for OpenAI, Anthropic, DeepMind

Enable or disable any feed:

```yaml
- name: "TechCrunch AI"
  url: "https://techcrunch.com/category/artificial-intelligence/feed/"
  priority: high
  enabled: true   # ← set to false to skip
```

Add your own feeds:

```yaml
- name: "My Custom Source"
  url: "https://example.com/feed.xml"
  priority: medium
  enabled: true
```

### `config/brand_kit.yaml` — your voice

Set your identity:

```yaml
author:
  name: "Your Name"
  title: "Brand Strategist & AI Enthusiast"
  tagline: "Helping brands understand and leverage AI in the real world"
```

The brand kit controls every aspect of post writing:
- `tone_of_voice.primary_traits` — how you come across
- `tone_of_voice.writing_style` — sentence length, hooks, emoji rules
- `tone_of_voice.post_structure` — HOOK → CONTEXT → EVIDENCE → YOUR TAKE → SO WHAT → CTA
- `brand.hashtags` — always-included + rotation pool
- `brand.max_characters` / `brand.max_words` — post length limits
- `research_standards.min_sources` — minimum sources cited per post

---

## Environment variables

Copy `.env.example` to `.env` and fill in:

```bash
# Required — your Anthropic API key
# Get one at https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-...

# Optional — override the default model
ANTHROPIC_MODEL=claude-sonnet-4-6

# Optional — publish drafts to Notion
# Setup: notion.so/my-integrations → New integration → copy token
NOTION_API_KEY=secret_...
# Open your Notion page → "..." → Connections → add your integration
# Copy the 32-char ID from the page URL
NOTION_PAGE_ID=your_page_id_here
```

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2026-05-18_14-30-00_openai-launches-gpt5-model.md
  2026-05-18_14-31-15_anthropic-funding-round.md
```

Each file has YAML frontmatter (metadata) followed by the post body:

```yaml
---
title: "OpenAI launches GPT-5"
date: "2026-05-18"
status: "draft"       ← change to "published" to track what's gone live
primary_source_url: https://...
source_count: 6
matched_companies:
  - OpenAI
  - Anthropic
matched_categories:
  - New AI Feature or Product Launch
---

Post body here...
```

---

## What gets written about

The generator is tuned to cover:

- **New AI product launches and features** — ChatGPT, Claude, Gemini, Perplexity, ElevenLabs, Midjourney, etc.
- **AI startup funding rounds** — seed, Series A/B/C, acquisitions, IPOs
- **Big tech AI moves** — Microsoft, Google, Apple, Amazon, Nvidia, Adobe
- **AI for marketing and brands** — how brands are using AI in creative, strategy, and content
- **Human-in-the-loop experiments** — practical AI workflows you're testing
- **AI research breakthroughs** — models, benchmarks, capability milestones

Topics are configurable in `config/topics.yaml`.

---

## Project structure

```
linkedin_post_generator/
├── config/
│   ├── topics.yaml          ← what news to track (edit freely)
│   ├── sources.yaml         ← RSS feeds (add/remove/toggle)
│   └── brand_kit.yaml       ← your voice, tone, post structure
├── src/
│   ├── news_gatherer.py     ← fetches + scores RSS articles
│   ├── trending_tracker.py  ← Google Trends keywords (pytrends)
│   ├── post_generator.py    ← Claude API post generation
│   └── notion_publisher.py  ← Notion API publishing
├── posts/                   ← generated drafts saved here
├── main.py                  ← CLI runner
├── requirements.txt
└── .env.example
```

---

## Claude Code agent pipeline (alternative)

If you run this project inside Claude Code, you can also use the built-in agent pipeline:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code reads `orchestrator.md` and delegates to subagents in `.claude/agents/`:
- `news-gatherer` → fetches RSS via WebFetch
- `trending-tracker` → searches trends via WebSearch
- `post-generator` → writes and saves drafts
- `notion-publisher` → pushes to Notion via MCP

Both approaches (Python script and Claude Code agents) read the same config files and save posts to the same `posts/` folder.
