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

### Choose a specific post angle

```
Run the pipeline. Use the funding_news angle.
```

```
Run the pipeline. Use the youtube_reaction angle.
```

Available angles (defined in `config/post_angles.yaml`):

| Angle | Use when |
|-------|----------|
| `feature_launch` | A new AI model, tool, or feature was released |
| `youtube_reaction` | An AI company published a notable YouTube video |
| `funding_news` | An AI startup raised a round, was acquired, or went public |
| `big_tech_move` | Google, Microsoft, Apple, Amazon, or Meta made a significant AI announcement |
| `experiment` | You personally tested an AI tool and want to share the results |

### Write an experiment post from your log

Add your experiment to `config/experiments.yaml`, then:

```
Run the pipeline. Use the experiment angle. Use experiment-002.
```

The generator will blend your first-person observations with supporting news coverage.

---

## Configuration

All settings live in `config/` — every file is designed to be edited directly:

| File | Purpose |
|------|---------|
| `config/sources.yaml` | RSS feeds and API sources to fetch from |
| `config/topics.yaml` | Companies, keywords, and freshness settings |
| `config/brand_kit.yaml` | Author voice, tone, writing style, and hashtag rules |
| `config/post_angles.yaml` | 5 content angle templates — feature launches, YouTube reactions, funding news, big tech moves, experiments |
| `config/experiments.yaml` | Your personal AI experiment log — the source for "I tried X" posts |

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

**Start here**: edit `config/brand_kit.yaml` to set your name, title, and tagline — the generator uses these for every post.

| What you want to change | Where to edit |
|-------------------------|---------------|
| Your name, title, tagline | `config/brand_kit.yaml` → `author` section |
| Your tone of voice and writing rules | `config/brand_kit.yaml` → `tone_of_voice` section |
| Your hashtag strategy | `config/brand_kit.yaml` → `brand.hashtags` |
| Which companies and topics to track | `config/topics.yaml` |
| Which news sources to follow | `config/sources.yaml` |
| How each type of post is structured | `config/post_angles.yaml` |
| Your personal AI experiments | `config/experiments.yaml` |

All files are read fresh on every run — no restart needed after editing.

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
