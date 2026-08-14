# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, detects the type of story (YouTube launch, funding, feature, experiment), and writes research-backed LinkedIn draft posts in your personal brand voice — entirely through Claude agents and subagents. No traditional code steps.

---

## What It Does

1. **Monitors AI news sources** — RSS feeds from TechCrunch, The Verge, VentureBeat, company blogs (OpenAI, Anthropic, Google, ElevenLabs, Perplexity, and more), and YouTube channels from all the major AI companies
2. **Detects story types** — automatically categorises each article as a YouTube launch, feature release, funding news, big tech move, research breakthrough, or regulation update
3. **Tracks trending keywords** — searches the web for what's buzzing in AI this week to make posts more discoverable
4. **Writes posts in your brand voice** — uses your brand kit and tone-of-voice rules to write posts that sound like you, not like a press release
5. **Cites real sources** — every post includes numbered sources with full URLs
6. **Saves drafts for review** — all posts land in `posts/` as markdown files you can review and edit before publishing
7. **Publishes to Notion** (optional) — pushes drafts to a Notion page with toggle blocks, labelled by post type

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS + YouTube articles, detects post type
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases from web search
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts (post-type-aware)
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
1. Spawns **news-gatherer** → reads RSS + YouTube feeds via WebFetch, returns scored articles with post type
2. Spawns **trending-tracker** → searches trending AI topics via WebSearch
3. For each article cluster, spawns **post-generator** → writes and saves a typed draft
4. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Run the pipeline. Prioritise YouTube launch posts this run.
```

---

## Configuration Files

All settings live in `config/` — edit these directly, changes take effect on the next run:

| File | Purpose |
|------|---------|
| `config/sources.yaml` | RSS feeds and YouTube channels to fetch from |
| `config/topics.yaml` | Companies, keywords, freshness settings, and trending seed terms |
| `config/brand_kit.yaml` | Your name, voice, tone, writing style, and hashtag rules |
| `config/post_templates.yaml` | Per-post-type templates: angles, hook prompts, CTA examples |

### Key things to customise

**In `config/brand_kit.yaml`:**
- `author.name` — your name, used in every post
- `author.title` — your professional title
- `author.tagline` — your LinkedIn headline
- `tone_of_voice.primary_traits` — how you come across
- `brand.post_type_guidance` — per-type hook and angle instructions

**In `config/topics.yaml`:**
- `companies_to_track` — add or remove AI companies you want to follow
- `freshness.max_article_age_hours` — how fresh articles must be (default: 48h)
- `freshness.min_relevance_score` — minimum score to include an article (default: 2)

**In `config/sources.yaml`:**
- `rss_feeds` — add new RSS feeds for any publication
- `youtube_channels` — add YouTube channels from AI companies you want to track

**In `config/post_templates.yaml`:**
- Edit `detection_keywords` to tune which articles get which post type
- Edit `hook_prompts`, `angle`, and `cta_examples` to change how each post type is framed

---

## Post Types

The pipeline automatically detects and labels each article with a post type:

| Post Type | When used | Emoji in Notion |
|-----------|-----------|-----------------|
| `youtube_launch` | A new YouTube video from an AI company | 📹 |
| `feature_launch` | A new product, feature, or model release | 🚀 |
| `funding_news` | Startup funding round, acquisition, or IPO | 💰 |
| `big_tech_ai` | Microsoft, Google, Apple, Meta, Amazon, Nvidia AI news | 🏢 |
| `ai_experiment` | Personal experiments with AI tools (human-in-the-loop) | 🧪 |
| `research_breakthrough` | Research papers, benchmarks, capability milestones | 🔬 |
| `ai_regulation` | Policy, regulation, AI safety, ethics news | ⚖️ |

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-08-14_10-30-00_openai-launches-gpt5-model.md     [🚀 feature_launch]
  2026-08-14_10-30-00_anthropic-funding-round.md         [💰 funding_news]
  2026-08-14_11-00-00_elevenlabs-youtube-demo.md         [📹 youtube_launch]
```

Each file contains:
- **YAML frontmatter**: source metadata, post_type, companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

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

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`, `config/post_templates.yaml`
- **Does**: Fetches all enabled RSS and YouTube feeds, scores articles by keyword relevance, auto-detects post type, deduplicates, returns top articles as JSON
- **Output**: JSON array of scored article objects, each with `post_type`

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days, focused on the companies you track
- **Output**: JSON array of 15–20 keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/post_templates.yaml`
- **Does**: Detects post type from the article cluster, loads the matching template, synthesises articles into a branded LinkedIn post, validates URLs, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, post_type, and source metadata

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page, labelled with an emoji for the post type
- **Output**: `success` or `failed`

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
  - name: "Midjourney YouTube"
    url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE"
    priority: medium
    enabled: true
    post_type_hint: "youtube_launch"
```

To find a YouTube channel ID, go to the channel page, view source, and search for `"channelId"`.

---

## Tracking Companies

Edit `config/topics.yaml` → `companies_to_track` to add a new company:

```yaml
ai_labs:
  - name: "My New Company"
    keywords:
      - "Company Name"
      - "Their Product"
      - "Their Model Name"
```

Any article mentioning these keywords scores +3 per match, ensuring the company's news surfaces reliably.
