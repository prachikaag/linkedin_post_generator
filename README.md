# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks what's trending, and writes research-backed LinkedIn posts in your voice — entirely through Claude agents. No code to run, no API keys required to start.

---

## What It Does

1. **Reads your topics file** (`config/topics.yaml`) — a curated list of AI companies, products, and categories you follow
2. **Fetches fresh news** from 20+ RSS feeds: TechCrunch, The Verge, VentureBeat, company blogs (OpenAI, Anthropic, Google, Meta, etc.), startup news, and YouTube channel updates
3. **Tracks trending keywords** from across the web over the past 7 days
4. **Detects the post type** — YouTube demo launch, product feature, startup funding, big tech news, or human-in-the-loop experiment
5. **Writes branded LinkedIn posts** following your tone, structure, and style from `config/brand_kit.yaml`
6. **Saves drafts to `posts/`** as markdown files with source metadata, ready to review before publishing
7. **Optionally pushes to Notion** if you have `NOTION_PAGE_ID` configured

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md                          ← main pipeline controller
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file you can read and edit. The orchestrator passes data between them. No Python, no dependencies.

---

## How to Run

### Option 1 — Claude Code (interactive, recommended)

Open this project in Claude Code and type:

```
Run the LinkedIn Post Generator pipeline.
```

With custom parameters:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 8 articles per cluster.
```

Dry-run (fetch and rank news only, no post generation):

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

### Option 2 — Shell script (from terminal)

```bash
./run.sh                        # 2 posts, default settings
./run.sh --posts 3              # 3 posts
./run.sh --posts 1 --dry-run    # fetch news only, no post generation
./run.sh --posts 5 --cluster 8  # 5 posts, 8 articles per cluster
```

Requires the `claude` CLI to be installed: https://claude.ai/code

---

## Configuration — Edit These Files

All settings live in `config/`. Edit them directly — changes take effect on the next run.

| File | What to edit |
|------|-------------|
| `config/topics.yaml` | Companies and keywords to track, freshness settings |
| `config/brand_kit.yaml` | Your name, tone of voice, writing style, hashtag strategy |
| `config/sources.yaml` | RSS feeds to monitor, YouTube channels, NewsAPI queries |

### Quick-start: Personalise your brand kit

Open `config/brand_kit.yaml` and update:

```yaml
author:
  name: "Your Full Name"
  title: "Your Job Title"
  tagline: "What you help people do"
  location: "Your City, Country"
```

Everything else (tone, structure, hashtags) is pre-configured and ready to go — tweak as needed.

### Environment Variables (optional)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in any of these:

```bash
# Notion publishing — push drafts to a Notion page
NOTION_PAGE_ID=your_32char_page_id_here  # from the page URL
NOTION_API_KEY=secret_xxx                # only needed for REST API fallback

# Broader news coverage (free key at newsapi.org)
NEWSAPI_KEY=your_key_here
```

All fields are optional. The pipeline runs without them.

---

## Content Types

The post-generator detects the type of news and adjusts the post angle:

| Type | Trigger | Post angle |
|------|---------|-----------|
| `youtube_launch` | Company posts a YouTube demo or product video | What does the demo reveal that the press release doesn't? |
| `product_feature_launch` | New AI model, feature, or product announced | What's the actual change for marketers? What to test first? |
| `startup_funding` | AI startup raises funding or gets acquired | What does the investment thesis say about where the market is going? |
| `bigtech_ai_news` | Major announcement from Google, Microsoft, Apple, Meta, Nvidia, Amazon | What should brand and marketing teams do with this? |
| `human_in_the_loop` | AI workflow experiment with honest results | What worked, what you fixed yourself, what you'd do differently |

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: title, date, content_type, sources, companies, categories, status
- **Post body**: the full LinkedIn draft, ready to review and copy-paste

Change `status: draft` → `status: published` to track what's gone live.

---

## Agents Reference

### `news-gatherer` — `.claude/agents/news-gatherer.md`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON

### `trending-tracker` — `.claude/agents/trending-tracker.md`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Runs 4–5 targeted web searches (launches, funding, YouTube demos, big tech, AI for brands) and returns 15–20 trending keyword phrases

### `post-generator` — `.claude/agents/post-generator.md`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`
- **Does**: Detects content type, synthesises articles, writes a branded post, validates all URLs, saves as `.md` draft

### `notion-publisher` — `.claude/agents/notion-publisher.md`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block to your Notion page

---

## Customising

### Add a new company to track

Edit `config/topics.yaml` under the right category:

```yaml
companies_to_track:
  ai_builders:
    - name: "Kling AI"
      keywords:
        - "Kling"
        - "Kling AI"
        - "Kling video"
```

### Add an RSS feed

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My New Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

### Change your tone

Edit `config/brand_kit.yaml` → `tone_of_voice.writing_style`. Every rule is applied on every run.

### Add a content angle

Edit `config/brand_kit.yaml` → `brand.content_angles`. New angles are included in the post-generator's context automatically.
