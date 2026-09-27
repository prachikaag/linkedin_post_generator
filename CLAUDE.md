# LinkedIn Post Generator — Project Guide

## What This Does

An AI pipeline that generates LinkedIn posts in your brand voice, backed by real sources.

Two modes:
- **News mode** — fetches today's AI news, finds trending keywords, writes a post
- **Experiment mode** — turns your personal AI experiment notes into a post

---

## How to Run

Open this project in Claude Code and say any of these:

```
Run the LinkedIn Post Generator pipeline.
```
```
Generate 3 LinkedIn posts from today's AI news.
```
```
Write a LinkedIn post from my latest AI experiment.
```
```
Run the pipeline in dry-run mode — fetch and rank news only, don't write posts.
```

The orchestrator in `orchestrator.md` handles everything from there.

---

## Components You Can Edit

Every component is a standalone file — edit one without touching the others.

### Configuration (edit these freely)

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | Companies and topics to track (OpenAI, Claude, Gemini, etc.) |
| `config/sources.yaml` | RSS feeds and YouTube channels to fetch news from |
| `config/brand_kit.yaml` | **Your tone of voice, writing style, and brand guidelines** |
| `config/post_types.yaml` | Post formats — hooks, angles, and hashtags for each type |
| `config/experiments.yaml` | **Your personal AI experiments log** — add entries to get posts |

### Agents (edit if you want to customise the pipeline behaviour)

| File | What it does |
|------|-------------|
| `.claude/agents/news-gatherer.md` | Fetches and scores RSS articles |
| `.claude/agents/trending-tracker.md` | Finds what's trending on the web |
| `.claude/agents/post-generator.md` | Writes LinkedIn posts from news articles |
| `.claude/agents/experiment-writer.md` | Writes LinkedIn posts from your experiments |
| `.claude/agents/notion-publisher.md` | Pushes drafts to a Notion page |

### Pipeline (edit to change workflow behaviour)

| File | What it does |
|------|-------------|
| `orchestrator.md` | Master pipeline — runs all steps in order |

---

## Your Most Important Config Files

### 1. `config/brand_kit.yaml`
Set your name, title, tone of voice, and writing style here.
Everything the AI writes is shaped by this file. **Edit your author details first.**

Key sections:
- `author` — your name, title, tagline
- `tone_of_voice.writing_style` — the rules every post must follow
- `tone_of_voice.post_structure` — the exact blueprint for every post
- `brand.human_in_the_loop` — your core philosophy about AI collaboration

### 2. `config/topics.yaml`
Controls what news gets fetched and scored.
Add companies or keywords you want to follow. Already includes:
- ChatGPT, Claude, Gemini, Perplexity, ElevenLabs, Midjourney
- Google, Microsoft, Apple, Amazon, Meta, Nvidia
- Startup funding keywords, AI research keywords

### 3. `config/post_types.yaml`
Defines the 5 post types and their specific hooks, angles, and hashtags:
- `new_feature` — AI tool launches a new feature
- `big_tech` — big tech makes a significant AI move
- `startup_funding` — AI startup raises money
- `video_reaction` — reacting to a YouTube video or demo
- `experiment` — sharing your personal AI experiment results

### 4. `config/experiments.yaml`
Your personal AI experiment log. Every entry can become a LinkedIn post.

**To log a new experiment, add an entry:**
```yaml
- tool: "Name of the AI tool"
  use_case: "What you used it for"
  date: "YYYY-MM-DD"
  time_spent: "e.g. 30 mins"
  prompt_or_brief: "The actual prompt you gave it"
  what_happened: "What it produced"
  what_worked: "The good parts"
  what_didnt_work: "What disappointed you"
  surprising_finding: "The unexpected thing"
  verdict: "Your honest one-sentence verdict"
  brand_takeaway: "What other marketers should take from this"
  post_status: "idea"   # ← this flags it for post generation
```

Then say: `Write a LinkedIn post from my latest AI experiment.`

---

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter.
Change `status: draft` to `status: published` to track what's gone live.

```
posts/
  2026-09-27_10-30-00_chatgpt-new-voice-mode.md      ← news post
  2026-05-01_14-30-00_experiment-claude-sonnet.md     ← experiment post
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
NOTION_PAGE_ID=your_32char_page_id    # enables Notion publishing
NOTION_API_KEY=secret_xxx              # Notion integration token
ANTHROPIC_API_KEY=                     # not needed inside Claude Code
```

---

## Quick Customisation Cheat Sheet

| I want to... | Edit this |
|-------------|-----------|
| Change my writing style | `config/brand_kit.yaml` → `tone_of_voice.writing_style` |
| Follow a new AI company | `config/topics.yaml` → add to `companies_to_track` |
| Add a new RSS feed | `config/sources.yaml` → add to the right category |
| Add a new YouTube channel | `config/sources.yaml` → `youtube_channels` |
| Change what makes a good post hook | `config/post_types.yaml` → `hook_templates` |
| Log an AI experiment | `config/experiments.yaml` → add new entry |
| Generate a post from an experiment | Say: `Write a post from my latest AI experiment` |
| Push to Notion | Set `NOTION_PAGE_ID` in `.env` |
