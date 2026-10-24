# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents. Two modes — **news** (default) and **experiment** — cover the two main content pillars.

```
orchestrator.md
│
├── NEWS MODE (default)
│   ├── .claude/agents/news-gatherer.md           → fetches + scores RSS articles
│   ├── .claude/agents/trending-tracker.md        → finds trending keyword phrases
│   ├── .claude/agents/post-generator.md          → writes & saves news-reaction drafts
│   └── .claude/agents/notion-publisher.md        → publishes drafts to Notion (optional)
│
└── EXPERIMENT MODE
    ├── reads config/experiments.yaml             → your personal AI experiments log
    ├── .claude/agents/experiment-post-generator.md → writes "I tried X" post drafts
    └── .claude/agents/notion-publisher.md        → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and input/output contract. The orchestrator passes data between them — no Python glue code required.

---

## How to Run

### Inside Claude Code (the only way to run this)

Open this project in Claude Code and say:

**For news-based posts (default):**
```
Run the LinkedIn Post Generator pipeline.
```

**For personal experiment posts:**
```
Generate experiment posts from my experiments log.
```

**For both:**
```
Run the LinkedIn Post Generator pipeline in both modes.
```

Claude Code reads `orchestrator.md` and executes the full pipeline.

**News mode steps:**
1. Spawns **news-gatherer** → reads RSS feeds via WebFetch, returns scored articles
2. Spawns **trending-tracker** → searches trending AI topics via WebSearch
3. For each article cluster, spawns **post-generator** → matches content angle, writes and saves a draft
4. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

**Experiment mode steps:**
1. Reads `config/experiments.yaml` → finds entries with `post_worthy: true` + `status: draft`
2. For each experiment, spawns **experiment-post-generator** → writes an "I tried X" draft
3. Spawns **notion-publisher** → pushes to Notion (optional)

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration

All settings live in `config/` — edit any file directly, changes take effect immediately on the next run.

| File | Purpose | Edit when... |
|------|---------|-------------|
| `config/topics.yaml` | AI companies, keywords, and freshness settings | Adding a new AI company/tool to track |
| `config/sources.yaml` | RSS feeds, company blogs, YouTube channels, APIs | Adding or removing a news source |
| `config/brand_kit.yaml` | Your name, title, tone of voice, writing rules | Updating your personal brand voice |
| `config/content_angles.yaml` | 5 post type templates (launch, funding, experiment, etc.) | Adjusting how a post type is framed |
| `config/experiments.yaml` | Your personal AI experiments log | After testing a new AI tool |

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
- **Reads**: `config/brand_kit.yaml`, `config/content_angles.yaml`
- **Does**: Matches article cluster to a content angle (product_launch, funding_take, trend_analysis, brand_lens), writes a branded LinkedIn post, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, and source metadata

### `experiment-post-generator`
- **Tools**: Read, Write
- **Reads**: `config/experiments.yaml`, `config/brand_kit.yaml`, `config/content_angles.yaml`
- **Does**: Reads a personal AI experiment entry, writes a first-person "I tried X" post in brand voice, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, and experiment metadata

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
