# LinkedIn Post Generator — Project Guide

A multi-agent pipeline that monitors AI news, tracks trending topics, and writes branded LinkedIn post drafts. Every component is a separate file you can edit without touching anything else.

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with options:
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
Run the pipeline in dry-run mode.
Run the pipeline in experiments mode.
```

The orchestrator (`orchestrator.md`) handles everything — spawning agents, passing data, saving drafts.

---

## Project Structure

```
orchestrator.md                          ← Master pipeline — run this
config/
  topics.yaml                           ← AI companies and keywords to track
  sources.yaml                          ← RSS feeds and news sources
  brand_kit.yaml                        ← Your voice, tone, and writing rules
  experiments.yaml                      ← Your personal AI experiment log
.claude/agents/
  news-gatherer.md                      ← Fetches + scores RSS articles
  trending-tracker.md                   ← Finds trending AI keyword phrases
  post-generator.md                     ← Writes news-driven post drafts
  experiment-post-generator.md          ← Writes personal "I tried X" posts
  notion-publisher.md                   ← Pushes drafts to Notion
posts/                                  ← Generated draft posts (markdown)
.env.example                            ← Copy to .env and fill in keys
```

---

## The Two Types of Posts

### 1. News-driven posts (default)
Triggered by RSS + trending topics. Cover: new AI feature launches, startup funding, big tech AI moves, YouTube videos from AI companies. These run automatically on every pipeline run.

### 2. Experiment posts (`experiments.yaml`)
Personal "I tried this AI tool" posts written from your own notes. To queue one:
1. Add an entry to `config/experiments.yaml`
2. Set `want_to_write_about: true`
3. Run: `Run the LinkedIn Post Generator pipeline.`
4. After the post is generated, set it back to `false`

---

## Editing the Components

| File | What to edit |
|------|-------------|
| `config/topics.yaml` | Add/remove AI companies, keywords, topic categories |
| `config/sources.yaml` | Add/remove RSS feeds; set `enabled: false` to pause one |
| `config/brand_kit.yaml` | **Start here** — set your name, title, tone, hashtags |
| `config/experiments.yaml` | Log AI experiments; flip `want_to_write_about: true` to queue a post |
| `orchestrator.md` | Adjust pipeline logic, post counts, experiment handling |
| `.claude/agents/*.md` | Refine any agent's behaviour directly |

---

## First-Time Setup

1. **Edit `config/brand_kit.yaml`** — fill in your name, title, and tagline
2. **Copy `.env.example` to `.env`** — add your Notion page ID if you want Notion publishing
3. **Run the pipeline** — `Run the LinkedIn Post Generator pipeline.`

---

## Output

Posts save to `posts/` as markdown files with YAML frontmatter:
```
posts/
  2024-01-15_10-30-00_openai-gpt5-launch.md      ← news post
  2024-01-15_11-00-00_experiment-elevenlabs.md   ← experiment post
```

Change `status: draft` → `status: published` to track what's gone live.

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `NOTION_PAGE_ID` | Your Notion page for drafts (optional) |
| `NOTION_API_KEY` | Notion integration token (optional) |
| `NEWSAPI_KEY` | NewsAPI.org key for broader coverage (optional) |
