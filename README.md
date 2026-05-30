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

All settings live in `config/`. These are the five files you edit to control everything.

| File | Controls | Edit when... |
|------|----------|--------------|
| `config/topics.yaml` | Companies, keywords, freshness thresholds | You want to track a new company or keyword |
| `config/sources.yaml` | RSS feeds and news sources | You want to add or remove a news source |
| `config/brand_kit.yaml` | Your name, brand focus areas, hashtags, post length | You change your professional identity or hashtag strategy |
| `config/tone_of_voice.yaml` | HOW you write — voice traits, style rules, post structure, dos/donts, banned words | You want to tune your writing voice or add/remove rules |
| `config/post_types.yaml` | Post templates per content category (feature launch, funding, YouTube drop, big tech, personal experiment) | You want to adjust the angles or hooks for a specific type of news |

### Quick start: fill in your details

Open `config/brand_kit.yaml` and update the `author` section:

```yaml
author:
  name: "Your Name"        # ← change this
  title: "Your Title"      # ← change this
  tagline: "..."           # ← change this
  location: "..."          # ← change this
```

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
- **YAML frontmatter**: source metadata, post type, companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Post Types

The post-generator automatically detects the right content type based on what the news articles are about, then applies type-specific hooks, angles, and takeaways.

| Post Type | When It Triggers | Focus |
|-----------|-----------------|-------|
| `feature_launch` | New model, tool, or feature from an AI company | What it does, how brands can use it today |
| `startup_funding` | Series A/B/C, acquisition, IPO, valuation | What the money tells us about the market |
| `youtube_video` | YouTube drops, demos, keynotes | What the demo reveals beyond the press release |
| `bigtech_ai` | Microsoft, Google, Apple, Amazon, Meta, Nvidia AI moves | Scale, lock-in, and what it means at platform level |
| `personal_experiment` | You tested a tool or ran a workflow | Honest results, specific prompts, what actually worked |
| `research_breakthrough` | Papers, benchmarks, capability milestones | Real-world implications for brands and marketers |

To add a new post type, open `config/post_types.yaml` and copy any existing block.

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
- **Reads**: `config/brand_kit.yaml`, `config/tone_of_voice.yaml`, `config/post_types.yaml`
- **Does**: Detects content type, synthesises a cluster of articles into a branded LinkedIn post, validates URLs, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, post type, and source metadata

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page
- **Output**: `success` or `failed`

---

## Tuning Your Voice

The fastest way to improve post quality is to edit `config/tone_of_voice.yaml`.

**To change how you sound:** edit `primary_traits`

**To change how you write:** edit `writing_style`

**To change what you never say:** edit `banned_words`

**To change the post blueprint:** edit `post_structure`

**To add a new hook style or angle:** open `config/post_types.yaml` and add to the relevant post type's `hook_templates` or `key_angles`

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

Set `enabled: false` to pause a feed without deleting it.

---

## Tracking New Companies

Edit `config/topics.yaml` under `companies_to_track`:

```yaml
companies_to_track:
  ai_labs:
    - name: "New Company"
      keywords:
        - "New Company"
        - "their product name"
        - "their CEO name"
```

Articles mentioning these keywords score +3 per match and are prioritised in the pipeline.
