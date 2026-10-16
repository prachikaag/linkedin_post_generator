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

All settings live in `config/` — each is a separate file you can edit without touching anything else:

| File | Purpose |
|------|---------|
| `config/sources.yaml` | RSS feeds and API sources to fetch from |
| `config/topics.yaml` | Companies, keywords, and freshness settings |
| `config/brand_kit.yaml` | Author voice, tone, writing style, and hashtag rules |
| `config/my_experiments.yaml` | Your personal AI experiment log — the "human in the loop" file |

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
- Your name, title, and professional tagline
- Tone traits (curious, pragmatic, opinionated, etc.)
- Writing style rules (paragraph length, hook style, etc.)
- Post structure preferences
- Hashtag strategy
- Minimum sources per post

The post-generator agent reads this file on every run — no restarts needed.

---

## Your Personal AI Experiments (Human-in-the-Loop)

Edit `config/my_experiments.yaml` to log your personal AI experiments.

Each entry you add can be woven into posts to create "I tried X — here's what happened" content:

```yaml
experiments:
  - tool: "ChatGPT o3"
    company: "OpenAI"
    date_started: "2026-10-01"
    experiment_status: "ongoing"
    use_case: "Writing competitive landscape briefs for clients"
    what_i_tried: "Gave it our full brand brief and asked for 3 competitor angles..."
    what_worked: "Surfaced framing I hadn't considered in under 2 minutes"
    what_surprised_me: "It pushed back on one of my assumptions — correctly"
    what_didnt_work: "Needed significant fact-checking on market share figures"
    my_verdict: "Use it for framing, not for facts."
    use_for_posts: true
```

When the post-generator finds an article about a company you've personally tested, it draws on your experiment to add a first-person angle to the post. Set `use_for_posts: false` to keep an experiment in your log but out of posts.

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
