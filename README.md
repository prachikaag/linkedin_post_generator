# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks trending keywords, and writes research-backed LinkedIn posts in your voice — entirely through Claude agents. No code to run; just edit config files and say "run the pipeline."

---

## What It Does

1. **Watches the AI landscape** — reads RSS feeds from TechCrunch, The Verge, VentureBeat, AI company blogs, YouTube channels, and more
2. **Tracks what's trending** — searches the web for the most-discussed AI topics of the past 7 days
3. **Writes posts in your voice** — uses your brand kit and tone of voice to write posts with cited sources
4. **Picks the right format** — automatically selects from 5 post types based on the news
5. **Saves drafts locally** — every post saved to `posts/` as a markdown file, ready to review
6. **Optionally publishes to Notion** — pushes drafts to your Notion review page

---

## Components (All Separately Editable)

```
linkedin_post_generator/
│
├── orchestrator.md                    ← Pipeline orchestrator (edit to change flow)
│
├── config/
│   ├── topics.yaml                    ← Companies and keywords to monitor
│   ├── sources.yaml                   ← RSS feeds, YouTube channels, APIs
│   ├── brand_kit.yaml                 ← Your voice, tone, writing rules
│   ├── content_types.yaml             ← 5 post formats with hooks and angles
│   └── experiments.yaml              ← Your personal AI experiment notes
│
├── .claude/agents/
│   ├── news-gatherer.md              ← Fetches + scores articles from feeds
│   ├── trending-tracker.md           ← Finds trending AI keywords via web search
│   ├── post-generator.md             ← Writes and saves LinkedIn drafts
│   └── notion-publisher.md           ← Publishes drafts to Notion (optional)
│
├── posts/                             ← Generated drafts live here
│
└── .env.example                       ← Environment variables template
```

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with options:

```
Run the pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

Claude Code reads `orchestrator.md` and runs the full pipeline using subagents.

---

## Customising Each Component

### `config/topics.yaml` — What to Monitor

Add or remove companies, keywords, and topic categories.

```yaml
companies_to_track:
  ai_labs:
    - name: "New Company"
      keywords:
        - "their product name"
        - "their company name"
```

Change `freshness.max_article_age_hours` to widen or narrow the time window.

---

### `config/sources.yaml` — Where to Get News

Add any RSS feed:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

Set `enabled: false` to pause a feed without deleting it.

---

### `config/brand_kit.yaml` — Your Voice

**Start here.** Fill in your name, title, and tagline. Then review:

- `tone_of_voice.primary_traits` — how you come across
- `tone_of_voice.writing_style` — rules applied to every post
- `tone_of_voice.post_structure` — the ordered sections of each post
- `brand.hashtags` — your always-on and rotation hashtags
- `brand.post_length` — short / medium / long

This file is read on every run — no restarts needed.

---

### `config/content_types.yaml` — Post Formats

Five post types, each with its own hook templates, angle, and structure:

| Type | When it's used | Example hook |
|------|---------------|--------------|
| `feature_launch` | AI company ships something new | "X just launched Y. Here's what brands need to know." |
| `startup_funding` | Investment rounds, acquisitions, IPOs | "X raised $Y. Here's the quiet signal nobody's talking about." |
| `bigtech_ai` | Microsoft, Google, Apple, Meta, Nvidia move | "When X does this, marketing teams should pay attention." |
| `personal_experiment` | Your own "I tried X" posts | "I spent 45 minutes using X for Y. Here's what nobody tells you." |
| `trend_synthesis` | Connecting multiple stories into a pattern | "Three things happened in AI this week that change the picture." |

Edit the `hook_templates` and `structure_notes` for each type to match your writing style.

---

### `config/experiments.yaml` — Your Personal AI Experiments

This is the source material for `personal_experiment` posts — the "human in the loop" content.

**To add an experiment:**

1. Copy the template entry
2. Fill in `tool`, `use_case`, `what_i_tried`, `what_worked`, `what_fell_short`, `takeaway_for_brands`
3. Set `status: "ready"` when you want it turned into a post

The post-generator automatically draws on `status: "ready"` experiments when writing personal experiment posts.

**An `experiments.yaml` entry:**

```yaml
- id: "exp-003"
  status: "ready"
  date: "2024-01-20"
  tool: "Perplexity"
  use_case: "Competitive brand research"
  time_spent: "1 hour"
  setup: "Tried using Perplexity to replace a desk research brief for a brand audit."
  what_i_tried: "Asked it to summarise a competitor's positioning from their website, LinkedIn, and press coverage."
  what_worked: "Excellent at pulling together public signals quickly. First pass was better than expected."
  what_fell_short: "Couldn't access paywalled content. Missed things behind a login."
  takeaway_for_brands: "Use it for quick-turn public research. Not for deep competitive intelligence."
  post_angle: "Where AI research tools hit their ceiling in brand strategy"
```

---

### `posts/` — Generated Drafts

Every run saves posts here as `.md` files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file has:
- **YAML frontmatter**: source metadata, content type, companies, categories, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Setup

1. **Set your brand details**: Edit `config/brand_kit.yaml` — fill in your name, title, and tagline
2. **Copy the env file**: `cp .env.example .env`
3. **Add Notion (optional)**: Set `NOTION_PAGE_ID` in `.env` and connect the Notion integration
4. **Run**: Open in Claude Code and say "Run the LinkedIn Post Generator pipeline"

### Environment Variables (`.env`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `NOTION_PAGE_ID` | Optional | Pushes post drafts to your Notion page |
| `NOTION_API_KEY` | Optional | Direct Notion API fallback |
| `NEWSAPI_KEY` | Optional | Additional news sources via NewsAPI.org |

---

## Post Types Reference

### Feature Launch
> For: OpenAI, Anthropic, Gemini, ElevenLabs, Midjourney, Perplexity, Runway, etc. launching new features or models.
> Angle: What changed, and what a brand team can do with it this week.

### Startup Funding
> For: AI funding rounds, acquisitions, IPOs.
> Angle: What the money bet signals about where the market is going.

### Big Tech AI
> For: Microsoft, Google, Apple, Amazon, Meta, Nvidia, Salesforce, Adobe.
> Angle: How Big Tech AI moves affect brands who live on those platforms.

### Personal Experiment (Human in the Loop)
> For: Your own tests of AI tools — what you tried, what worked, what didn't.
> Angle: Authentic "I ran the experiment so you don't have to" reporting.

### Trend Synthesis
> For: Multiple stories that form a pattern.
> Angle: Pattern recognition across the AI landscape — what it all means.

---

## Agents Reference

### `news-gatherer`
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON

### `trending-tracker`
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days, returns 15–20 keyword phrases

### `post-generator`
- **Reads**: `config/brand_kit.yaml`, `config/content_types.yaml`, `config/experiments.yaml`
- **Does**: Selects content type, synthesises articles into a branded LinkedIn post, saves as `.md` draft

### `notion-publisher`
- **Does**: Appends the post as a toggle block on a Notion page
