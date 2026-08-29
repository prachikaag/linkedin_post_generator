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

All settings live in `config/` — each file is a standalone editable component:

| File | Purpose |
|------|---------|
| `config/topics.yaml` | Companies and keywords to track (OpenAI, Claude, Perplexity, Midjourney, etc.) |
| `config/sources.yaml` | RSS feeds, company blogs, YouTube channels, and optional APIs |
| `config/brand_kit.yaml` | Your name, tone of voice, writing style, post structure, and hashtags |
| `config/content_pillars.yaml` | Content angles: human-in-loop, product launch, startup funding, big tech, research, policy |
| `posts/published_log.yaml` | Memory log — tracks covered topics to avoid repetition across runs |

Edit these files directly — changes take effect on the next run.

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
- **Reads**: `config/brand_kit.yaml`, `config/content_pillars.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post, selects the right content pillar (human-in-loop, product launch, funding, big tech, research, policy), validates URLs, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, pillar, and source metadata

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

## Content Pillars

The pipeline matches each article cluster to a content angle before generating the post. Edit `config/content_pillars.yaml` to change the angle, opening templates, or required elements per pillar.

| Pillar ID | When it fires | Your angle |
|-----------|--------------|------------|
| `human_in_loop` | New feature / tool you've personally tested | First-person experiment report |
| `product_launch` | Major model or product release | What changed and what brands should do |
| `startup_funding` | Funding round, acquisition, IPO | What the money signals about market direction |
| `big_tech_ai` | Microsoft, Google, Apple, Meta, Nvidia move | Practical impact on brand and marketing teams |
| `research_breakthrough` | Research paper, benchmark, capability jump | Translated for non-technical brand leaders |
| `regulation_policy` | EU AI Act, copyright ruling, safety event | Rules for brands using AI |

---

## Memory (Avoiding Repetition)

Every time a post is generated, the pipeline appends an entry to `posts/published_log.yaml`. On the next run, companies and topics covered recently are deprioritised so you don't write about the same thing twice.

Adjust the cooldown windows in `published_log.yaml`:
```yaml
company_cooldown_days: 7   # days before covering the same company again
topic_cooldown_days: 3     # days before covering the same topic category again
```

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
