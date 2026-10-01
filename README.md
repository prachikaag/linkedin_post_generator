# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — in your brand voice, with cited sources, ready to review and publish.

---

## What It Does

1. **Scans** RSS feeds and YouTube channels for fresh AI news (last 48 hours by default)
2. **Scores** articles by relevance to your topic list (AI companies, funding, launches, BigTech)
3. **Finds** what's trending across the web this week
4. **Writes** 2 LinkedIn posts per run in your tone — with sources, hashtags, and a hook that stops the scroll
5. **Saves** drafts to `posts/` as markdown files you can review and edit before posting
6. **Pushes** drafts to Notion (optional) so you can manage them alongside other content

---

## What It Covers

The pipeline is pre-configured to track:

**AI Assistants** — ChatGPT (OpenAI), Claude (Anthropic), Gemini (Google), Perplexity

**Creative AI** — Midjourney, ElevenLabs, Runway, Suno, Stability AI, Pika

**Big Tech AI** — Microsoft Copilot, Google AI, Apple Intelligence, Amazon Bedrock, Nvidia, Salesforce Agentforce, Adobe Firefly

**Funding & Startups** — Series A through IPO, acquisitions, valuations

**YouTube Drops** — Product demos, founder talks, and research walkthroughs from key AI channels

---

## Post Types

Each generated draft is labelled with a post type:

| Post Type | When it fires |
|-----------|---------------|
| **New Feature / Product Launch** | Any major AI product ships something new |
| **YouTube Drop** | Key AI company releases a video |
| **Big Tech AI News** | Microsoft, Google, Apple, Amazon, Nvidia, Salesforce |
| **AI Startup Funding** | Raise, acquisition, IPO, valuation milestone |
| **Human in the Loop Experiment** | Personal experiments with AI tools in real work |
| **AI Trend / Opinion** | Pattern across multiple developments worth synthesising |

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with options:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration

All settings live in `config/` — edit these files directly, changes apply on the next run.

### `config/brand_kit.yaml` — Your voice and brand
- **Author details** — fill in your name, title, tagline (one-time setup)
- **Tone of voice** — writing style rules, dos/don'ts, post structure
- **Post types** — the angles you write about and example hooks for each
- **Companies spotlight** — the AI companies you follow most closely
- **Hashtags** — always-include list and rotation pool

### `config/topics.yaml` — What news to track
- **Companies to track** — AI labs, AI builders, big tech, with per-company keyword lists
- **Topic categories** — funding, product launches, marketing AI, research, regulation, productivity
- **Freshness settings** — how old articles can be, minimum relevance score

### `config/sources.yaml` — Where to fetch news from
- **RSS feeds** — TechCrunch, VentureBeat, The Verge, Wired, MIT Tech Review, Ars Technica
- **Company blogs** — OpenAI, Anthropic, Google AI, DeepMind, Meta AI, Microsoft, HuggingFace, Mistral, Perplexity, ElevenLabs
- **YouTube channels** — Google DeepMind, OpenAI, Anthropic, Two Minute Papers
- **Optional APIs** — NewsAPI (set `NEWSAPI_KEY` in `.env` and enable in sources.yaml)

---

## Output

Posts land in `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5-model.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file has YAML frontmatter (title, date, post type, sources, status) followed by the full post body.

Change `status: draft` → `status: published` to track what's gone live on LinkedIn.

---

## Setup

```bash
cp .env.example .env
# Edit .env and fill in optional keys
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `NOTION_PAGE_ID` | Optional | Push drafts to a Notion page |
| `NOTION_API_KEY` | Optional | Direct Notion REST API access |
| `NEWSAPI_KEY` | Optional | Extra news coverage beyond RSS |

No API key is needed for the core pipeline — it runs entirely through Claude Code.

---

## Architecture

```
orchestrator.md                          ← master pipeline (read this first)
├── .claude/agents/news-gatherer.md      ← fetches + scores RSS & YouTube articles
├── .claude/agents/trending-tracker.md  ← finds trending AI keyword phrases this week
├── .claude/agents/post-generator.md    ← writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md  ← pushes drafts to Notion (optional)

config/
├── brand_kit.yaml    ← your voice, tone, post types, hashtags
├── topics.yaml       ← companies, keywords, freshness settings
└── sources.yaml      ← RSS feeds, YouTube channels, API sources

posts/                ← generated drafts land here
```
