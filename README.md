# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — in your voice, with your brand, citing real sources. Built entirely on Claude agents. No code to run.

---

## What it does

Each run:
1. Fetches fresh AI news from 20+ RSS feeds (company blogs, TechCrunch, VentureBeat, YouTube channels, and more)
2. Scores articles by relevance against your topics of interest
3. Searches the web for trending AI keyword phrases this week
4. Writes 1–3 LinkedIn draft posts in your tone of voice, citing real sources
5. Optionally saves drafts to a Notion page for review

The posts follow a fixed structure: hook → context → evidence → your take → so what → CTA → sources → hashtags.

If you've logged a personal AI experiment in `config/experiments.yaml` that's relevant to the news, the post weaves it in naturally — giving the "I've been testing this" voice that makes posts feel human, not just curated.

---

## How to run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude will read `orchestrator.md` and run the full pipeline.

### Variations

```
Run the LinkedIn Post Generator. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't write posts yet.
```

```
Run the pipeline. Use 8 articles per post cluster.
```

---

## Architecture

Everything is a markdown file. No Python. No servers. Just Claude agents passing data to each other.

```
orchestrator.md                        ← start here
├── .claude/agents/news-gatherer.md    ← fetches + scores RSS articles
├── .claude/agents/trending-tracker.md ← finds trending AI keyword phrases
├── .claude/agents/post-generator.md   ← writes + saves LinkedIn drafts
└── .claude/agents/notion-publisher.md ← publishes drafts to Notion (optional)
```

---

## Configuration files

All editable. Changes take effect on the next run — no restarts needed.

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Which companies, keywords, and topic categories to track. Also freshness settings (max article age, minimum relevance score). |
| `config/brand_kit.yaml` | Your name, title, tone of voice, writing style rules, post structure, hashtag strategy, and citation standards. |
| `config/sources.yaml` | Every RSS feed and API source. Add feeds, remove them, or set `enabled: false` to skip. |
| `config/experiments.yaml` | Your personal AI experiments log. The post-generator reads this and weaves in relevant personal experience when a news topic matches a tool you've tested. |

---

## Setup

### 1. Fill in your brand kit

Open `config/brand_kit.yaml` and update:
- `author.name` — your full name
- `author.title` — your LinkedIn headline / professional title
- `author.location` — your city and country

Everything else is already configured for an AI-curious brand strategist voice. Tweak the `tone_of_voice` and `brand` sections as you develop your own style.

### 2. Log your experiments

Open `config/experiments.yaml`. It comes pre-loaded with example entries for Claude, ChatGPT, Perplexity, ElevenLabs, Midjourney, and Gemini.

Edit them to match your actual experience. Add new tools as you test them. The post-generator only references experiments you've actually logged here — it won't invent experience you haven't had.

### 3. Configure Notion (optional)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then fill in:

```
NOTION_API_KEY=secret_xxx         # from notion.so/my-integrations
NOTION_PAGE_ID=32_char_page_id    # from your Notion page URL
```

If you skip this, posts are saved as `.md` files in `posts/` only.

### 4. Optional: add a NewsAPI key

A free key from [newsapi.org](https://newsapi.org/) gives you broader coverage beyond RSS. Add your key to `.env` and set `enabled: true` under `optional_apis.newsapi` in `config/sources.yaml`.

---

## Output

Generated posts land in `posts/` as markdown files:

```
posts/
  2026-05-14_10-30-00_openai-launches-new-reasoning-model.md
  2026-05-14_10-30-00_anthropic-funding-round-series-e.md
```

Each file has YAML frontmatter (metadata, sources, status) followed by the full post body.

Change `status: "draft"` to `status: "published"` to track what's gone live.

---

## Customising what gets covered

### Add a new company to track

Edit `config/topics.yaml` → `companies_to_track`. Copy an existing block and update the `name` and `keywords`.

### Add a news source

Edit `config/sources.yaml` → `rss_feeds`. Any RSS or Atom feed works:

```yaml
rss_feeds:
  ai_news:
    - name: "My Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

### Change how many posts are generated

When running: `Run the LinkedIn Post Generator. Generate 3 posts.`

Or edit the default `MAX_POSTS` in `orchestrator.md`.

### Change your writing style

Edit `config/brand_kit.yaml` → `tone_of_voice.writing_style`. Each bullet is an instruction the post-generator follows on every run.

### Add a personal experiment

Edit `config/experiments.yaml`. Copy the template block at the bottom, fill in your experience, and it'll be available to weave into future posts automatically.

---

## Agents reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Output**: JSON array of scored article objects

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml` (seed terms)
- **Output**: JSON array of 15–20 trending keyword phrases

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/experiments.yaml`
- **Output**: Saved `.md` draft + JSON result object

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Reads**: `.env` (NOTION_PAGE_ID)
- **Output**: `success` or `failed`
