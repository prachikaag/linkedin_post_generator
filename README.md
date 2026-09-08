# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, turns your personal AI experiments into posts, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md              → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md           → finds trending keyword phrases
├── .claude/agents/experiment-post-generator.md  → turns your AI experiments into posts
├── .claude/agents/post-generator.md             → writes & saves LinkedIn post drafts
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
1. Checks `config/experiments.yaml` for any personal AI experiments marked `ready` → generates "human in the loop" posts
2. Spawns **news-gatherer** → reads RSS feeds via WebFetch, returns scored articles
3. Spawns **trending-tracker** → searches trending AI topics via WebSearch
4. For each article cluster, spawns **post-generator** → writes and saves a draft
5. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Generate a post from my latest AI experiment only.
```

```
Run the pipeline experiments only — skip news, just process my experiment log.
```

---

## Configuration Files (edit these to customise)

All settings live in `config/` — edit any file and changes take effect on the next run.

| File | Purpose |
|------|---------|
| `config/topics.yaml` | Companies, keywords, and topic categories to track |
| `config/sources.yaml` | RSS feeds, company blogs, YouTube channels to fetch from |
| `config/brand_kit.yaml` | Your voice, tone, writing style, post structure, and hashtag strategy |
| `config/experiments.yaml` | Your personal AI experiments → becomes "human in the loop" posts |

---

## The 5 Agent Components

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds and YouTube channels, scores articles by keyword relevance, deduplicates, returns top articles as JSON
- **Output**: JSON array of scored article objects

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days
- **Output**: JSON array of 15–20 keyword phrases

### `experiment-post-generator` ← NEW
- **Tools**: Read, Write
- **Reads**: `config/experiments.yaml`, `config/brand_kit.yaml`
- **Does**: Finds experiments with `status: ready`, generates "I tried X — here's what happened" LinkedIn posts, marks experiments as processed
- **Output**: JSON with filenames and results; updates `experiments.yaml`

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`
- **Does**: Synthesises a cluster of news articles into a branded LinkedIn post, validates URLs, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, and source metadata

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page
- **Output**: `success` or `failed`

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-05-14_10-30-00_openai-launches-new-reasoning-model.md    ← news post
  2026-05-14_10-35-00_experiment-midjourney-v7.md               ← experiment post
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, categories, trending keywords, post type, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## The Experiments Workflow (Human in the Loop)

The `config/experiments.yaml` file is where you log your own AI experiments. Each entry can become a LinkedIn post in the "I tried X — here's what actually happened" format — the most authentic, credible content type for an AI-forward professional.

### To generate a post from an experiment:

1. Open `config/experiments.yaml`
2. Copy the template at the bottom of the file
3. Fill in the fields: what you did, what worked, what surprised you, what failed, your takeaway
4. Set `status: "ready"`
5. Run the pipeline — the experiment post generator will pick it up automatically

### Experiment fields:

| Field | What to write |
|-------|--------------|
| `tool` | The AI tool you tested |
| `use_case` | What you used it for |
| `what_i_did` | Step-by-step description of the experiment |
| `what_worked` | Specific wins |
| `what_surprised` | Unexpected findings (good or bad) |
| `what_failed` | What didn't work — be honest |
| `key_takeaway` | The single most important insight |
| `so_what_for_brands` | Concrete advice for brand/marketing teams |

---

## Customising Your Brand

Edit `config/brand_kit.yaml` to set:
- Your name and title (fill in the placeholders at the top)
- Your point of view and brand focus areas
- Tone traits and writing style rules
- Post structure preferences
- Hashtag strategy
- Minimum sources per post

The post-generator and experiment-post-generator agents read this file on every run — no restarts needed.

---

## Adding News Sources

Edit `config/sources.yaml` to add any RSS feed or YouTube channel:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true

youtube_channels:
  - name: "AI Company YouTube"
    url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID"
    priority: medium
    enabled: true
```

---

## Adding Topics to Track

Edit `config/topics.yaml` to add new companies, keywords, or topic categories:

```yaml
companies_to_track:
  ai_labs:
    - name: "New AI Company"
      keywords:
        - "Company Name"
        - "their product name"
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# Required for Notion publishing (optional feature)
NOTION_PAGE_ID=your_32char_page_id_here

# Optional: direct Notion REST API fallback
NOTION_API_KEY=secret_xxx

# Optional: NewsAPI for additional sources
NEWSAPI_KEY=your_key_here
```
