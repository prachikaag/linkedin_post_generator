# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md             → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md          → finds trending keyword phrases
├── .claude/agents/post-generator.md            → writes & saves news-based LinkedIn post drafts
├── .claude/agents/experiment-post-generator.md → turns your own AI experiments into "I tried X" drafts
└── .claude/agents/notion-publisher.md          → publishes drafts to Notion (optional)
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
4. For each `"ready"` entry in `config/experiments.yaml`, spawns **experiment-post-generator** → writes and saves an "I tried X" draft
5. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster. Draft 1 experiment post.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration

All settings live in `config/`:

| File | Purpose |
|------|---------|
| `config/sources.yaml` | RSS feeds and API sources to fetch from |
| `config/topics.yaml` | Companies, keywords, and freshness settings |
| `config/brand_kit.yaml` | Author voice, tone, writing style, and hashtag rules |
| `config/experiments.yaml` | Your log of hands-on AI experiments — the human-in-the-loop input |

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

### `experiment-post-generator`
- **Tools**: Read, Write, Edit
- **Reads**: `config/experiments.yaml`, `config/brand_kit.yaml`
- **Does**: Turns one "ready" entry from your experiments log into a first-person "I tried X" post, saves it as a `.md` draft, then marks the entry `status: posted` and records the filename
- **Output**: JSON object with filename, filepath, content, and the experiment it came from

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

## Logging Your Own AI Experiments (Human-in-the-Loop)

The news pipeline covers what's happening in AI. This file covers what's happening with *you* in AI — the experiments, the tools you tried, the honest results. It's what turns "I follow AI news" into "I'm actually using this stuff."

Workflow:

1. After you try a new AI tool, feature, or workflow, add an entry to `config/experiments.yaml`:
   ```yaml
   - id: "exp-002"
     status: "ready"
     date_tried: "2026-06-25"
     tool: "Claude"
     feature: "Claude Code on the web"
     use_case: "Automating my LinkedIn content research pipeline"
     what_i_did: "Built a multi-agent pipeline that tracks AI news and drafts posts in my voice."
     what_happened: "Worked end-to-end on the first real run, needed only light editing."
     surprises: "Getting citations verifiably real was harder than getting the writing right."
     would_recommend: true
     rating: 4
     source_url: "https://www.anthropic.com/news/claude-code-on-the-web"
     source_name: "Anthropic"
     linked_post: null
   ```
2. Set `status: "ready"` when you want it turned into a post (leave it `"idea"` if you're just jotting a note for later).
3. On the next pipeline run, the **experiment-post-generator** picks up every `"ready"` entry (up to `MAX_EXPERIMENT_POSTS`, default 2), writes a first-person draft citing the tool's official source, and saves it to `posts/`.
4. The entry is automatically flipped to `status: "posted"` with `linked_post` pointing at the generated file — so you never get duplicate posts from the same experiment.

These posts skip the multi-source "EVIDENCE" structure used by news posts — they're a personal account (HOOK → WHAT I TRIED → WHAT HAPPENED → MY TAKE → SO WHAT → CTA → one source citation for the tool itself).

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
