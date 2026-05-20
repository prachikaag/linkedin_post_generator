# LinkedIn Post Generator

An agentic pipeline that monitors AI news, tracks trending keywords, and drafts research-backed LinkedIn posts in your personal brand voice.

---

## Running the Pipeline

When the user asks to generate LinkedIn posts, **read `orchestrator.md` and execute every step in order**, spawning the subagents it describes.

Common triggers and their parameters:

| User says | What to do |
|-----------|-----------|
| "generate my LinkedIn posts" | Run full pipeline, `MAX_POSTS=2` |
| "generate [N] post(s)" | Run full pipeline, `MAX_POSTS=N` |
| "dry run" | Run Steps 1–2 only (`DRY_RUN=true`), print scored articles |
| "reset seen articles" | Write `{"seen_urls": []}` to `data/seen_articles.json` |

After every successful full run: **commit `data/seen_articles.json`** so the deduplication memory persists across sessions.

---

## Project Structure

```
├── CLAUDE.md                    ← you are here
├── orchestrator.md              ← full pipeline instructions
├── config/
│   ├── brand_kit.yaml           ← tone of voice, writing rules, hashtags
│   ├── topics.yaml              ← companies, keywords, topic categories
│   └── sources.yaml             ← RSS feeds and optional API sources
├── .claude/agents/
│   ├── news-gatherer.md         ← fetches + scores articles from RSS feeds
│   ├── trending-tracker.md      ← finds trending AI keywords via web search
│   ├── post-generator.md        ← writes posts following brand_kit.yaml
│   └── notion-publisher.md      ← publishes drafts to Notion (optional)
├── data/
│   └── seen_articles.json       ← URLs already used (prevents duplicates across runs)
└── posts/                       ← generated .md draft files
```

---

## Configuration Files

All configuration lives in `config/` and `data/` — the user edits these, not the code.

### `config/brand_kit.yaml` — Edit this first
- `author` block: fill in your name, title, tagline
- `tone_of_voice`: writing rules and post structure (already opinionated — tweak as needed)
- `brand.hashtags`: always-include tags and rotation pool
- `brand.post_length`: `"short"` / `"medium"` / `"long"`

### `config/topics.yaml` — What news to track
- `companies_to_track`: AI labs, builders, big tech — each with keyword lists
- `topic_categories`: scoring categories (launch, funding, research, etc.)
- `trending_keywords.seed_terms`: seed phrases for the trending-tracker
- `freshness`: age cutoff, relevance threshold, max articles per run

### `config/sources.yaml` — Where to fetch news from
- `rss_feeds`: enabled/disabled feeds by section (ai_news, company_blogs, funding_news, youtube_channels)
- `optional_apis.newsapi`: set `enabled: true` after adding `NEWSAPI_KEY` to `.env`

### `.env` — API keys
- `NOTION_PAGE_ID`: 32-char ID from the Notion page URL — enables Notion publishing
- `NEWSAPI_KEY`: optional, broadens news coverage beyond RSS

### `data/seen_articles.json` — Deduplication memory
Format: `{"seen_urls": ["https://...", ...]}`. Grows automatically each run. To reset, write `{"seen_urls": []}`.

---

## First-Time Setup

1. `cp .env.example .env` — fill in any API keys you want
2. Open `config/brand_kit.yaml` — replace `author.name`, `author.title`, `author.tagline` with your real details
3. (Optional) Add your Notion page ID to `.env`
4. Say: "Generate my LinkedIn posts"

---

## Output

Each run saves drafts to `posts/` as markdown files with YAML frontmatter:
```
posts/YYYY-MM-DD_HH-MM-SS_<slug>.md
```
Frontmatter tracks: title, date, all source URLs, matched companies, relevance score, status (`draft`).

If Notion is configured, drafts also appear as toggle blocks on your Notion page.
