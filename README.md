# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents. No traditional code steps.

---

## What It Does

1. **Reads your topics** — companies, keywords, and categories you care about (`config/topics.yaml`)
2. **Fetches fresh news** — scans RSS feeds from TechCrunch, VentureBeat, The Verge, company blogs, YouTube channels, and more (`config/sources.yaml`)
3. **Tracks what's trending** — searches the web for the most-discussed AI topics from the past 7 days
4. **Scores articles** — ranks each article by how closely it matches your topics
5. **Writes posts** — synthesises clusters of top articles into branded LinkedIn drafts that sound exactly like you
6. **Saves drafts** — writes markdown files to `posts/` with full YAML frontmatter for tracking
7. **Publishes to Notion** — optionally pushes each draft to a Notion page for review (if configured)

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with options:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration Files

Everything that controls the pipeline is split into separate files you can edit independently:

### `config/profile.yaml` — Your Identity
Your name, professional title, tagline, and location.
This appears in every post as the author's voice.

### `config/tone_of_voice.md` — How You Sound
Writing rules, post structure blueprint, dos, don'ts, and signature phrases.
Edit this to change the style of every post — paragraph length, emoji rules, hook format, what words to avoid.

### `config/brand_kit.yaml` — Your Brand Focus
The lenses you write through (AI for marketing, human-in-the-loop workflows, startup funding), your hashtag strategy, and post length settings.

### `config/topics.yaml` — What News to Track
The companies, products, and keywords you follow:
- AI labs (OpenAI, Anthropic, Google DeepMind, Mistral, etc.)
- AI builders and startups (Cursor, Synthesia, Suno, Groq, etc.)
- Big tech (Microsoft, Apple, Amazon, Nvidia, Salesforce, Adobe)
- Topic categories (feature launches, funding, marketing AI, research, regulation)

Also controls freshness settings — how old an article can be, minimum relevance score.

### `config/sources.yaml` — Where to Get News
All RSS feeds the pipeline fetches from:
- General AI news (TechCrunch, The Verge, VentureBeat, Wired, MIT Tech Review)
- Company blogs (OpenAI, Anthropic, Google AI, DeepMind, Meta AI, HuggingFace)
- Funding news (Crunchbase, TechCrunch Startups, SiliconAngle)
- YouTube channels (Google DeepMind, OpenAI, Anthropic, Two Minute Papers)

Add any RSS feed by adding an entry to the appropriate section.

---

## Setup

### 1. First Run (no Notion)

Just open the project in Claude Code and run the pipeline. Posts save to `posts/` as `.md` files.

### 2. Enable Notion Publishing (optional)

Copy `.env.example` to `.env` and fill in your Notion credentials:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
NOTION_API_KEY=secret_xxx          # from notion.so/my-integrations
NOTION_PAGE_ID=your32charPageId    # from your Notion page URL
```

Setup steps for Notion:
1. Go to `https://www.notion.so/my-integrations` → New integration (Internal)
2. Copy the **Internal Integration Token** → paste as `NOTION_API_KEY`
3. Open your LinkedIn Post Ideas Notion page
4. `...` menu → Connections → connect your integration
5. Copy the 32-char page ID from the URL → paste as `NOTION_PAGE_ID`

### 3. Personalise Your Profile

Edit `config/profile.yaml` — replace placeholder values with your real name, title, and tagline.

### 4. Personalise Your Brand

Edit `config/brand_kit.yaml` to adjust focus areas and hashtags.
Edit `config/tone_of_voice.md` to adjust writing style rules.

---

## Output

Generated posts save to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-06-27_09-00-00_openai-launches-gpt5-model.md
  2026-06-27_09-00-00_anthropic-raises-series-e.md
```

Each file contains:
- **YAML frontmatter**: sources, companies mentioned, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Architecture

The pipeline is a multi-agent system where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases via web search
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

### news-gatherer
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON

### trending-tracker
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- Searches the web for trending AI topics from the past 7 days and returns 15–20 keyword phrases

### post-generator
- **Tools**: Read, Write
- **Reads**: `config/profile.yaml`, `config/tone_of_voice.md`, `config/brand_kit.yaml`
- Synthesises a cluster of articles into a branded LinkedIn post, saves as `.md` draft

### notion-publisher
- **Tools**: Read, Notion MCP
- Appends the post as a toggle block on a Notion page

---

## Customising Your Voice

| To change... | Edit this file |
|---|---|
| Your name and title | `config/profile.yaml` |
| Writing style and tone | `config/tone_of_voice.md` |
| Post topics and hashtags | `config/brand_kit.yaml` |
| Which companies to track | `config/topics.yaml` |
| Which news sources to use | `config/sources.yaml` |
| Notion page destination | `.env` → `NOTION_PAGE_ID` |

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
