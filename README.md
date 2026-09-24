# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts in your voice — entirely through Claude agents and subagents.

Designed for brand strategists and marketers who follow AI news closely and want to publish opinionated, sourced LinkedIn posts that demonstrate they are **actively experimenting with AI** — human in the loop, not just observing.

---

## What It Does

1. **Reads your topics** — a list of AI companies, tools, and news categories you care about
2. **Fetches fresh news** — RSS feeds from TechCrunch, The Verge, VentureBeat, company blogs, and YouTube channels
3. **Filters out already-covered stories** — tracks post history so you never repeat yourself
4. **Finds trending keywords** — searches the web for what's buzzing in AI right now
5. **Writes branded LinkedIn posts** — follows your tone of voice, cites sources, stays within character limits
6. **Handles YouTube videos specially** — video demos from AI companies get a dedicated post format
7. **Publishes to Notion** (optional) — pushes drafts to your Notion review page

---

## Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles + YouTube videos
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts (news + YouTube formats)
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)

config/
├── interests.md        ← EDIT THIS FIRST — plain English topics of interest
├── brand_kit.yaml      ← EDIT THIS — your name, voice, tone, hashtags
├── topics.yaml         ← EDIT THIS — companies, keywords, freshness settings
├── sources.yaml        ← EDIT THIS — RSS feeds and YouTube channels
└── post_history.yaml   ← AUTO-MANAGED — tracks covered URLs (do not edit manually)
```

---

## Quick Start

### 1. Personalise your config files (do this once)

**`config/interests.md`** — The simplest file to edit. Plain English. Describes what you write about, which AI tools you follow, and what stories you want. No YAML required.

**`config/brand_kit.yaml`** — Your name, title, tone of voice, and post style. The most important file for getting posts that sound like you. Edit:
```yaml
author:
  name: "Prachi [Your Last Name]"
  title: "Your Actual Job Title"
  tagline: "Your LinkedIn tagline"
  location: "Your City, Country"
```

**`config/topics.yaml`** — Add or remove companies and keywords. Controls what counts as "relevant" when scoring news articles.

**`config/sources.yaml`** — Add or remove RSS feeds. Enable/disable any feed with `enabled: true/false`.

### 2. Set up Notion (optional but recommended)

Copy `.env.example` to `.env` and fill in your Notion page ID:
```bash
cp .env.example .env
```

Then edit `.env`:
```
NOTION_PAGE_ID=your_32char_page_id_here
```

See `.env.example` for setup instructions.

### 3. Run the pipeline

Open this project in Claude Code and say:
```
Run the LinkedIn Post Generator pipeline.
```

Claude Code will read `orchestrator.md` and execute the full pipeline.

---

## How to Run

### Inside Claude Code (required)

```
Run the LinkedIn Post Generator pipeline.
```

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration Files Reference

| File | What It Controls | How Often to Edit |
|------|-----------------|-------------------|
| `config/interests.md` | Plain English description of your focus areas | When your content strategy changes |
| `config/brand_kit.yaml` | Name, tone, voice, hashtags, post structure | Rarely — set once and tweak occasionally |
| `config/topics.yaml` | Companies tracked, keywords, freshness settings | When you want to track a new company or tool |
| `config/sources.yaml` | RSS feeds and YouTube channels | When you find a good new source |
| `config/post_history.yaml` | Tracks covered articles (auto-managed) | Only to clear history and allow re-coverage |

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md        ← type: news
  2024-01-15_10-30-00_google-deepmind-new-demo.md    ← type: youtube_video
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, categories, trending keywords, post type, status
- **Post body**: the full LinkedIn draft, ready to review and publish

### Reviewing your drafts

1. Open the `.md` file in any text editor or Markdown viewer
2. Read the post body
3. Edit anything you want to change — your voice, your take, the CTA
4. When you're happy, publish to LinkedIn and change `status: draft` to `status: published`

---

## Post Types

### News Post (standard)
Used for: AI feature launches, funding rounds, BigTech moves, research breakthroughs.

Structure: Hook → Context → Evidence → Your Take → So What → CTA → Sources → Hashtags

### YouTube Video Post
Used for: Demo videos, keynotes, and product walkthroughs from AI companies.

Structure: Hook → What I Watched → The Brand Angle → My Experiment → So What → CTA → Sources → Hashtags

The YouTube format is designed to sound like you actually watched the video and are sharing what's worth knowing for brand and marketing teams.

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds and YouTube channels, scores articles by keyword relevance, filters out previously covered URLs, flags YouTube videos as `type: youtube_video`, deduplicates, returns top articles as JSON
- **Output**: JSON array of scored article objects

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days
- **Output**: JSON array of 15–20 keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post using news or YouTube format, validates URLs, saves as `.md` draft
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
- Post structure preferences for both news and YouTube posts
- Content categories and angles
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

To add a YouTube channel:
```yaml
youtube_channels:
  - name: "Channel Name"
    url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE"
    priority: medium
    enabled: true
```

Find a YouTube channel's ID by going to the channel page and looking at the URL, or using a channel ID finder tool.

---

## Post History & Avoiding Repeats

The pipeline automatically tracks which article URLs have been used in generated posts via `config/post_history.yaml`. On each run, the news-gatherer filters out any article already covered.

To reset history and allow re-coverage of old topics, clear the file:
```yaml
covered_urls: []
covered_slugs: []
post_log: []
```

---

## Environment Variables

```bash
# Required for Notion publishing (optional feature)
NOTION_PAGE_ID=your_32char_page_id_here
NOTION_API_KEY=secret_xxx

# Optional: NewsAPI for additional sources
NEWSAPI_KEY=your_key_here
```
