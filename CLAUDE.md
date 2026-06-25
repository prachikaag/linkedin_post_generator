# LinkedIn Post Generator

An AI-powered pipeline that tracks AI news, finds what's trending, and writes research-backed LinkedIn drafts — in your voice, with cited sources, ready to review and publish.

---

## How to Run

Say one of these to Claude:

```
Run the LinkedIn Post Generator pipeline.
```
```
Run the pipeline. Generate 3 posts.
```
```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```
```
Run the pipeline and skip Notion publishing.
```

The orchestrator (`orchestrator.md`) handles everything. Claude reads it and runs the full pipeline automatically.

---

## The Pipeline (What Happens)

```
1. news-gatherer     → fetches RSS feeds, scores articles by topic relevance
2. trending-tracker  → searches web for the 15–20 hottest AI keyword phrases right now
3. post-generator    → for each article cluster: writes a branded LinkedIn draft, saves to posts/
4. review-editor     → presents each draft for your approval before Notion push
5. notion-publisher  → publishes approved drafts to your Notion page (optional)
```

---

## Editable Components

All configuration lives in `config/` — edit any file and changes take effect on the next run.

| File | What it controls | Edit when... |
|------|-----------------|--------------|
| `config/topics.yaml` | Companies, keywords, trending seeds, freshness settings | You want to track new companies, remove topics, or change how fresh articles must be |
| `config/brand_kit.yaml` | Your name, voice, tone, post structure, hashtags, length limits | Your brand evolves, you want a different style, or you want to adjust the post template |
| `config/sources.yaml` | RSS feeds and API sources to pull from | You want to add a new publication, remove a source, or disable a feed temporarily |
| `config/editorial_rules.yaml` | Content mix targets, topics to avoid, seasonal focus, quality gates | You want to shift your content focus, avoid certain angles, or set publishing frequency |

---

## Output

Posts are saved to `posts/` as markdown files:

```
posts/
  2026-01-15_10-30-00_openai-launches-new-model.md
  2026-01-15_10-30-00_ai-startup-raises-200m.md
```

Each file has YAML frontmatter (metadata) followed by the post body.
Change `status: draft` → `status: published` to track what's gone live.

---

## Environment Setup

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

| Variable | Required? | What it does |
|----------|-----------|--------------|
| `ANTHROPIC_API_KEY` | Only outside Claude Code | Claude API access |
| `NOTION_PAGE_ID` | Optional | Enables Notion publishing |
| `NOTION_API_KEY` | Optional | REST API fallback for Notion |
| `NEWSAPI_KEY` | Optional | Broader news coverage via NewsAPI |

---

## Agents Reference

Each agent is a self-contained markdown file in `.claude/agents/`:

| Agent | File | Role |
|-------|------|------|
| News Gatherer | `news-gatherer.md` | Fetches + scores RSS articles |
| Trending Tracker | `trending-tracker.md` | Finds hottest AI keyword phrases |
| Post Generator | `post-generator.md` | Writes branded LinkedIn draft |
| Review Editor | `review-editor.md` | Presents drafts for your approval |
| Notion Publisher | `notion-publisher.md` | Publishes approved drafts to Notion |

---

## Customising Your Content Mix

`config/editorial_rules.yaml` controls:
- How many posts per topic category (funding vs. launches vs. experiments)
- Topics to avoid this week
- Seasonal or timely angles to prioritise
- Minimum quality gates before a post gets generated

---

## Customising Your Brand Voice

`config/brand_kit.yaml` is the single source of truth for how every post is written. Key things to personalise:

1. `author.name` and `author.title` — your full name and professional title
2. `tone_of_voice.primary_traits` — how you want to come across
3. `brand.focus_areas` — the lenses you write through
4. `brand.hashtags` — your hashtag strategy
5. `research_standards.min_sources` — minimum sources required per post

---

## Adding a New Company to Track

Edit `config/topics.yaml` under `companies_to_track`:

```yaml
    - name: "New Company"
      keywords:
        - "New Company"
        - "their product name"
        - "CEO name"
```

---

## Adding a New RSS Feed

Edit `config/sources.yaml`:

```yaml
    - name: "My New Source"
      url: "https://example.com/feed.xml"
      priority: high    # high | medium | low
      enabled: true
```
