# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## What It Does

1. **Monitors AI news** — reads 20+ RSS feeds from TechCrunch, The Verge, VentureBeat, company blogs (OpenAI, Anthropic, Google DeepMind, Mistral, ElevenLabs, etc.), and YouTube channels
2. **Tracks trending topics** — searches the web for the AI stories generating the most buzz in the last 7 days
3. **Classifies stories** — matches each article cluster to a post type (product launch, funding round, personal experiment, YouTube demo, big tech move, research paper, policy news)
4. **Writes branded posts** — applies your tone of voice, writing style rules, and brand guidelines to generate LinkedIn drafts with cited sources
5. **Saves as markdown drafts** — each post lands in `posts/` ready for you to review, edit, and publish
6. **Publishes to Notion** — optionally pushes drafts to a Notion page as toggle blocks

---

## Architecture

The pipeline is a **multi-agent system** — an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file. The orchestrator passes data between them.

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with custom parameters:

```
Run the pipeline. Generate 3 posts.
```

```
Run the pipeline. Generate 1 post about AI startup funding — force post type startup_funding.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Run the pipeline. Generate 1 post about my personal experiment with [tool].
```

---

## Configuration Files

All settings live in `config/`. **Edit these files to customise everything** — changes take effect on the next run.

| File | What it controls |
|------|-----------------|
| `config/brand_kit.yaml` | Your name, title, tone of voice, writing style, post structure, hashtag strategy |
| `config/topics.yaml` | Companies and keywords to track, trending keyword seeds, freshness settings |
| `config/sources.yaml` | RSS feeds and APIs to fetch from (enable/disable per source) |
| `config/post_types.yaml` | Post type definitions — triggers, angles, hook starters, CTA style |
| `config/prompts.yaml` | System-level prompt templates and hard constraints injected into every generation |

### Quick Personalisation Checklist

1. **`config/brand_kit.yaml`** → update `author.name` and `author.title` with your real details
2. **`config/brand_kit.yaml`** → review `tone_of_voice.writing_style` and adjust any rules that don't match your voice
3. **`config/post_types.yaml`** → enable/disable post types, edit `hook_starters` to sound more like you
4. **`config/prompts.yaml`** → edit `voice_examples` with actual sentences you've written
5. **`config/topics.yaml`** → add any companies or keywords you want tracked

---

## Post Types

The pipeline auto-detects which type of post to write based on the article cluster. You can also force a specific type.

| Type ID | What it writes about |
|---------|---------------------|
| `product_launch` | New model releases, feature updates, product announcements |
| `youtube_release` | YouTube demos, keynotes, on-stage reveals |
| `startup_funding` | Funding rounds, acquisitions, IPOs, valuations |
| `bigtech_news` | Microsoft, Google, Apple, Amazon, Meta, Nvidia, Salesforce AI moves |
| `human_in_the_loop` | Personal experiments — what you tested, what happened, what you learned |
| `research_breakthrough` | Research papers, benchmarks, capability milestones |
| `ai_regulation` | Policy, regulation, governance, legal developments |

Force a type by telling the pipeline:
```
Run the pipeline. Force post type: human_in_the_loop.
```

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: post type, source metadata, companies matched, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Notion Integration (Optional)

To push drafts to a Notion page:

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → create a new Internal integration
2. Copy the integration token → add as `NOTION_API_KEY` in `.env`
3. Open your LinkedIn Post Ideas Notion page → connect the integration
4. Copy the 32-char page ID from the URL → add as `NOTION_PAGE_ID` in `.env`

Each generated post is appended as a collapsible toggle block with a date heading and draft callout.

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `NOTION_PAGE_ID` | Optional | Enables Notion publishing |
| `NOTION_API_KEY` | Optional | Fallback Notion REST API key |
| `NEWSAPI_KEY` | Optional | Broader news coverage via NewsAPI |

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

---

## Agents Reference

### `news-gatherer`
Reads `config/sources.yaml` + `config/topics.yaml`. Fetches all enabled RSS feeds via WebFetch. Scores articles by keyword relevance (+3 per company keyword match, +1 per category keyword match). Deduplicates and returns the top scored articles as a JSON array.

### `trending-tracker`
Reads seed terms from `config/topics.yaml`. Uses WebSearch to find the most-discussed AI topics from the last 7 days. Returns 15–20 keyword phrases as a JSON array.

### `post-generator`
Reads `config/brand_kit.yaml`, `config/post_types.yaml`, and `config/prompts.yaml`. Auto-detects post type from article triggers. Synthesises the article cluster into a branded LinkedIn post. Validates all URLs against input data. Saves as a `.md` draft with YAML frontmatter.

### `notion-publisher`
Reads the Notion page ID from `.env`. Appends the post as a toggle block on the configured Notion page using the Notion MCP connector.
