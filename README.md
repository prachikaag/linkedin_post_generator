# LinkedIn Post Generator

An AI-powered pipeline that watches AI news, tracks what's trending, and writes research-backed LinkedIn post drafts in your voice.

Built for people who want to be part of the AI conversation — not just observers.

---

## What It Does

1. **Reads your topics** (`config/topics.yaml`) — the AI companies, products, and themes you care about
2. **Fetches fresh news** from 20+ RSS feeds: TechCrunch, The Verge, company blogs, YouTube channels, and more
3. **Scores articles** for relevance: company keyword match (+3), topic category match (+1)
4. **Finds trending keywords** via Google Trends (falls back gracefully if unavailable)
5. **Writes LinkedIn posts** via Claude — synthesising multiple articles into one opinionated take
6. **Saves drafts** to `posts/` as markdown files you can review, edit, and publish
7. **Publishes to Notion** (optional) — posts appear as collapsible toggle blocks on your content page

---

## Architecture

Two ways to run — pick one or use both:

```
Option A: Python runner (scheduled, automated)
──────────────────────────────────────────────
python main.py
    └── src/config_loader.py      → loads all YAML config + env vars
    └── src/news_fetcher.py       → RSS fetching + keyword scoring
    └── src/trending_tracker.py   → Google Trends keyword discovery
    └── src/post_generator.py     → Claude API post writing + file saving
    └── src/notion_publisher.py   → Notion toggle block publishing

Option B: Claude Code agents (interactive, inside Claude Code)
──────────────────────────────────────────────────────────────
orchestrator.md
    └── .claude/agents/news-gatherer.md     → fetches + scores RSS articles
    └── .claude/agents/trending-tracker.md  → finds trending phrases via WebSearch
    └── .claude/agents/post-generator.md    → writes + saves LinkedIn drafts
    └── .claude/agents/notion-publisher.md  → publishes drafts to Notion
```

---

## Quick Start

### 1. Clone and install

```bash
pip install -r requirements.txt
```

### 2. Fill in your brand

Edit `config/brand_kit.yaml` — replace the placeholder values at the top:

```yaml
author:
  name: "Your Name"        # e.g. "Prachi Kaag"
  title: "Your Title"      # e.g. "Brand Strategist & AI Experimenter"
  tagline: "..."           # your LinkedIn tagline
```

### 3. Set your API key

Copy `.env.example` to `.env` (already done) and add your Anthropic key:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

Get a key at [console.anthropic.com](https://console.anthropic.com/).

### 4. Run

```bash
# Generate 2 posts (default)
python main.py

# Generate 3 posts
python main.py --max-posts 3

# Preview what news was found — no posts generated
python main.py --dry-run

# Generate posts but skip Notion
python main.py --skip-notion
```

Posts are saved to `posts/` as `.md` files. Open them, review, edit, then paste into LinkedIn.

---

## Configuration Files

All behaviour is controlled by three YAML files — no code changes needed:

| File | What to edit |
|------|-------------|
| `config/brand_kit.yaml` | Your name, tone, writing rules, hashtags, post length |
| `config/topics.yaml` | Companies to track, topic categories, freshness settings |
| `config/sources.yaml` | RSS feeds, company blogs, YouTube channels |

### brand_kit.yaml — your voice

The most important file. It controls:
- **`author`** — your name, title, and tagline (injected into every prompt)
- **`tone_of_voice.primary_traits`** — the personality of your posts
- **`tone_of_voice.writing_style`** — hard rules for every sentence
- **`tone_of_voice.post_structure`** — hook → context → evidence → your take → so what → CTA → sources → hashtags
- **`brand.hashtags`** — always-include and rotate-from hashtag lists
- **`research_standards.min_sources`** — minimum cited sources per post (default: 4)

### topics.yaml — what you track

Three sections:
- **`companies_to_track`** — AI labs, builders, and big tech companies with keyword lists
- **`topic_categories`** — themes like "AI Startup Funding" or "New AI Feature Launch"
- **`trending_keywords`** — seed terms for Google Trends discovery
- **`freshness`** — max article age (hours), minimum relevance score, max articles per run

To add a company:
```yaml
ai_labs:
  - name: "Your New Company"
    keywords:
      - "company name"
      - "product name"
```

### sources.yaml — where to fetch news

Add any RSS feed:
```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Feed"
      url: "https://example.com/feed.xml"
      priority: high    # high / medium / low
      enabled: true
```

---

## Notion Setup (optional)

Posts can be automatically pushed to a Notion page as collapsible toggle blocks.

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → **New integration** (Internal)
2. Copy the **Internal Integration Token** → paste as `NOTION_API_KEY` in `.env`
3. Open your LinkedIn Post Ideas Notion page
4. Click `...` → **Connections** → connect your integration
5. Copy the **32-character page ID** from the URL → paste as `NOTION_PAGE_ID` in `.env`

Leave both blank to skip Notion — posts save as `.md` files only.

---

## Running Inside Claude Code

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with custom parameters:

```
Run the LinkedIn Post Generator. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only.
```

Claude will execute `orchestrator.md`, which spawns the four subagents in sequence.

---

## Output

Each generated post is saved as:

```
posts/2026-06-03_14-30-00_openai-launches-new-feature.md
```

The file contains:
- **YAML frontmatter** — source metadata, matched companies, categories, status
- **Post body** — full LinkedIn draft with sources list and hashtags

Change `status: "draft"` to `status: "published"` to track what's gone live.

---

## Automating with a Cron Job

Run daily at 8am:

```bash
# Edit your crontab
crontab -e

# Add this line (adjust the path)
0 8 * * * cd /path/to/linkedin_post_generator && python main.py >> logs/run.log 2>&1
```

Or as a GitHub Actions workflow — create `.github/workflows/generate.yml` and trigger on schedule.

---

## Post Examples

See `posts/` for example outputs. The pipeline generates posts like:

> *Something shifted in enterprise AI this week. It's bigger than any one announcement.*
>
> *The pattern isn't one company doing well. It's the whole market committing...*

Each post synthesises 4–6 articles into one opinionated take with cited sources.
