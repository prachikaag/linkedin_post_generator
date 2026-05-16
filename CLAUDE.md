# LinkedIn Post Generator

Automated pipeline that tracks AI news, identifies trending topics, and generates LinkedIn posts in your brand voice — with cited sources — ready for review and publishing.

## How to run

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in your API keys
cp .env.example .env

# Generate up to 2 posts (default)
python run_pipeline.py

# Generate 3 posts with a 8-article cluster per post
python run_pipeline.py --max-posts 3 --pool-size 8

# Preview what news is available without generating posts
python run_pipeline.py --dry-run

# Generate without publishing to Notion
python run_pipeline.py --no-notion
```

## Editable config files

All behaviour is controlled by three YAML files in `config/`. Edit them freely.

### `config/topics.yaml`
Controls what gets tracked and scored.
- `companies_to_track` — add/remove companies and their keywords
- `topic_categories` — labels used to score article relevance
- `trending_keywords.seed_terms` — seed phrases for Google Trends
- `freshness` — age limit, minimum relevance score, max articles per run

### `config/brand_kit.yaml`
Controls how posts are written.
- `author` — your name and title (shown in every post)
- `tone_of_voice.primary_traits` — your personality as a writer
- `tone_of_voice.writing_style` — rules applied to every sentence
- `tone_of_voice.post_structure` — the exact HOOK → CTA blueprint
- `tone_of_voice.dos` / `donts` — what to do and avoid
- `brand.focus_areas` — the lenses you write through
- `brand.hashtags` — always-included tags + rotation pool
- `brand.max_hashtags`, `max_characters`, `max_words` — hard limits

### `config/sources.yaml`
Controls where news is fetched from.
- `rss_feeds` — feeds grouped by `ai_news`, `company_blogs`, `funding_news`, `youtube_channels`
- Set `enabled: false` on any feed to pause it without deleting it
- Set `priority: high/medium/low` — high-priority feeds are fetched first
- `optional_apis.newsapi` — enable by setting `enabled: true` and adding `NEWSAPI_KEY` to `.env`

## Environment variables (`.env`)

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key |
| `ANTHROPIC_MODEL` | No | `sonnet` (default), `opus`, or `haiku` |
| `NOTION_API_KEY` | No | Notion integration token for auto-publishing |
| `NOTION_PAGE_ID` | No | 32-char Notion page ID to append posts to |
| `NEWSAPI_KEY` | No | NewsAPI.org key for extra article sources |

## Output

Generated posts land in `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-05-16_10-30-00_openai-launches-gpt5.md
```

Each file contains:
- **Frontmatter** — title, date, source URLs, matched companies, categories, relevance score, status (`draft`)
- **Post body** — ready-to-copy LinkedIn post

Change `status: "draft"` to `status: "published"` manually after you post.

## Claude Code agent mode

Run the full pipeline via Claude Code orchestration instead of Python:

```
/run-pipeline
```

This uses the agent definitions in `.claude/agents/`:
- `news-gatherer.md` — fetches and scores RSS feeds
- `trending-tracker.md` — web searches for trending AI topics
- `post-generator.md` — writes the post following the brand kit
- `notion-publisher.md` — appends to Notion
- `orchestrator.md` — coordinates all agents and summarises results

## Pipeline steps

1. **News Gatherer** — Fetches enabled RSS feeds, scores each article by keyword matches (+3 per company keyword, +1 per category keyword), deduplicates, and returns the top 25 articles
2. **Trending Tracker** — Queries Google Trends for rising AI searches; falls back to a curated list if rate-limited
3. **Post Generator** — Clusters articles around the highest-scoring anchor, calls Claude with the brand kit as a cached system prompt, streams the post, and saves it to `posts/`
4. **Notion Publisher** — Appends a collapsible toggle block to your Notion page (optional)
