# LinkedIn Post Generator

This project generates research-backed LinkedIn post drafts by fetching AI news, tracking trending keywords, and writing branded posts aligned to your voice and brand kit.

---

## How to Run

To generate new LinkedIn post drafts, say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude will read `orchestrator.md` and execute the full pipeline automatically.

### Custom runs

```
Run the LinkedIn Post Generator. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch news only, don't generate posts.
```

```
Run the pipeline and push drafts to Notion.
```

---

## Project Structure

```
linkedin_post_generator/
├── config/
│   ├── topics.yaml        ← Companies, keywords, and freshness settings
│   ├── brand_kit.yaml     ← Your voice, tone, writing style, and hashtag rules
│   └── sources.yaml       ← RSS feeds and news sources to fetch from
├── .claude/
│   └── agents/
│       ├── news-gatherer.md       ← Fetches + scores RSS articles
│       ├── trending-tracker.md    ← Finds trending keyword phrases via web search
│       ├── post-generator.md      ← Writes + saves LinkedIn post drafts
│       └── notion-publisher.md    ← Publishes drafts to Notion (optional)
├── posts/                 ← Generated .md draft posts saved here
├── orchestrator.md        ← Master pipeline definition
└── .env.example           ← Environment variables template
```

---

## First-Time Setup

### 1. Personalise your brand kit

Edit `config/brand_kit.yaml` and fill in:
- `author.name` — your name
- `author.title` — your professional title
- `author.tagline` — your LinkedIn headline
- `author.location` — your city and country

The tone of voice, post structure, and writing rules are pre-configured with strong defaults. Adjust them to match your style.

### 2. Customise your topics

Edit `config/topics.yaml` to:
- Add or remove companies to track under `companies_to_track`
- Adjust topic categories under `topic_categories`
- Change freshness settings (how old articles can be, minimum relevance score)

### 3. Enable Notion publishing (optional)

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Fill in:
- `NOTION_PAGE_ID` — the 32-character page ID from your Notion "LinkedIn Post Ideas" page
- `NOTION_API_KEY` — your Notion internal integration token (only needed for standalone use outside Claude Code)

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2026-10-26_14-00-00_openai-launches-gpt6.md
  2026-10-26_14-00-00_anthropic-funding-round.md
```

Each file has:
- **YAML frontmatter** — source metadata, matched companies, categories, status
- **Post body** — the full LinkedIn draft, ready to review and publish

Change `status: draft` → `status: published` to track what's gone live.

---

## Quick Edits

| Goal | Edit |
|------|------|
| Add a news source | Add entry in `config/sources.yaml` |
| Track a new company | Add entry in `config/topics.yaml` under `companies_to_track` |
| Change post length | Edit `brand.post_length` in `config/brand_kit.yaml` |
| Change hashtags | Edit `brand.hashtags` in `config/brand_kit.yaml` |
| Generate more posts per run | Say "Generate 3 posts" when running |
| Adjust freshness window | Edit `freshness.max_article_age_hours` in `config/topics.yaml` |

---

## Pipeline Flow

```
[news-gatherer]     ──→  scored articles JSON
[trending-tracker]  ──→  trending keywords JSON
         ↓
[post-generator]    ──→  saved .md draft in posts/
         ↓ (if NOTION_PAGE_ID is set)
[notion-publisher]  ──→  toggle block appended to Notion page
```
