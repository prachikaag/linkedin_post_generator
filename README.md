# LinkedIn Post Generator

Automatically finds trending AI news, matches it to your topics of interest, and drafts LinkedIn posts in your voice — all ready for your review before publishing.

You are always in the loop. The tool drafts, you decide what ships.

## What it does

1. **Reads your topics file** (`config/topics.yaml`) — companies, keywords, and categories you care about
2. **Fetches news** from curated RSS feeds (TechCrunch, VentureBeat, company blogs, YouTube channels, newsletters)
3. **Scores articles** by relevance to your tracked companies and topic categories
4. **Pulls trending keywords** to understand what people are searching
5. **Generates draft posts** via Claude, following your brand kit and tone of voice exactly
6. **Saves drafts** as markdown files in `/posts/` for you to review, edit, and publish

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key (skip if running inside Claude Code — it's automatic)
cp .env.example .env
# Edit .env and paste your ANTHROPIC_API_KEY

# 3. Personalise your config — do this before the first run
#    config/brand_kit.yaml  → your name, tone of voice, writing style
#    config/topics.yaml     → companies and topics to track
#    config/sources.yaml    → add/remove RSS feeds
```

### Fill in your brand kit

Open `config/brand_kit.yaml` and update the `author` section with your details:

```yaml
author:
  name: "Prachi Kaag"                  # ← your name
  title: "Brand Strategist | AI"       # ← your LinkedIn headline
  tagline: "Helping brands leverage AI in the real world"
```

Everything else in the file controls your tone, writing style, and hashtags — read through it and tweak to match how you actually write.

## Usage

### Run the full pipeline (recommended for daily/weekly use)

```bash
# Generate up to 3 posts from today's top AI news
python main.py run

# Generate up to 5 posts
python main.py run --max-posts 5

# See what news would be picked without generating posts
python main.py run --dry-run
```

### Write a post on a specific topic (most flexible)

Spotted a story you want to react to? Heard about a launch? Use this:

```bash
# Search for recent articles on a topic and generate a post
python main.py write-post --topic "Claude 4 launch"
python main.py write-post --topic "ElevenLabs new voice feature"
python main.py write-post --topic "AI startup funding Series B"

# Paste in a specific article URL — it fetches the article and finds related sources
python main.py write-post --url "https://techcrunch.com/2025/..."
```

### Manage your drafts

```bash
# List all saved draft posts
python main.py list-posts

# Read a specific draft
python main.py show 1
python main.py show --file posts/2025-04-28_openai-launches.md

# Mark a post as published once you've posted it on LinkedIn
python main.py mark-published 1

# Show paths to all editable config files
python main.py config
```

## Customise everything

| File | What it controls |
|------|-----------------|
| `config/brand_kit.yaml` | Your name, tone of voice, writing style, post types, hashtags, post length |
| `config/topics.yaml` | Companies to track, topic categories, trending keyword seeds |
| `config/sources.yaml` | RSS feeds, YouTube channels, newsletters, optional NewsAPI |
| `.env` | API keys and model selection |

### Content types in your brand kit

The brand kit defines five post types you rotate through:

| Type | When to use |
|------|------------|
| **Personal Experiment** | "I tried X for Y — here's what happened" |
| **News Reaction** | Reacting to a launch, feature, or announcement |
| **Funding Signal** | AI startup raised money — what does it signal? |
| **Trend Analysis** | Connecting dots across multiple developments |
| **How Brands Can Use It** | Practical breakdown for marketers |

## Generated posts

Posts are saved in `posts/` as markdown files with YAML frontmatter:

```
posts/
  2025-04-28_10-30-00_claude-4-launches.md
  2025-04-28_10-30-05_elevenlabs-raises-series-b.md
```

Each file contains the draft post plus metadata (source URLs, matched companies, trending keywords, relevance score). Edit the file directly, then copy the post to LinkedIn when ready.

Run `python main.py mark-published 1` to mark a post as published and keep your archive clean.

## Adding news sources

Edit `config/sources.yaml` to add any RSS feed or YouTube channel:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high     # high | medium | low
      enabled: true
```

YouTube channels work the same way — use the YouTube RSS format:

```yaml
  youtube_channels:
    - name: "Channel Name"
      url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE"
      priority: medium
      enabled: true
```

Find a channel's ID by visiting their YouTube page and inspecting the page source for `channelId`.

## Optional integrations

### NewsAPI (broader news coverage)

Get a free key at [newsapi.org](https://newsapi.org/), add `NEWSAPI_KEY=your_key` to `.env`, and set `enabled: true` under `optional_apis.newsapi` in `config/sources.yaml`.

### Notion (push drafts to your Notion workspace)

1. Create an internal integration at [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Add the token and your page ID to `.env`
3. Posts are automatically pushed to Notion after each run
