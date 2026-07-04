# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, selects the right post template for the story type, and writes research-backed LinkedIn drafts in your exact voice — entirely through Claude agents. No code to run.

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code reads `orchestrator.md` and runs the full pipeline:

1. **news-gatherer** → fetches RSS feeds, scores articles by relevance, returns top articles
2. **trending-tracker** → searches the web for trending AI keywords this week
3. **post-generator** → selects the right post template, writes and saves a branded draft
4. **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set in `.env`)

### Custom runs

```
Run the LinkedIn Post Generator. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md       → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md    → finds trending keyword phrases
├── .claude/agents/post-generator.md      → picks template, writes + saves post draft
└── .claude/agents/notion-publisher.md    → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file. The orchestrator passes data between them.

---

## Configuration Files

All settings live in `config/`. Edit any file — changes take effect on the next run.

| File | What it controls | Edit frequency |
|------|-----------------|----------------|
| `config/author_profile.yaml` | **WHO** you are — name, title, brand angle, content pillars | Once |
| `config/brand_kit.yaml` | **HOW** you write — tone, voice rules, post structure, hashtags | Occasionally |
| `config/post_templates.yaml` | **WHAT KIND** of post — 6 templates for different story types | Occasionally |
| `config/topics.yaml` | **WHAT** companies and topics to track | As needed |
| `config/sources.yaml` | **WHERE** news comes from — RSS feeds and APIs | As needed |

---

## Component Guide

### `config/author_profile.yaml` — Who You Are

Fill this in once. It drives post attribution and the lens every post is written through.

```yaml
name: "Prachi"
full_name: "Prachi Jain"
title: "Brand Strategist & AI Enthusiast"
tagline: "Helping brands understand and leverage AI in the real world"
brand_angle: >
  You write as a brand strategist who experiments with AI tools personally...
```

### `config/brand_kit.yaml` — How You Write

Controls your tone of voice, writing style rules, post structure blueprint, dos/don'ts, and hashtag strategy.

Key sections:
- `tone_of_voice.primary_traits` — how you come across
- `tone_of_voice.writing_style` — rules for every post (paragraph length, hook style, etc.)
- `tone_of_voice.post_structure` — the ordered blueprint: HOOK → CONTEXT → EVIDENCE → YOUR TAKE → SO WHAT → CTA → SOURCES → HASHTAGS
- `brand.hashtags` — always-include tags + rotation pool
- `research_standards` — minimum sources, quote format

### `config/post_templates.yaml` — What Kind of Post

Six templates, each designed for a specific story type. The post-generator auto-selects the best match based on article categories and companies.

| Template key | When it fires | Angle |
|---|---|---|
| `product_launch` | New feature/model/product | What can brands actually do now? |
| `funding_news` | Funding round, acquisition, IPO | Decode the investor signal |
| `ai_experiment` | Personal AI tool experiment | Honest results, human-in-the-loop |
| `big_tech_news` | Microsoft, Google, Apple, Meta, etc. | Strategic pattern behind the move |
| `research_breakthrough` | Research paper, benchmark result | Translate technical → practical |
| `ai_regulation` | Policy, law, governance | What brands actually need to do |

Each template sets the hook style, strategic angle, opinion focus, and CTA options for that story type.

### `config/topics.yaml` — What to Track

Controls which AI companies, products, and topic categories trigger article collection.

```yaml
companies_to_track:
  ai_labs:
    - name: "OpenAI"
      keywords: ["ChatGPT", "GPT-4", "GPT-5", "o3", "Sora"]
    - name: "Anthropic"
      keywords: ["Claude", "MCP", "claude sonnet"]
  # ... ElevenLabs, Midjourney, Perplexity, etc.

topic_categories:
  - name: "AI Startup Funding"
    keywords: ["funding", "raises", "Series A", "acquisition"]
  # ... product launches, big tech, research, regulation
```

### `config/sources.yaml` — Where News Comes From

RSS feeds from major AI news sources, company blogs, and YouTube channels. All feeds have `enabled: true/false` and `priority: high/medium/low`.

Pre-configured sources include TechCrunch, The Verge, VentureBeat, MIT Tech Review, Wired, OpenAI Blog, Anthropic Blog, Google AI Blog, DeepMind Blog, Crunchbase News, and more.

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-07-04_10-30-00_openai-launches-gpt5-model.md
  2026-07-04_10-30-00_anthropic-series-e-funding.md
```

Each file contains:
- **YAML frontmatter**: title, date, template used, sources, companies, categories, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Update `status: draft` → `status: published` to track what's gone live.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

| Variable | Purpose | Required |
|---|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key | Only for standalone use (not needed in Claude Code) |
| `NOTION_PAGE_ID` | Notion page where drafts are published | Optional |
| `NOTION_API_KEY` | Notion integration token | Only if using direct API fallback |
| `NEWSAPI_KEY` | NewsAPI key for broader coverage | Optional |

---

## Customising Your Setup

### Add a new RSS source

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

### Track a new AI company

Edit `config/topics.yaml` under `companies_to_track`:

```yaml
ai_builders:
  - name: "New Company"
    keywords:
      - "New Company"
      - "their product name"
```

### Change your writing style

Edit `config/brand_kit.yaml` → `tone_of_voice.writing_style`.

Each item in the list is a rule injected directly into the post-generator prompt.

### Add a new post template

Edit `config/post_templates.yaml` — copy any existing template block, give it a new key, and add its `trigger_categories` and `trigger_keywords`.

---

## First-Time Setup Checklist

- [ ] Edit `config/author_profile.yaml` — add your real name, title, LinkedIn URL
- [ ] Edit `config/brand_kit.yaml` → `author` section — confirm your name and tagline
- [ ] Review `config/brand_kit.yaml` → `tone_of_voice` — adjust any rules that don't match your voice
- [ ] Review `config/topics.yaml` — add/remove companies you care about
- [ ] Copy `.env.example` to `.env` — add `NOTION_PAGE_ID` if you use Notion
- [ ] Run the pipeline: tell Claude Code "Run the LinkedIn Post Generator pipeline"
- [ ] Review drafts in `posts/` — edit before publishing
