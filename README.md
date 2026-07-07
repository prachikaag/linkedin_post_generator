# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── config/content_ideas.yaml            → user-queued post ideas (loaded first)
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
│     └── config/experiments.yaml        → personal AI experiments for first-person angles
│     └── config/brand_kit.yaml          → tone of voice and writing rules
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

All settings live in `config/` — edit any file directly, changes take effect on the next run:

| File | Purpose |
|------|---------|
| `config/sources.yaml` | RSS feeds, YouTube channels, and API sources to fetch from |
| `config/topics.yaml` | Companies, keywords, trending seed terms, and freshness settings |
| `config/brand_kit.yaml` | Author voice, tone of voice, writing style, and hashtag rules |
| `config/experiments.yaml` | Your personal AI experiments — the post-generator uses these for first-person angles |
| `config/content_ideas.yaml` | A queue of post ideas you want the pipeline to build around |

### Quick guide: adding an experiment

Open `config/experiments.yaml` and copy the template block at the bottom. Fill in:
- `tool` — which AI tool you tested
- `use_case` — what you were trying to accomplish
- `what_surprised_me` — this usually becomes your hook
- `verdict` — your honest conclusion

Set `post_used: false` and the post-generator will pick it up on the next run. It sets this to the frontmatter `experiment_used` field once the post is saved so you can track it.

### Quick guide: queueing a post idea

Open `config/content_ideas.yaml` and copy the template block. Set `priority: high` for ideas you want picked up next run. The orchestrator passes the idea to the post-generator, which uses the `angle` and `notes` fields to shape the post's framing — while still grounding it in fresh news.

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
- **Does**: Fetches all enabled RSS feeds and YouTube channel feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON
- **Output**: JSON array of scored article objects

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days across model releases, funding, and research
- **Output**: JSON array of 15–20 keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/experiments.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post; injects a first-person experiment angle if a relevant experiment exists; honours a content idea if supplied; validates URLs; saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, experiment used, and source metadata

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a collapsible toggle block on a Notion page with status callout
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
