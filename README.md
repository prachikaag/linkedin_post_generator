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

All settings live in `config/` — edit these files directly, changes take effect on the next run:

| File | Purpose |
|------|---------|
| `config/brand_kit.yaml` | **Start here.** Your name, tone of voice, writing style, hashtags |
| `config/topics.yaml` | Companies, keywords, and freshness settings to track |
| `config/sources.yaml` | RSS feeds and API sources to fetch from |
| `config/post_templates.yaml` | Post angles for each content type (launch, funding, big tech, experiment, trend) |
| `config/experiments.yaml` | **Your personal AI experiments log** — the "human in the loop" library |

### `config/experiments.yaml` — Your experiments log

This is the most personal piece of the system. Every time you try a new AI tool, add an entry here:

```yaml
experiments:
  - date: "2026-06-01"
    tool: "Perplexity"
    tool_category: "research"
    use_case: "Research for a client strategy deck"
    what_i_did: "Used Perplexity Pro to pull competitor landscape data"
    what_surprised_me: "Cited sources inline — saved hours of tracking references"
    what_didnt_work: "Funding figures needed manual verification"
    verdict: "Best research tool I've found; treat numbers as leads, not facts."
    would_recommend_for: "Rapid competitive research and landscape analysis"
    share_in_posts: true
```

When the post generator finds an article about a tool you've experimented with, it pulls your real experience and weaves it into the post — making the content uniquely yours.

### Memory (deduplication)

`memory/processed_urls.json` tracks which article URLs have already been used.
On each run, the orchestrator filters those out so you never write two posts about the same article.
To re-process an article, delete its URL from the `processed` list in that file.

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
- **Reads**: `config/brand_kit.yaml`, `config/post_templates.yaml`, `config/experiments.yaml`
- **Does**: Selects the right post template for the content type, optionally weaves in a first-person experiment, synthesises articles into a branded post, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, template used, and whether a personal experiment was woven in

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
