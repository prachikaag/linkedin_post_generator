# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md              → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md           → finds trending keyword phrases
├── .claude/agents/post-generator.md             → writes & saves news-driven drafts
├── .claude/agents/experiments-post-generator.md → writes "I tried this" experiment posts
└── .claude/agents/notion-publisher.md           → publishes drafts to Notion (optional)
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
3. For each article cluster, spawns **post-generator** → writes and saves a news draft
4. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

### Generate an experiment post (human-in-the-loop)

```
Run the LinkedIn Post Generator pipeline with INCLUDE_EXPERIMENT_POST=true.
```

This adds a step that reads your first unpublished experiment from `config/personal_experiments.yaml` and writes a personal "I tried this" LinkedIn post alongside the news posts.

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration

All settings live in `config/` — **edit these files to make the pipeline yours**:

| File | Purpose |
|------|---------|
| `config/brand_kit.yaml` | **Start here** — your name, voice, tone, style, and hashtag rules |
| `config/topics.yaml` | Companies and keywords to track (ChatGPT, Claude, ElevenLabs, etc.) |
| `config/sources.yaml` | RSS feeds and API sources to fetch from |
| `config/personal_experiments.yaml` | Log your hands-on AI experiments for experiment posts |

### First-time setup checklist

1. **`config/brand_kit.yaml`** — update `author.name`, `author.title`, `author.location`, and `author.tagline`
2. **`config/personal_experiments.yaml`** — add your first AI experiment (copy the template at the top)
3. **`.env`** — copy `.env.example` to `.env` and add your Notion page ID if you want Notion publishing

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
  2024-01-15_10-30-00_openai-launches-gpt5.md          ← news post
  2024-09-07_14-00-00_experiment-claude.md              ← experiment post
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

### `experiments-post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/personal_experiments.yaml`
- **Does**: Writes a first-person "I tried this AI tool" post from your logged experiments — the human-in-the-loop angle
- **Output**: JSON object with filename, filepath, content, and tool name

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

## Logging Personal AI Experiments

Edit `config/personal_experiments.yaml` to log every AI tool you try. Each entry has:
- **tool** — the AI tool name
- **date** — when you tried it (YYYY-MM-DD)
- **use_case** — what you used it for
- **what_worked** — honest positives with specifics
- **what_didnt** — honest limitations (this is what makes posts credible)
- **verdict** — your one-sentence brand-leader take
- **published** — set to `true` after the post goes live

The `experiments-post-generator` agent picks the first unpublished entry with a date set, writes the post, and returns its filename. Then manually set `published: true` in the yaml.

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
