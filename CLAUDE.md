# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks trending topics, and writes
research-backed LinkedIn post drafts in the author's brand voice.

## How to Run

### Inside Claude Code (agent mode — most powerful)
```
Run the LinkedIn Post Generator pipeline.
```
Claude reads `orchestrator.md` and spawns the four specialised subagents.

### As a standalone Python script
```bash
pip install -r requirements.txt
cp .env.example .env        # fill in ANTHROPIC_API_KEY (not needed inside Claude Code)
python run_pipeline.py      # generates 2 posts by default
```

Common flags:
```bash
python run_pipeline.py --max-posts 3          # generate 3 posts
python run_pipeline.py --dry-run              # score news only, skip post generation
python run_pipeline.py --no-notion            # skip Notion even if configured
```

## Project Layout

```
config/
  topics.yaml       ← companies, keywords, and freshness settings   (EDIT THIS)
  brand_kit.yaml    ← your voice, tone, post structure, hashtags     (EDIT THIS)
  sources.yaml      ← RSS feeds and news sources                     (EDIT THIS)

pipeline/
  news_fetcher.py   ← fetches RSS feeds with feedparser
  article_scorer.py ← scores articles by keyword relevance
  trending_tracker.py ← asks Claude for trending AI keywords
  post_generator.py ← generates LinkedIn post via Claude API
  notion_publisher.py ← publishes to Notion via REST API

.claude/agents/
  news-gatherer.md      ← Claude Code agent: RSS fetch + score
  trending-tracker.md   ← Claude Code agent: web search for trending topics
  post-generator.md     ← Claude Code agent: write + save post draft
  notion-publisher.md   ← Claude Code agent: publish to Notion

orchestrator.md   ← Claude Code orchestrator that chains all four agents
run_pipeline.py   ← standalone Python runner
```

## Editing the Config Files

All three config files are designed to be edited directly. Changes take effect on the next run.

### `config/topics.yaml`
- `companies_to_track` — add/remove companies and their search keywords
- `topic_categories` — scoring categories (funding, launches, regulation, etc.)
- `trending_keywords.seed_terms` — seed terms for the trending tracker
- `freshness` — `max_article_age_hours`, `min_relevance_score`, `max_articles_per_run`

### `config/brand_kit.yaml`
- `author` — your name, title, tagline
- `tone_of_voice.primary_traits` — how you come across
- `tone_of_voice.writing_style` — rules applied to every post
- `tone_of_voice.post_structure` — the ordered blueprint (hook → context → evidence → take → so what → CTA → sources → hashtags)
- `brand.hashtags` — always_include + rotate_from list
- `brand.post_length` and `brand.max_characters`

### `config/sources.yaml`
- Add any RSS/Atom feed: name, url, priority (high/medium/low), enabled (true/false)
- YouTube channel RSS feeds are supported (standard Atom format)
- `optional_apis.newsapi` — enable with `NEWSAPI_KEY` in .env for broader coverage

## Environment Variables (.env)

| Variable | Required | Purpose |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | Only outside Claude Code | Anthropic API key |
| `ANTHROPIC_MODEL` | No (default: claude-sonnet-4-6) | Claude model to use |
| `NOTION_PAGE_ID` | No | 32-char Notion page ID for publishing |
| `NOTION_API_KEY` | No | Notion Internal Integration Token |
| `NEWSAPI_KEY` | No | NewsAPI key for extra sources |

## Post Output Format

Posts are saved to `posts/` as markdown with YAML frontmatter:

```markdown
---
title: "Article headline"
date: "2024-01-15"
status: "draft"
primary_source_url: https://...
primary_source_name: TechCrunch AI
all_sources:
  - title: ...
    url: ...
    publication: ...
source_count: 6
matched_companies: [OpenAI, Anthropic]
matched_categories: [New AI Feature or Product Launch]
---

Post body here...
```

Change `status: draft` to `status: published` to track what's gone live.

## Agents Reference (Claude Code mode)

| Agent | Tools | Does |
|-------|-------|------|
| `news-gatherer` | Read, WebFetch | Fetches RSS, scores articles, returns JSON array |
| `trending-tracker` | Read, WebSearch | Finds trending AI keyword phrases via web search |
| `post-generator` | Read, Write | Writes branded post, saves as .md draft |
| `notion-publisher` | Read, Notion MCP | Appends post as toggle block on Notion page |
