# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, watches YouTube channels from tracked companies, tracks what's trending, and writes research-backed LinkedIn draft posts — entirely through Claude agents. No Python glue code required.

---

## What It Does

1. **Watches YouTube channels** from AI companies (OpenAI, Anthropic, Google DeepMind, etc.) — new video releases are high-priority signals for product launches
2. **Fetches AI news** from 20+ RSS feeds covering tech news, company blogs, and funding announcements
3. **Tracks trending keywords** across the web to match posts to what people are searching for
4. **Deduplicates** against your published post log — never writes about the same story twice
5. **Generates LinkedIn drafts** using your personal brand kit, tone of voice, and citation standards
6. **Reviews each draft** against your brand kit (optional, human-in-the-loop)
7. **Publishes to Notion** for review before you post (optional)

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/youtube-watcher.md    → detects new YouTube videos from AI company channels
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
├── .claude/agents/post-reviewer.md      → human-in-the-loop brand kit check (optional)
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and input/output contract.

---

## Configuration — Your Editable Components

All settings live in `config/`. **Edit these files directly — changes take effect on the next run.**

| File | What It Controls | When to Edit |
|------|-----------------|--------------|
| `config/brand_kit.yaml` | Your name, title, voice, tone, post structure, hashtags | Set up once; refine as your brand evolves |
| `config/topics.yaml` | AI companies to track, topic categories, freshness settings | Add/remove companies as the landscape shifts |
| `config/sources.yaml` | RSS feeds and YouTube channels to monitor | Add new feeds; disable irrelevant ones |
| `config/published_log.yaml` | Log of posts already written; topics to skip | Update after posting; add topics to skip |

---

## How to Run

### Inside Claude Code

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code will read `orchestrator.md` and execute the full pipeline automatically.

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline with human-in-the-loop review enabled.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Run the LinkedIn Post Generator. Focus on YouTube video releases and AI startup funding news.
```

---

## Setup

### 1. Fill in your brand kit

Edit `config/brand_kit.yaml` and update the `author` section:

```yaml
author:
  name: "Your Name"          # Your name as it should appear in posts
  title: "Your Title"        # Your professional title
  tagline: "Your tagline"    # Your LinkedIn tagline
  location: "Your City"      # Your location
```

The tone, voice rules, post structure, and hashtags are already tuned for your brand — adjust any rule that doesn't feel right.

### 2. Set up your environment

```bash
cp .env.example .env
```

Then edit `.env`:
- **`NOTION_PAGE_ID`** — your Notion page ID (optional, for publishing to Notion)
- **`REVIEW_BEFORE_SAVE`** — set to `true` to enable draft review before saving
- **`ANTHROPIC_API_KEY`** — only needed if running outside Claude Code

### 3. Customise your topics (optional)

Edit `config/topics.yaml` to:
- Add new companies under `companies_to_track`
- Change how fresh articles need to be (`max_article_age_hours`)
- Lower the minimum relevance score to get more articles

### 4. Add or remove news sources (optional)

Edit `config/sources.yaml` to:
- Add any RSS feed (set `enabled: true`)
- Disable feeds that aren't relevant (set `enabled: false`)
- Add YouTube channels under `rss_feeds.youtube_channels`

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-05-14_22-55-00_enterprise-ai-market-shift-real-data.md
  2026-05-14_23-10-00_vertical-ai-depth-over-horizontal.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, categories, trending keywords, review notes, status
- **Post body**: the full LinkedIn draft, ready to review and publish

**After posting to LinkedIn:**
1. Change `status: draft` to `status: published` in the file's frontmatter
2. Add an entry to `config/published_log.yaml` to prevent re-covering the same story

---

## Agents Reference

### `youtube-watcher`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches YouTube RSS feeds for all tracked AI company channels, detects new videos in the freshness window, scores them as high-priority articles
- **Output**: JSON array of video objects (same schema as news articles, plus `is_youtube_video: true`)

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
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post following the brand kit exactly, validates URLs, saves as `.md` draft
- **Output**: JSON object with filename, filepath, content, and source metadata

### `post-reviewer`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`
- **Does**: Checks draft against brand kit rules — hook quality, emoji count, word/character limits, no forbidden words, source count, CTA quality. Flags specific issues with fix suggestions. Updates frontmatter with review notes.
- **Output**: JSON object with issues list and suggestions

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page
- **Output**: `success` or `failed`

---

## Tracking What You've Published

`config/published_log.yaml` is your publishing history. It prevents re-writing the same stories.

**Workflow after posting:**
1. Post goes live on LinkedIn
2. Open `posts/YYYY-MM-DD_..._slug.md` and change `status: draft` → `status: published`
3. Add the post to `config/published_log.yaml`:

```yaml
published_posts:
  - title: "Your post title"
    slug: "the-post-slug"
    date: "2026-05-14"
    status: "published"
    primary_url: "https://techcrunch.com/..."
    matched_companies:
      - "OpenAI"
```

Future pipeline runs will skip articles whose URLs appear in `published_log`.

**To permanently skip a topic:**
```yaml
skipped_topic_phrases:
  - "EU AI Act"        # not relevant to your audience
  - "Cerebras IPO"     # already covered
```

---

## Customising Your Brand

Edit `config/brand_kit.yaml` to set or change:
- Your name, title, and professional tagline
- Tone traits (curious, pragmatic, opinionated, etc.)
- Writing style rules (paragraph length, hook style, etc.)
- Post structure sections and their lengths
- Hashtag strategy
- Signature phrases that are distinctly yours
- Minimum sources per post

The post-generator reads this file on every run — no restarts needed.

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

To add a YouTube channel:

```yaml
rss_feeds:
  youtube_channels:
    - name: "Midjourney YouTube"
      url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE"
      priority: high
      enabled: true
```

Find a channel's ID by visiting their YouTube page and checking the URL, or using a channel ID lookup tool.
