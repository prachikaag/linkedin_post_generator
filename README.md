# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks trending keywords, and writes
research-backed LinkedIn post drafts — in your voice, with cited sources.

Built entirely as Claude agent workflows. No Python required to run.

---

## What it does

1. **Monitors AI news** — reads 20+ RSS feeds (TechCrunch, The Verge, company blogs,
   YouTube channels, funding news) and scores articles by relevance to your topics.

2. **Tracks trending keywords** — searches the web for what's buzzing in AI right now,
   so posts feel timely and discoverable.

3. **Writes in your voice** — reads your brand kit, tone guide, and personal experiments
   log, then generates posts that sound like you — opinionated, cited, brand-aware.

4. **Saves drafts** — each post is a markdown file with full YAML frontmatter tracking
   sources, companies, categories, and publication status.

5. **Publishes to Notion** — optionally pushes each draft to a Notion page as a
   collapsible toggle block for review and editing before publishing.

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude reads `orchestrator.md` and runs the full pipeline end-to-end.

### Options

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Run the pipeline. Use 5 articles per cluster.
```

---

## Configuration Files

All settings live in `config/`. Edit these directly — changes take effect on the next run.

### `config/topics.yaml` — What to track
The master list of AI companies, keywords, and topic categories the news gatherer
uses to score articles. Add new companies or keywords here whenever your interests shift.

```yaml
companies_to_track:
  ai_labs:
    - name: "OpenAI"
      keywords: ["OpenAI", "ChatGPT", "GPT-5", ...]
```

### `config/tone_of_voice.md` — How you write
Your complete personal style guide. The post generator reads this in full before writing
anything. Edit freely — this is the single most powerful way to shape your posts.

Covers: voice traits, writing rules, banned words, post structure, example rhythms.

### `config/brand_kit.yaml` — Your brand settings
Author info, hashtag strategy, post length limits, citation standards, and dos/don'ts.
**Fill in `author.name`, `author.title`, and `author.tagline`** before your first run.

### `config/personal_experiments.md` — Your AI experiments log
The "human in the loop" file. Add entries here as you test AI tools.
When the pipeline finds news about a tool you've experimented with, it references
your personal experience directly — adding authentic first-person content that
sets your posts apart from AI-generated summaries.

Template included. Just copy, fill in, and append.

### `config/sources.yaml` — Where to fetch news
All RSS feeds, company blogs, YouTube channels, and optional API sources.
Add new feeds here. Set `enabled: false` to pause a source without deleting it.

---

## Setup

### 1. Fill in your author details

Edit `config/brand_kit.yaml`:

```yaml
author:
  name: "Your Name"          # e.g. "Prachi Jain"
  title: "Your Title"        # e.g. "Brand Strategist & AI Practitioner"
  tagline: "Your tagline"
  location: "City, Country"
```

### 2. Personalise your tone (optional but powerful)

Edit `config/tone_of_voice.md` to match your actual writing voice.
The more specific you make it, the more the posts will sound like you.

### 3. Log your experiments (optional)

Edit `config/personal_experiments.md` and add tools you've tested.
The pipeline uses this to add real first-person observations to relevant posts.

### 4. Set up Notion (optional)

Copy `.env.example` to `.env` and fill in:

```bash
NOTION_API_KEY=secret_xxx          # from notion.so/my-integrations
NOTION_PAGE_ID=your_32char_id      # from your Notion page URL
```

Then connect your Notion integration to the target page.

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2026-05-14_22-55-00_enterprise-ai-market-shift-real-data.md
  2026-05-14_23-10-00_vertical-ai-depth-over-horizontal.md
```

Each file has YAML frontmatter:

```yaml
---
title: "Article headline"
date: "2026-05-14"
primary_source_url: "https://..."
all_sources:
  - title: "..."
    url: "..."
    publication: "..."
source_count: 6
matched_companies: [OpenAI, Anthropic]
matched_categories: [New AI Feature or Product Launch]
status: "draft"
---
```

Change `status: draft` → `status: published` to track what's gone live.

---

## Pipeline Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and
input/output contract. The orchestrator passes data between them.

### `news-gatherer`
- Reads `config/sources.yaml`, `config/topics.yaml`
- Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates
- Returns top articles as a scored JSON array

### `trending-tracker`
- Reads `config/topics.yaml` for seed terms
- Searches the web for what's buzzing in AI in the last 7 days
- Returns 15–20 trending keyword phrases as JSON

### `post-generator`
- Reads `config/brand_kit.yaml`, `config/tone_of_voice.md`, `config/personal_experiments.md`
- Synthesises a cluster of articles into a branded LinkedIn post
- Validates URLs (only uses URLs from source articles — never constructs them)
- Saves as a `.md` draft with full YAML frontmatter

### `notion-publisher`
- Reads `NOTION_PAGE_ID` from `.env`
- Appends the post as a collapsible toggle block on your Notion page

---

## Post Topics Covered

The pipeline monitors and writes about:

- **AI model launches** — ChatGPT, Claude, Gemini, Perplexity, Grok, Mistral, Llama, etc.
- **New AI features** — anything a major AI platform ships or announces
- **AI startup funding** — Series A/B/C rounds, IPOs, acquisitions, valuations
- **Big tech AI moves** — Microsoft Copilot, Apple Intelligence, Amazon Bedrock, etc.
- **AI for brands and marketing** — tools and strategies for marketing teams
- **AI research breakthroughs** — benchmarks, capabilities, research papers
- **AI tools and productivity** — agents, workflows, coding tools, automation
- **YouTube drops** — new videos from OpenAI, Anthropic, Google DeepMind, Two Minute Papers
- **Human-in-the-loop workflows** — how practitioners are actually using AI day-to-day

---

## Adding New Companies or Topics

Edit `config/topics.yaml`:

```yaml
companies_to_track:
  ai_labs:
    - name: "New Company"
      keywords:
        - "New Company"
        - "their product name"
        - "their CEO name"
```

Higher-priority keywords (company names) score `+3` per match.
Topic category keywords (launch, funding, etc.) score `+1` per match.

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
