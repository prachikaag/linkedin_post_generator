# LinkedIn Post Generator

## What this project does

This is a multi-agent LinkedIn post generator. It:
1. Fetches AI news from RSS feeds and web search
2. Tracks trending keyword phrases
3. Generates research-backed LinkedIn post drafts in your voice
4. Optionally publishes drafts to Notion

No Python code — the pipeline runs entirely through Claude agent subagents.

## How to run

**Generate fresh posts:**
```
Run the LinkedIn Post Generator pipeline.
```

**Generate 3 posts with 5 sources each:**
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

**Dry-run (fetch news only, no post generation):**
```
Run the pipeline in dry-run mode.
```

The orchestrator is in `orchestrator.md`. Read it, then follow the steps it describes.

## Project structure

```
config/
  topics.yaml      ← edit to add/remove companies and keywords to track
  brand_kit.yaml   ← edit to set your name, tone, writing style, hashtags
  sources.yaml     ← edit to add/remove RSS feeds and news APIs

.claude/agents/
  news-gatherer.md      ← fetches + scores RSS articles
  trending-tracker.md   ← finds trending AI phrases via web search
  post-generator.md     ← writes LinkedIn posts using brand_kit.yaml
  notion-publisher.md   ← pushes drafts to Notion (optional)

orchestrator.md   ← top-level pipeline instructions; read this to run

posts/            ← generated post drafts saved here as .md files
.env.example      ← copy to .env and fill in NOTION_PAGE_ID to enable Notion
```

## First-time setup

1. Edit `config/brand_kit.yaml`:
   - Set `author.name`, `author.title`, `author.tagline`, `author.location`
   - Adjust tone traits if needed (they're pre-configured as a starting point)

2. Optionally set up Notion:
   - Copy `.env.example` to `.env`
   - Fill in `NOTION_PAGE_ID` (see `.env.example` for instructions)

3. Optionally add NewsAPI (more coverage):
   - Add `NEWSAPI_KEY` to `.env`
   - Set `enabled: true` in `config/sources.yaml` under `optional_apis.newsapi`

## Key config files

### topics.yaml
Controls what news gets tracked. Add companies or keywords to boost relevance scoring.
Every keyword match = +3 score (company) or +1 score (category).

### brand_kit.yaml
Controls how every post is written. The post-generator reads this on every run — no restart needed.
Key fields to personalise: `author.name`, `tone_of_voice.primary_traits`, `brand.hashtags`.

### sources.yaml
RSS feeds to fetch. Set `enabled: false` to skip a feed. Add any RSS URL you like.

## Output format

Posts are saved to `posts/YYYY-MM-DD_HH-MM-SS_slug.md` with YAML frontmatter:
- `status: draft` → change to `status: published` when you've posted it
- `all_sources` → the articles used to generate the post
- `matched_companies` / `matched_categories` → what triggered this article cluster

## Network note

If running in a restricted network environment (e.g. Claude Code cloud), RSS WebFetch
may be blocked. The agents will fall back to WebSearch automatically.
