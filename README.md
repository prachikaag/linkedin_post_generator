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

```
Run the LinkedIn Post Generator pipeline with CONTENT_TYPE "AI Tool Launch".
```

```
Run the LinkedIn Post Generator pipeline with CONTENT_TYPE "Human-in-the-Loop Experiment".
```

```
Run the LinkedIn Post Generator pipeline with CONTENT_TYPE "YouTube Video or Demo Release".
```

### Available content types

| Content Type | What it covers |
|---|---|
| `AI Tool Launch` | New model, product, or feature releases |
| `Human-in-the-Loop Experiment` | Real-world AI testing — your experiments and results |
| `YouTube Video or Demo Release` | AI company demo or keynote videos |
| `AI Startup Funding` | Investment rounds, acquisitions, IPOs |
| `Big Tech AI Move` | Microsoft / Apple / Google / Meta / Amazon AI news |
| `AI for Marketing` | How brands and agencies are using AI |

---

## Configuration

All settings live in `config/`:

| File | Purpose |
|------|---------|
| `config/sources.yaml` | RSS feeds and YouTube channels to monitor |
| `config/topics.yaml` | Companies, keywords, content categories, and freshness settings |
| `config/brand_kit.yaml` | Author voice, tone, writing style, content types, and hashtag rules |

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
- **Reads**: `config/brand_kit.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post, validates URLs, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, and source metadata

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page
- **Output**: `success` or `failed`

---

## Customising Your Brand

Edit `config/brand_kit.yaml` to set:
- Your name, title, and professional tagline (update the `author` section first)
- Tone traits (curious, pragmatic, opinionated, etc.)
- Writing style rules (paragraph length, hook style, etc.)
- Post structure preferences
- Content types — named post formats with their angle and hook style
- Hashtag strategy
- Minimum sources per post

The post-generator agent reads this file on every run — no restarts needed.

### First-time setup checklist

1. Open `config/brand_kit.yaml` and update the `author` section with your real name, title, and tagline
2. Review `brand.content_types` and edit the `angle` descriptions to match how you personally write
3. Add or remove companies in `config/topics.yaml` → `companies_to_track`
4. Copy `.env.example` to `.env` and add your `NOTION_PAGE_ID` if you use Notion
5. Run the pipeline and review the draft in `posts/`

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
