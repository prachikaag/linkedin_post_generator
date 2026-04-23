# LinkedIn Post Generator

Monitors AI news across RSS feeds and Google News, checks what's trending, and uses Claude to write on-brand LinkedIn posts with cited sources — all shaped by your personal tone of voice and brand kit.

## How it works

```
config/topics.yaml      → what to track (AI companies, categories, keywords)
config/sources.yaml     → where to look (RSS feeds, NewsAPI)
config/brand_kit.yaml   → how to sound (tone, structure, hashtags, examples)
        ↓
src/news_fetcher.py     → pulls & filters articles from all sources
src/trending_tracker.py → checks Google Trends for relevant keywords
src/post_generator.py   → calls Claude to write posts in your voice
src/orchestrator.py     → runs the full pipeline end-to-end
        ↓
outputs/posts_TIMESTAMP.md   → ready-to-copy LinkedIn posts
outputs/run_TIMESTAMP.json   → full run data (articles, trends, posts)
```

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create your .env file
cp .env.example .env
# Then add your ANTHROPIC_API_KEY (and optionally NEWSAPI_KEY)
```

## Usage

```bash
# Full pipeline: fetch news + trends → generate 3 posts
python main.py

# Generate 5 posts instead of 3
python main.py --posts 5

# Skip Google Trends (faster, uses keywords from topics.yaml directly)
python main.py --no-trends

# Fetch news only — no Claude call
python main.py --dry-run

# Re-process articles you've already seen
python main.py --no-skip-seen

# Only fetch and list today's news
python main.py fetch

# Only show what's trending on Google
python main.py trends
```

## Customising the three config files

### `config/topics.yaml` — *What to track*
- Add or remove AI companies, adjust their keyword lists
- Edit categories (product launches, funding, research, etc.)
- Update `priority_keywords` to always surface certain topics
- Add to `exclude_keywords` to filter out noise

### `config/brand_kit.yaml` — *How to sound*
- Edit `persona` with your real name and positioning
- Adjust `tone.descriptors` to shift the writing style
- Modify `post_structure` to change length, hooks, or closings
- Update `hashtags` with your preferred tags
- Add your own `example_posts` to steer the model's style

### `config/sources.yaml` — *Where to look*
- Add RSS feed URLs for any publication
- Toggle `newsapi.enabled` on/off
- Add Google News query URLs for specific searches
- Adjust `fetch_settings.max_article_age_days` (default: 7 days)

## Output

Each run saves two files in `outputs/`:
- `posts_TIMESTAMP.md` — the LinkedIn posts, ready to copy
- `run_TIMESTAMP.json` — full data (articles, trends, posts) for auditing

`data/seen_articles.json` tracks which articles have already been processed so you don't get duplicates across runs.

## API Keys

| Key | Where to get it | Required? |
|-----|----------------|-----------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/) | Yes |
| `NEWSAPI_KEY` | [newsapi.org](https://newsapi.org/) — free tier: 100 req/day | No (RSS feeds work without it) |
