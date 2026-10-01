# LinkedIn Post Generator

This project is an AI-powered LinkedIn post generator that fetches trending AI news, tracks what's buzzing, and writes research-backed draft posts in the author's brand voice.

## How to Run the Pipeline

To run the full pipeline (fetch news → find trending topics → generate posts):

```
Run the LinkedIn Post Generator pipeline.
```

To generate more posts or use fewer sources:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

To preview the news without generating posts:

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

The orchestrator lives in `orchestrator.md` — read that file to understand the full pipeline.

---

## What This Builds

Draft LinkedIn posts for a brand and marketing professional tracking the AI space, with a specific focus on:

- New features or product launches from AI companies (ChatGPT, Claude, Gemini, Perplexity, ElevenLabs, Midjourney, etc.)
- New YouTube videos from key AI companies and researchers
- Big tech AI moves (Microsoft, Google, Apple, Nvidia, Amazon, Salesforce)
- AI startup funding rounds, acquisitions, and IPOs
- "Human in the loop" posts — personal experiments using AI tools in real work

Every post is written from the perspective of someone who follows AI news closely and has opinions on **how brands can leverage AI today** — not a neutral summary, but a real take.

---

## Editable Configuration Files

| File | What to edit |
|------|-------------|
| `config/brand_kit.yaml` | Your name, title, tone of voice, writing style, hashtags |
| `config/topics.yaml` | Companies to track, topic categories, trending keyword seeds |
| `config/sources.yaml` | RSS feeds, YouTube channels, API sources |

---

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter.

Change `status: draft` to `status: published` to track what's been posted to LinkedIn.

---

## Environment

Copy `.env.example` to `.env` and fill in:
- `NOTION_PAGE_ID` — to push drafts to a Notion page (optional)
- `NEWSAPI_KEY` — for broader news coverage beyond RSS (optional)

---

## Pipeline Agents

| Agent | File | Role |
|-------|------|------|
| news-gatherer | `.claude/agents/news-gatherer.md` | Fetches and scores RSS/YouTube articles |
| trending-tracker | `.claude/agents/trending-tracker.md` | Finds what's buzzing across the web this week |
| post-generator | `.claude/agents/post-generator.md` | Writes and saves a branded LinkedIn draft |
| notion-publisher | `.claude/agents/notion-publisher.md` | Pushes drafts to Notion (optional) |
