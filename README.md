# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

---

## What It Does

1. **Fetches fresh AI news** from 20+ RSS feeds (TechCrunch, The Verge, company blogs, YouTube channels, Crunchbase)
2. **Scores articles by relevance** against your tracked companies and topic categories
3. **Finds what's trending** via web search — recent launches, funding, model releases, product demos
4. **Writes LinkedIn posts** in your voice, with cited sources, structured exactly the way you write
5. **Saves drafts to `posts/`** as markdown files with YAML frontmatter
6. **Optionally pushes to Notion** for review before publishing

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

Each agent is a self-contained markdown file with its own role, tools, and input/output contract.

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code reads `orchestrator.md` and runs the full pipeline:
1. Spawns **news-gatherer** → reads RSS feeds, returns scored articles
2. Spawns **trending-tracker** → searches for trending AI topics
3. For each article cluster, spawns **post-generator** → writes and saves a draft
4. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

### Custom parameters

```
Run the pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration — All Editable Components

All settings live in `config/`. Edit any of these files to change how the pipeline behaves.

| File | What it Controls |
|------|-----------------|
| `config/brand_kit.yaml` | Author name, title, tagline, hashtag strategy, post length limits |
| `config/tone_of_voice.md` | Full writing voice guide — hooks, forbidden words, tone traits, examples |
| `config/content_pillars.md` | The 6 things you write about — with angle starters for each pillar |
| `config/experiments_log.md` | Your AI experiment diary — raw material for "human in the loop" posts |
| `config/topics.yaml` | Companies and keywords to track (OpenAI, Anthropic, Midjourney, etc.) |
| `config/sources.yaml` | RSS feeds and news sources to fetch from |

### The 6 Content Pillars (defined in `config/content_pillars.md`)

| # | Pillar | Trigger |
|---|--------|---------|
| 1 | **AI Tool Experiments** | You tested a tool on a real project |
| 2 | **New AI Launches** | A tracked company ships something new |
| 3 | **AI × Marketing & Brand Strategy** | An AI development has brand implications |
| 4 | **AI Startup Ecosystem** | Funding, acquisitions, notable moves |
| 5 | **Big Tech AI Strategy** | Microsoft/Apple/Google/Meta makes an AI move |
| 6 | **Opinion & Hot Takes** | You have a strong contrarian or analytical take |

### Companies Tracked Out of the Box

ChatGPT / OpenAI · Claude / Anthropic · Gemini / Google DeepMind · Perplexity · ElevenLabs · Midjourney · Runway · Pika · Meta AI · xAI / Grok · Mistral · Cohere · Microsoft Copilot · Apple Intelligence · Amazon Bedrock · Nvidia · Salesforce Agentforce · Adobe Firefly · Hugging Face

Add or remove companies and keywords in `config/topics.yaml`.

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-30-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies matched, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` → `status: published` to track what's gone live.

---

## Setup

### 1. Copy the environment file

```bash
cp .env.example .env
```

### 2. Fill in your details

```bash
# Optional: Notion publishing
NOTION_PAGE_ID=your_32char_page_id

# Optional: NewsAPI for broader coverage
NEWSAPI_KEY=your_key
```

### 3. Personalise your brand

Edit these files before your first run:
- `config/brand_kit.yaml` → update `author.name`, `author.title`, `author.tagline`
- `config/tone_of_voice.md` → tweak voice rules to match how you actually write
- `config/content_pillars.md` → adjust pillars and angle starters to your focus

### 4. Run

```
Run the LinkedIn Post Generator pipeline.
```

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Output**: JSON array of scored article objects

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Output**: JSON array of 15–20 trending keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/tone_of_voice.md`, `config/content_pillars.md`, `config/experiments_log.md`
- **Output**: JSON object with filename, filepath, content, and source metadata

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Reads**: `.env` for `NOTION_PAGE_ID`
- **Output**: `success` or `failed`

---

## Adding Your Own AI Experiments

The "human in the loop" posts (Pillar 1) draw on `config/experiments_log.md`. Add an entry every time you test an AI tool on a real brief:

```markdown
## [DATE] — [Tool] × [Use Case]

**What I did:** [the brief or task]
**What actually happened:** [honest result]
**Standout moment:** [the specific thing worth sharing]
**Post potential:** Yes / Maybe / No
**Status:** Idea only / Draft written / Posted →
```

The post-generator checks for recent relevant experiments and weaves them into posts automatically.

---

## Adding News Sources

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```
