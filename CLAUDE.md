# LinkedIn Post Generator

This project is an AI-powered pipeline that turns AI news into branded LinkedIn post drafts. It runs entirely through Claude agents — no Python required.

## How to Run

To run the full pipeline (fetch news → track trends → generate posts → publish to Notion):

```
Run the LinkedIn Post Generator pipeline.
```

Claude will read `orchestrator.md` and execute all four subagents in sequence.

### Common variants

```
Run the LinkedIn Post Generator. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Run the LinkedIn Post Generator and use 8 articles per post.
```

## Configuration Files

Edit these to customise what gets tracked and how posts are written:

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Companies to track, topic categories, trending keyword seeds, freshness settings |
| `config/brand_kit.yaml` | **Your name and title**, tone of voice, writing style rules, post structure, hashtags |
| `config/sources.yaml` | RSS feeds, company blogs, YouTube channels, optional NewsAPI |

**First-time setup**: Open `config/brand_kit.yaml` and replace the `author` placeholders with your actual name, title, and location.

## Pipeline Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md     → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md  → finds trending AI keyword phrases
├── .claude/agents/post-generator.md    → writes + saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md  → pushes drafts to Notion (optional)
```

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter. Change `status: draft` to `status: published` to track what's gone live.

## Notion Integration

Set `NOTION_PAGE_ID` in a `.env` file (copy from `.env.example`) to push drafts to a Notion page automatically after each run.

## Topic Coverage

The pipeline tracks:
- AI model launches (OpenAI, Anthropic, Google, Perplexity, ElevenLabs, Midjourney, etc.)
- Big tech AI moves (Microsoft, Apple, Amazon, Nvidia, Salesforce, Adobe)
- AI startup funding rounds and acquisitions
- AI research breakthroughs and benchmarks
- AI tools for marketing, productivity, and brand teams

Add any company or keyword to `config/topics.yaml` → it takes effect on the next run.
