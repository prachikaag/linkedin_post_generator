# LinkedIn Post Generator

An AI-powered pipeline that monitors trending AI news, tracks what's buzzing, and writes
research-backed LinkedIn draft posts in your voice — using Claude agents and subagents.
No code to run. Just configure and go.

---

## What It Does

1. **Fetches fresh AI news** from ~20 RSS feeds and company blogs (TechCrunch, VentureBeat,
   OpenAI, Anthropic, DeepMind, YouTube channels, funding sources, and more)
2. **Scores articles by relevance** against your tracked companies and topic categories
3. **Finds what's trending** — searches for the most-discussed AI topics from the past 7 days
4. **Generates LinkedIn posts** in your voice, with cited sources, following your brand kit and
   tone of voice — including your personal experiments and opinions
5. **Saves drafts** as markdown files in `posts/` — ready for you to review, tweak, and post
6. **Optionally publishes to Notion** if you have a Notion integration configured

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude will read `orchestrator.md` and execute the full pipeline automatically.

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Architecture

The pipeline is a multi-agent system. The orchestrator spawns specialised subagents and passes
data between them:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending AI keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file. The orchestrator passes JSON between them.

---

## Configuration Files

All settings live in `config/`. Edit these files — changes take effect on the next run.

| File | What it Controls | Edit When |
|------|-----------------|-----------|
| `config/topics.yaml` | Which companies and keywords to track, freshness settings | You want to add/remove companies or topics |
| `config/sources.yaml` | RSS feeds, YouTube channels, and API sources | You want new news sources |
| `config/brand_kit.yaml` | Post structure rules, hashtags, length, citation standards | You want to change post format rules |
| `config/tone_of_voice.md` | How you write — voice, rhythm, banned words, the "human in the loop" requirement | You want to adjust writing style |
| `config/personal_context.yaml` | Your AI experiments, signature opinions, open questions, client patterns | You try new tools or want posts to reflect new thinking |

### The most important file to keep updated: `personal_context.yaml`

This is what makes posts sound like you instead of a generic AI summary. Update it when:
- You try a new AI tool — add it to `current_experiments` with what you found
- You form a new opinion — add it to `signature_opinions`
- You notice a pattern in your work — add it to `patterns_from_client_work`

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `NOTION_PAGE_ID` | Optional | Pushes post drafts to your Notion page |
| `NOTION_API_KEY` | Optional | Direct Notion REST API fallback |
| `NEWSAPI_KEY` | Optional | Broader news coverage (free at newsapi.org) |
| `ANTHROPIC_API_KEY` | Optional | Only needed outside Claude Code |

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-35-00_anthropic-funding-round.md
```

Each file contains YAML frontmatter (metadata, sources, status) followed by the full post body.

Change `status: draft` to `status: published` to track what's gone live.

---

## Tracking What You've Covered

The frontmatter in each post file logs:
- `matched_companies` — which AI companies the post covers
- `matched_categories` — topic category (funding, product launch, research, etc.)
- `all_sources` — every article used with full URLs
- `status` — `draft` or `published`

This lets you scan `posts/` to see what you've already written about before running again.

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/tone_of_voice.md`, `config/personal_context.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post in your voice, with personal context layered in, saves as `.md` draft

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page

---

## Adding News Sources

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

YouTube channels work via RSS too — any YouTube channel has a feed at:
`https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`

---

## Customising Your Voice

The three files that shape how posts sound are read fresh on every run:

1. **`config/tone_of_voice.md`** — narrative guide in plain English. Edit it like a document.
   Change the banned words list, add new rhythm rules, adjust the "human in the loop" requirement.

2. **`config/brand_kit.yaml`** — structural rules. Change post length, number of hashtags,
   minimum sources required, your name and title.

3. **`config/personal_context.yaml`** — personal experiments and opinions. This is the most
   important one to keep current. Update it every time you try a new tool or form a new view.
