# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks trending topics, and writes research-backed LinkedIn posts in your brand voice — with cited sources.

---

## How to Run

Open this project in Claude Code, then say:

> **Run the LinkedIn Post Generator pipeline**

Claude reads `orchestrator.md` and executes the full pipeline automatically.

### Common invocations

| What to say | What happens |
|---|---|
| "Run the pipeline" | Generates 2 posts (default) |
| "Run the pipeline, 3 posts" | Generates 3 posts |
| "Run a dry run" | Fetches news + trending topics, prints top articles — no posts written |
| "Run the pipeline and publish to Notion" | Generates posts AND pushes to Notion (requires Notion configured in `.env`) |

---

## One-time Setup

### 1 — Fill in your brand details

Edit `config/brand_kit.yaml` — the `author` block at the top:

```yaml
author:
  name: "Your Full Name"
  title: "Your Job Title / Headline"
  tagline: "One-line LinkedIn tagline"
  location: "City, Country"
```

Everything else in `brand_kit.yaml` (tone, style rules, hashtags, post structure) is ready to use and tuned for AI content. Edit as needed.

### 2 — (Optional) Connect Notion

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then fill in your Notion credentials (instructions in `.env.example`):

```
NOTION_API_KEY=secret_xxxx
NOTION_PAGE_ID=your32charPageId
```

### 3 — (Optional) Add NewsAPI for broader news coverage

Free key at `https://newsapi.org/`. Add to `.env`:

```
NEWSAPI_KEY=your_key_here
```

Then in `config/sources.yaml`, set `enabled: true` under `optional_apis.newsapi`.

---

## Project Components — All Separately Editable

```
linkedin_post_generator/
│
├── config/
│   ├── topics.yaml        ← Companies + keywords to track; trending seed terms
│   ├── sources.yaml       ← RSS feeds and APIs to pull from
│   └── brand_kit.yaml     ← Your tone of voice, post structure, hashtags, style rules
│
├── memory/
│   ├── seen_articles.yaml ← URLs of articles already used — prevents repeats across runs
│   └── post_history.yaml  ← Log of all generated posts (topic, date, filename)
│
├── posts/                 ← Generated .md draft posts land here
│
├── orchestrator.md        ← The main pipeline: spawns all subagents in order
│
├── .claude/agents/
│   ├── news-gatherer.md       ← Fetches RSS feeds, scores + deduplicates articles
│   ├── trending-tracker.md    ← Web-searches for trending AI keywords this week
│   ├── post-generator.md      ← Writes the LinkedIn post following your brand kit
│   └── notion-publisher.md    ← (Optional) Pushes draft to your Notion page
│
├── .env.example           ← Copy to .env and fill in keys
└── CLAUDE.md              ← This file
```

---

## Editing Each Component

### Add/remove companies to track

Edit `config/topics.yaml` under `companies_to_track`:

```yaml
ai_labs:
  - name: "New Company"
    keywords:
      - "New Company"
      - "Their Main Product"
```

Higher-scored keywords surface those articles earlier. Company keyword hits = +3 points; category keyword hits = +1 point.

### Add/remove news sources

Edit `config/sources.yaml`. Each feed has:
- `enabled: true/false` — toggle without deleting
- `priority: high/medium/low` — high feeds are fetched first
- `url` — RSS or Atom feed URL

YouTube channel feeds follow the format:
```
https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID
```

### Change your writing style

Edit `config/brand_kit.yaml`:

| Section | What it controls |
|---|---|
| `tone_of_voice.primary_traits` | How you come across (curious, pragmatic, opinionated…) |
| `tone_of_voice.writing_style` | Hard rules applied to every post |
| `tone_of_voice.post_structure` | The ordered blueprint every post follows |
| `tone_of_voice.dos` / `donts` | Credibility rules |
| `brand.hashtags` | `always_include` + `rotate_from` pool |
| `brand.post_length` | `short` (300-500 chars), `medium` (500-900), `long` (900-1300) |
| `brand.content_angles` | Prompt templates for the post angle |

### Change what topics are trending

Edit `trending_keywords.seed_terms` in `config/topics.yaml`. These are the anchor terms the trending-tracker searches around.

---

## Generated Posts

Posts land in `posts/` as markdown files:

```
posts/2026-06-06_14-32-00_openai-launches-gpt5.md
```

Each file has YAML frontmatter (title, sources, matched companies, status) followed by the ready-to-copy post body.

**Status is always `draft`** — nothing is published to LinkedIn automatically. You review, edit, and post manually.

If Notion is configured, each post is also appended as a collapsible toggle block to your Notion page.

---

## Memory System

The generator tracks what it has already processed so you don't get the same articles twice.

| File | Purpose |
|---|---|
| `memory/seen_articles.yaml` | URLs of articles already used in past runs |
| `memory/post_history.yaml` | Log of all generated posts with date, topic, and filename |

**To reset memory** (re-process all articles fresh):

```bash
# Clear seen articles only
echo "seen_articles: []" > memory/seen_articles.yaml

# Clear full post history
echo "posts: []" > memory/post_history.yaml
```

---

## Pipeline Flow

```
orchestrator.md
│
├── [0] Read memory/seen_articles.yaml
│
├── [1] news-gatherer      → fetches RSS, scores by keyword, skips seen URLs
│                            returns: ranked JSON array of fresh articles
│
├── [2] trending-tracker   → web-searches trending AI phrases this week
│                            returns: 15-20 keyword phrases
│
├── [3] Build clusters     → groups articles into per-post bundles
│
├── [4] post-generator     → writes post per cluster following brand_kit.yaml
│                            saves: posts/YYYY-MM-DD_slug.md
│
├── [5] notion-publisher   → (if configured) pushes draft to Notion
│                            appends toggle block to your Notion page
│
└── [6] Update memory      → appends used URLs to seen_articles.yaml
                             appends post log entry to post_history.yaml
```
