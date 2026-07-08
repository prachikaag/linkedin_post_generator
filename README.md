# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, identifies the best content angle, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents, with no traditional code required.

---

## What It Does

1. **Reads** your topics of interest (`config/topics.yaml`) — AI companies, keywords, categories
2. **Fetches** fresh news from 15+ RSS feeds — AI labs, company blogs, startup funding, YouTube channels
3. **Tracks** trending keywords from across the web for the past 7 days
4. **Selects** the best content angle for each story — launch, funding, big tech move, personal experiment, trend
5. **Writes** a branded LinkedIn post with cited sources, following your exact tone and voice
6. **Saves** drafts to `posts/` as editable markdown files
7. **Publishes** drafts to Notion (optional) so you can review and copy-paste to LinkedIn

---

## Quick Start

### 1. Set up your personal details (required)

Edit `config/brand_kit.yaml` and fill in the `author` section:

```yaml
author:
  name: "Your Name"
  title: "Your Professional Title"
  tagline: "Your LinkedIn tagline"
  location: "Your City, Country"
```

### 2. Add your Notion page (optional but recommended)

Copy `.env.example` to `.env` and add your Notion page ID:

```bash
cp .env.example .env
# Then edit .env and set NOTION_PAGE_ID=your_32char_page_id
```

See `.env.example` for full setup instructions.

### 3. Log your AI experiments (optional but powerful)

Edit `config/personal_experiments.yaml` — add the AI tools you've actually used. When a news story relates to a tool you've tested, the pipeline writes a "human-in-the-loop" post from your own experience. That's your most credible content type.

Set `status: "ready_to_post"` when you want an experiment to be available for post generation.

### 4. Run the pipeline

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

---

## All Components

Every component is a separate file you can edit and tweak. Nothing is buried in code.

### Configuration (edit to customise)

| File | What it controls | When to edit |
|------|-----------------|--------------|
| `config/brand_kit.yaml` | Your name, tone, writing rules, post structure, hashtags | Before first run, and whenever your voice evolves |
| `config/topics.yaml` | Companies to track, topic categories, trending keyword seeds, freshness settings | To add new AI companies or remove topics you don't care about |
| `config/sources.yaml` | RSS feeds, YouTube channels, optional API sources | To add new sources or disable feeds that are too noisy |
| `config/personal_experiments.yaml` | Your personal AI tool experiments | Every time you try a new AI tool — this drives your "I tried X" posts |
| `templates/content-angles.yaml` | The 6 post framing types: hooks, prompts, triggers | To change how each story type is framed, or add new angles |

### Agents (the AI workers — read to understand, edit carefully)

| Agent | What it does |
|-------|-------------|
| `.claude/agents/news-gatherer.md` | Fetches and scores all RSS articles |
| `.claude/agents/trending-tracker.md` | Finds trending AI keywords from the web |
| `.claude/agents/content-angle-selector.md` | Picks the right content angle for each story |
| `.claude/agents/post-generator.md` | Writes the LinkedIn post following your brand kit |
| `.claude/agents/notion-publisher.md` | Publishes drafts to Notion |

### Orchestrator

| File | What it does |
|------|-------------|
| `orchestrator.md` | Runs the full pipeline — wires all agents together in sequence |

---

## Content Angles

The pipeline recognises 6 distinct post types and writes each differently:

| Angle | When it fires | Hook style |
|-------|--------------|------------|
| **Product Launch** | New model, feature, or product released | "X just changed how brands will Y" |
| **Funding News** | Investment round, acquisition, IPO | "The money flowing into X tells us something important" |
| **Big Tech Move** | Microsoft, Google, Apple, Amazon, Nvidia | "When X commits to Y, the rest of the market follows" |
| **Personal Experiment** | You've personally tested the related tool | "I tried X for Y — here's the honest version" |
| **Research Explainer** | Research paper or benchmark result | "A paper just changed what we thought AI could do" |
| **Industry Trend** | 3+ articles point to the same shift | "Three things happened this week. They all point the same way." |

**Personal Experiment posts are the most powerful** — they're triggered when a `ready_to_post` entry in `personal_experiments.yaml` matches the news story. Add your experiments there.

Edit `templates/content-angles.yaml` to change the hooks, prompts, and triggers for any angle.

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-07-08_10-30-00_openai-launches-gpt5-model.md
  2026-07-08_10-30-00_perplexity-raises-series-b.md
```

Each file contains:
- **YAML frontmatter**: source metadata, content angle, companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## What Gets Tracked

### AI Companies
OpenAI / ChatGPT, Anthropic / Claude, Google DeepMind / Gemini, Perplexity, ElevenLabs, Midjourney, Stability AI, xAI / Grok, Meta AI / LLaMA, Mistral, Runway, Pika Labs, Cohere, Character AI, Hugging Face, and more.

### Big Tech
Microsoft / Copilot, Google, Apple Intelligence, Amazon / Bedrock, Nvidia, Salesforce / Agentforce, Adobe Firefly.

### AI Builders and Startups
Cerebras, Groq, Harvey AI, Cognition / Devin, Scale AI, Writer, Glean, Cursor, Suno, Synthesia, and more.

### Topic Categories
- New AI Feature or Product Launch
- AI Startup Funding
- AI for Marketing and Brands
- AI Research and Breakthroughs
- AI Regulation and Policy
- AI Tools and Productivity

### News Sources (RSS)
TechCrunch, The Verge, VentureBeat, Wired, MIT Technology Review, Ars Technica, CNBC Tech, OpenAI Blog, Anthropic Blog, Google AI Blog, DeepMind Blog, Meta AI Blog, Microsoft AI Blog, Hugging Face Blog, Mistral Blog, Perplexity Blog, ElevenLabs Blog, TechCrunch Startups, Crunchbase News, SiliconAngle, plus YouTube channels for Google DeepMind, OpenAI, Anthropic, and Two Minute Papers.

---

## Customising

### Add a new AI company to track

Edit `config/topics.yaml` under `companies_to_track`:

```yaml
- name: "New Company"
  keywords:
    - "Company Name"
    - "Their Product"
```

### Add a new RSS feed

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

### Change how a post type is framed

Edit `templates/content-angles.yaml` — find the angle you want to change and update `hook_starters`, `your_take_prompt`, or `so_what_prompt`.

### Add a personal experiment

Edit `config/personal_experiments.yaml` — copy the template block and fill in:
- `tool` — the exact tool name
- `use_case` — what you used it for (be specific)
- `what_worked` / `what_flopped` — honest observations
- `honest_verdict` — one sentence, would you recommend it?
- `status: "ready_to_post"` — when it's ready to trigger post generation

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NOTION_PAGE_ID` | No | 32-char Notion page ID. Posts are published here as toggle blocks. |
| `NOTION_API_KEY` | No | Notion integration token (only needed for direct API fallback). |
| `ANTHROPIC_API_KEY` | No | Not needed inside Claude Code — uses OAuth automatically. |
| `NEWSAPI_KEY` | No | Expands sources beyond RSS. Free key at newsapi.org. |
