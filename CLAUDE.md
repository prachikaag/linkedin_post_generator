# LinkedIn Post Generator

A multi-agent pipeline that fetches trending AI news, tracks what's buzzing across the web, and generates research-backed LinkedIn draft posts — all inside Claude Code with no code to run.

---

## How to Run

When the user asks to run the pipeline (any phrasing like "generate posts", "run the pipeline", "make LinkedIn posts"), read `orchestrator.md` and follow its instructions exactly. It defines the full pipeline.

**Common invocations:**

- "Run the LinkedIn Post Generator pipeline." → default: 2 posts, 6 articles/cluster
- "Run the pipeline and generate 3 posts." → MAX_POSTS=3
- "Run the pipeline in dry-run mode." → DRY_RUN=true (fetch + rank news only, no post generation)
- "Run with 8 articles per cluster." → SOURCE_POOL_SIZE=8

---

## Architecture

```
orchestrator.md                              ← top-level pipeline (read this to execute)
├── .claude/agents/news-gatherer.md         ← fetches + scores RSS articles via WebFetch
├── .claude/agents/trending-tracker.md      ← finds trending keyword phrases via WebSearch
├── .claude/agents/post-generator.md        ← writes branded LinkedIn drafts + saves to posts/
└── .claude/agents/notion-publisher.md      ← publishes drafts to Notion (optional)
```

Each agent is self-contained with its own tools, role, and input/output contract.
The orchestrator passes structured JSON between them.

---

## Configuration (all editable files)

| File | Purpose | Edit when... |
|------|---------|--------------|
| `config/brand_kit.yaml` | Author voice, tone, writing rules, hashtags | Updating your name/title or how posts sound |
| `config/topics.yaml` | Companies + keywords to track, freshness settings | Adding/removing companies or topics |
| `config/sources.yaml` | RSS feeds and optional NewsAPI queries | Adding new news sources |
| `.env` | API keys (Notion, NewsAPI) | Configuring integrations |

---

## First-Time Setup

Before the first run, the user must fill in their personal details in `config/brand_kit.yaml`:

```yaml
author:
  name: "Your Real Name"           # ← REQUIRED: fill this in
  title: "Your Professional Title" # ← REQUIRED: fill this in
  location: "Your City, Country"   # ← fill this in
```

The `config/brand_kit.yaml` also controls tone of voice, writing style, post structure, and hashtag strategy — all of which are used by the post-generator agent on every run.

---

## Output

Posts are saved to `posts/` as Markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file has:
- **YAML frontmatter**: all source metadata, matched companies, trending keywords, status
- **Post body**: the full LinkedIn draft ready to review

Change `status: draft` → `status: published` to track what's gone live.

If `NOTION_PAGE_ID` is set in `.env`, posts are also pushed to Notion as collapsible toggle blocks.

---

## Topic Coverage

The pipeline automatically covers:
- **AI model launches & features**: OpenAI, Anthropic, Google, Perplexity, ElevenLabs, Midjourney, Runway, xAI, Meta, Mistral, and more
- **Big tech AI moves**: Microsoft, Apple, Amazon, Nvidia, Salesforce, Adobe
- **AI startup funding rounds**: Series A/B/C, IPOs, acquisitions
- **AI research breakthroughs**: papers, benchmarks, capability milestones
- **AI for marketing & brands**: how brands use AI in creative and strategy
- **YouTube video releases** from key AI company channels

Edit `config/topics.yaml` to add companies or adjust scoring weights.
Edit `config/sources.yaml` to add RSS feeds or enable NewsAPI.
