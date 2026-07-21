# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and input/output contract. The orchestrator passes data between them — no Python glue code required.

---

## How to Run

### Inside Claude Code (the only way to run this)

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code will read `orchestrator.md` and execute the full pipeline:
1. Spawns **news-gatherer** → reads RSS feeds via WebFetch, returns scored articles
2. Spawns **trending-tracker** → searches trending AI topics via WebSearch
3. For each article cluster, spawns **post-generator** → writes and saves a draft
4. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration

All settings live in `config/` — each file is a standalone component you can edit independently:

| File | Purpose | Edit when... |
|------|---------|--------------|
| `config/topics.yaml` | Companies, keywords, and freshness settings | Adding a new AI company to track, adjusting how old articles can be |
| `config/sources.yaml` | RSS feeds and API sources | Adding a new news source, disabling a feed |
| `config/brand_kit.yaml` | Author voice, tone, writing style, and hashtag rules | Updating your name/title, changing tone or post length |
| `config/post_templates.yaml` | Post templates by content type | Tweaking how funding posts vs. product launch posts are framed |

Edit these files directly — changes take effect on the next run.

### First-time setup: fill in your brand

Open `config/brand_kit.yaml` and update:
```yaml
author:
  name: "Your Name"          # ← your full name
  title: "Your Title"        # ← e.g. "Brand Strategist & AI Experimenter"
  tagline: "..."             # ← your LinkedIn headline
  location: "City, Country"  # ← your location
```

Everything else in `brand_kit.yaml` is pre-configured with good defaults for AI-focused marketing content.

### Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# Required for Notion publishing (optional feature)
NOTION_PAGE_ID=your_32char_page_id_here

# Optional: direct Notion REST API fallback
NOTION_API_KEY=secret_xxx

# Optional: NewsAPI for additional sources
NEWSAPI_KEY=your_key_here
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
- **YAML frontmatter**: source metadata, companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON
- **Output**: JSON array of scored article objects

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days
- **Output**: JSON array of 15–20 keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/post_templates.yaml`
- **Does**: Selects the best-fit post template (product launch, funding, big tech, human-in-the-loop, etc.), synthesises a cluster of articles into a branded LinkedIn post, validates URLs, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, source metadata, and template used

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page
- **Output**: `success` or `failed`

---

## Customising Your Brand

Edit `config/brand_kit.yaml` to set:
- Your name, title, and professional tagline
- Tone traits (curious, pragmatic, opinionated, etc.)
- Writing style rules (paragraph length, hook style, etc.)
- Post structure preferences
- Hashtag strategy
- Minimum sources per post

The post-generator agent reads this file on every run — no restarts needed.

---

## Post Templates

`config/post_templates.yaml` contains six post templates, each tuned for a different kind of story:

| Template | Triggered by | Best for |
|----------|-------------|---------|
| `ai_product_launch` | Feature/launch articles | ChatGPT, Claude, Gemini, ElevenLabs, Midjourney announcements |
| `ai_startup_funding` | Funding/acquisition articles | Series A–C rounds, unicorn valuations, acquisitions |
| `big_tech_ai` | Microsoft, Google, Apple, Meta, Nvidia moves | Strategic pivots, enterprise partnerships, platform plays |
| `human_in_the_loop` | Marketing/experiment articles | Your personal AI workflow experiments and honest results |
| `ai_regulation_policy` | Regulation/policy articles | EU AI Act, copyright battles, government AI rules |
| `ai_research` | Research/benchmark articles | Papers, capability milestones, benchmark results |
| `default` | Fallback | General AI news that doesn't fit the above |

To add a new template, copy any existing block, give it a unique `name`, set `trigger_categories` and `trigger_keywords`, and fill in the five guidance fields.

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
