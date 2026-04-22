# LinkedIn Post Generator

Automatically finds trending AI news, matches it to your topics of interest, and drafts LinkedIn posts in your voice — all ready for your review before publishing.

## How it works

1. **Fetches news** from curated RSS feeds (TechCrunch, VentureBeat, company blogs, etc.)
2. **Scores articles** by relevance to your tracked companies and topic categories
3. **Pulls trending keywords** from Google Trends to understand what people are searching
4. **Generates draft posts** via Claude, following your brand kit and tone of voice exactly
5. **Saves drafts** as markdown files in `/posts/` for you to review, edit, and publish

You are always in the loop — the tool drafts, you decide what ships.

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key
cp .env.example .env
# Edit .env and paste your ANTHROPIC_API_KEY

# 3. Personalise your config (do this before first run)
#    - config/brand_kit.yaml  → your name, tone, writing style
#    - config/topics.yaml     → companies and topics to track
#    - config/sources.yaml    → add/remove RSS feeds
```

## Usage

```bash
# Generate up to 3 posts from today's top AI news
python main.py run

# Generate up to 5 posts
python main.py run --max-posts 5

# See what news would be picked without generating posts
python main.py run --dry-run

# List all saved draft posts
python main.py list-posts

# Read a specific draft
python main.py show 1

# Show paths to all config files
python main.py config
```

## Customise Everything

| File | What it controls |
|------|-----------------|
| `config/brand_kit.yaml` | Your name, tone of voice, writing style, hashtags, post length |
| `config/topics.yaml` | Companies to track, topic categories, trending keyword seeds |
| `config/sources.yaml` | RSS feeds and optional NewsAPI queries |
| `.env` | API keys and model selection |

## Generated Posts

Posts are saved in `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-new-model.md
  2024-01-15_10-30-05_elevenlabs-raises-series-b.md
```

Each file contains the draft post plus metadata (source URL, matched companies, trending keywords, relevance score). Edit the file directly, then copy the post to LinkedIn when ready. Change `status: draft` to `status: published` to keep track.

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

## Optional: NewsAPI

For broader news coverage, get a free key at [newsapi.org](https://newsapi.org/), add it to `.env`, and set `enabled: true` under `optional_apis.newsapi` in `config/sources.yaml`.
