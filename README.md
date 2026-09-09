# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents.

**Goal:** Show you're following news in AI and have a clear opinion on how brands can leverage it — with real experiments, cited sources, and your own voice.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/memory-tracker.md     → filters already-covered articles, updates history
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → identifies post type, writes & saves drafts
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
2. Spawns **memory-tracker** → filters out articles already covered in previous posts
3. Spawns **trending-tracker** → searches trending AI topics via WebSearch
4. For each article cluster, spawns **post-generator** → identifies the post type, writes and saves a draft
5. Spawns **memory-tracker** → records new post URLs in memory (deduplication)
6. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration — Edit These Files

All settings live in `config/`. **These are the files you'll customise most often.**

| File | What to edit |
|------|-------------|
| `config/brand_kit.yaml` | **Your name, title, tone, writing style, post types, hashtags** |
| `config/topics.yaml` | **Companies, keywords, and topic categories to track** |
| `config/sources.yaml` | **RSS feeds and API sources to fetch news from** |

Edit these files directly — changes take effect on the next run.

---

## Configuration Deep Dive

### `config/brand_kit.yaml` — Your Voice & Brand

**Fill in first:**
```yaml
author:
  name: "Your Name"       # Your first name or full name
  title: "Your Title"     # Your LinkedIn title
  tagline: "..."          # One-line positioning
  location: "City, Country"
```

**Post types** — the pipeline picks the right one automatically based on the news:
| Type | When it triggers |
|------|-----------------|
| `feature_launch` | A new model, feature, or tool launches |
| `youtube_reaction` | An AI company ships a YouTube demo or keynote |
| `funding_decoded` | A startup announces funding, acquisition, or IPO |
| `human_in_the_loop` | Firsthand AI experiments or real workflow stories |
| `bigtech_ai_move` | Microsoft, Google, Apple, Amazon, Meta, etc. makes an AI move |
| `ai_experiment` | Real-world AI adoption stories from practitioners |

**Tone traits** you already have baked in:
- Curious and experimental — you try AI tools and share honest results
- Pragmatic and brand-focused — you connect AI news to real outcomes
- Accessible, not overly technical
- Opinionated — clear point of view, not a neutral summary
- Human in the loop — always the editor, AI is always the drafter

---

### `config/topics.yaml` — What Gets Tracked

**Companies tracked by default:**

*AI Labs:* OpenAI (ChatGPT, GPT-5, Sora, Operator), Anthropic (Claude, MCP), Google DeepMind (Gemini, NotebookLM, Veo), Perplexity, ElevenLabs, Midjourney, Stability AI, xAI (Grok), Meta AI (LLaMA), Mistral, Runway, Pika Labs, Suno, Udio, Synthesia, Luma AI, Kling AI, HuggingFace

*AI Builders:* Cerebras, Groq, Harvey AI, Cognition/Devin, Scale AI, Writer, Glean, Cursor, Windsurf, Replit, Gamma, Descript, Heygen, Ideogram

*Big Tech:* Microsoft, Apple, Amazon, Nvidia, Salesforce, Adobe, Notion, Canva

**Topic categories tracked:**
- New AI Feature or Product Launch
- YouTube Video or Demo Launch ← distinct category, not just an article type
- AI Startup Funding
- AI for Marketing and Brands
- Human in the Loop / AI Experimentation
- AI Research and Breakthroughs
- AI Regulation and Policy
- AI Tools and Productivity

---

### `config/sources.yaml` — Where News Comes From

**RSS feeds included:**
- AI news: TechCrunch, The Verge, VentureBeat, Wired, MIT Tech Review, Ars Technica, CNBC
- Company blogs: OpenAI, Anthropic, Google AI, DeepMind, Meta AI, Microsoft, HuggingFace, Mistral, Perplexity, ElevenLabs
- Startup & funding: TechCrunch Startups, Crunchbase, SiliconAngle
- YouTube channels: Google DeepMind, OpenAI, Anthropic, Two Minute Papers

To add a new source:
```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high   # high | medium | low
      enabled: true
```

---

## Memory System

The pipeline tracks every article URL and topic it's used in a post at `data/published_articles.json`.

On each run, before generating posts, the memory-tracker removes articles already covered in previous runs. This means:
- No duplicate posts about the same story
- The pipeline always surfaces genuinely new news
- History accumulates automatically — no manual management needed

To reset memory (force re-generation on older articles), clear `data/published_articles.json`:
```json
{
  "_comment": "...",
  "last_updated": "",
  "published_urls": [],
  "published_topics": [],
  "post_history": []
}
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

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON

### `memory-tracker`
- **Tools**: Read, Write
- **Reads/Writes**: `data/published_articles.json`
- **Does (filter mode)**: Removes articles already covered in previous posts from the pool
- **Does (update mode)**: Records article URLs and topics from new posts into memory

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`
- **Does**: Identifies the best post type for the article cluster, synthesises sources into a branded LinkedIn post, validates URLs, saves as `.md` draft

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# Required for Notion publishing (optional feature)
NOTION_PAGE_ID=your_32char_page_id_here
NOTION_API_KEY=secret_xxx

# Optional: NewsAPI for additional sources
NEWSAPI_KEY=your_key_here
```

---

## Quick-Start Checklist

- [ ] Open `config/brand_kit.yaml` → fill in `author.name`, `author.title`, `author.tagline`, `author.location`
- [ ] Open `config/topics.yaml` → add or remove companies and keywords you care about
- [ ] Open `config/sources.yaml` → add any custom RSS feeds
- [ ] (Optional) Add `NOTION_PAGE_ID` to `.env` to push drafts to Notion automatically
- [ ] Say **"Run the LinkedIn Post Generator pipeline"** in Claude Code
- [ ] Review drafts in `posts/`, edit as needed, then publish
