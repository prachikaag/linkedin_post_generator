# LinkedIn Post Generator

An AI pipeline that monitors the AI news landscape, surfaces what's trending, and writes research-backed LinkedIn post drafts in your voice — with a human-in-the-loop review step before committing to full generation.

---

## What It Does

1. **Fetches news** from 20+ RSS feeds (TechCrunch, The Verge, VentureBeat, Wired, OpenAI/Anthropic/Google blogs, Crunchbase, YouTube channels, and more)
2. **Tracks trending keywords** across the AI space from the past 7 days
3. **Generates a menu of post ideas** for you to review and pick from (default mode)
4. **Writes full LinkedIn post drafts** in your exact voice and brand style — with cited sources
5. **Saves drafts** to `posts/` as markdown files ready to review and publish
6. **Publishes to Notion** (optional) for editorial workflow

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

**Default: IDEAS MODE** — shows you a menu of 8 post ideas to pick from. Choose what resonates. Then say:

```
Generate post for idea 3
```

Or to generate posts without the ideas step:

```
Run the pipeline and generate posts directly
```

Other useful prompts:
```
Show me what's in the news today — dry run only
Generate 3 posts from today's news
Run the pipeline. Generate posts for ideas 1, 3, and 5.
```

---

## Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md       → Fetches + scores RSS articles
├── .claude/agents/trending-tracker.md    → Finds trending keyword phrases
├── .claude/agents/post-idea-generator.md → Generates idea menu for review ← HUMAN IN THE LOOP
├── .claude/agents/post-generator.md      → Writes & saves LinkedIn drafts
└── .claude/agents/notion-publisher.md    → Publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and contract. No Python or external dependencies required — runs entirely within Claude Code.

---

## Configuration Files

All settings are in `config/`. **Each file is independently editable.**

| File | What It Controls | Edit When |
|------|-----------------|-----------|
| `config/persona.yaml` | Who you are — name, bio, POV, tools you use | Your title or focus changes |
| `config/brand_kit.yaml` | How you write — tone, style, structure, hashtags | You want to change your voice |
| `config/content_pillars.yaml` | What you write about — 6 post types with angles and hooks | You want a new content category |
| `config/topics.yaml` | Which companies and keywords to track | You want to add/remove an AI company |
| `config/sources.yaml` | Which RSS feeds and APIs to fetch from | You want to add a new news source |
| `config/memory.yaml` | Track record of what's been written | Auto-updated; edit to reset history |

---

## Content Pillars — What Gets Written

The pipeline generates posts across 6 content types. Each has its own framing, hook style, and CTA format defined in `config/content_pillars.yaml`.

| Pillar | Trigger | Example |
|--------|---------|---------|
| **Feature Launch** | New model/product from ChatGPT, Claude, Gemini, Perplexity, Midjourney, ElevenLabs etc. | "A new AI feature dropped. Here's what brands actually need to know." |
| **YouTube Video** | New video/demo from a major AI company | "I watched [Company]'s new demo so you don't have to." |
| **Startup Funding** | Funding rounds, acquisitions, IPOs | "An AI startup just raised $X. The interesting part isn't the number." |
| **Big Tech AI** | Microsoft, Apple, Google, Meta, Amazon AI moves | "Most brand teams are already paying for this software. AI just changed what it does." |
| **Human in the Loop** | Your own AI experiments and firsthand testing | "I spent [time] testing [tool] for [task]. Here's what I actually found." |
| **Brand Strategy** | Synthesis posts: what AI developments mean for brands | "Here's what I think brands are missing in all the AI conversation right now." |

---

## Setting Up Your Identity

Edit `config/persona.yaml` to fill in your details:

```yaml
author:
  name: "Your Name"
  title: "Your Title"
  tagline: "Your tagline"
  linkedin_url: "https://www.linkedin.com/in/yourprofile"
  location: "City, Country"
```

Also update `perspective` and `authority_topics` in that file — these shape how every post is framed from your POV.

---

## Adding Your Brand Voice

Edit `config/brand_kit.yaml` to refine:
- `tone_of_voice.primary_traits` — how you come across
- `tone_of_voice.writing_style` — your sentence and paragraph rules
- `tone_of_voice.post_structure` — the blueprint every post follows
- `brand.hashtags` — your hashtag strategy

The defaults are calibrated for an opinionated brand strategist and AI practitioner who experiments with tools firsthand and writes for marketing and brand leaders.

---

## Tracking What's Been Written

`config/memory.yaml` is auto-updated after each post is generated. It tracks:
- Source URLs already used as primary anchors (prevents re-covering the same story)
- Companies recently featured (encourages diversity)
- Full post history with date, pillar, and status

To reset history and allow re-covering past topics, clear the arrays in that file.

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5-model.md
  2024-01-16_09-15-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, categories, pillar, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to copy, edit, and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Notion Integration (Optional)

Set `NOTION_PAGE_ID` in `.env` to push drafts directly to a Notion page as toggle blocks.

Copy `.env.example` to `.env` and fill in:

```bash
NOTION_PAGE_ID=your_32char_page_id_here
NOTION_API_KEY=secret_xxx   # only needed for standalone use
```

Setup: Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New integration → copy the token → connect it to your LinkedIn Post Ideas page → copy the page ID from the URL.

---

## Adding News Sources

Edit `config/sources.yaml` to add any RSS feed:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

YouTube channels are already tracked — add more in the `youtube_channels` section.

---

## Agents Reference

| Agent | Tools | Reads | Does |
|-------|-------|-------|------|
| `news-gatherer` | Read, WebFetch | sources.yaml, topics.yaml, memory.yaml | Fetches RSS, scores by relevance, tags YouTube, returns ranked JSON |
| `trending-tracker` | Read, WebSearch | topics.yaml | Finds 15-20 trending AI keyword phrases |
| `post-idea-generator` | Read | content_pillars.yaml, persona.yaml, memory.yaml | Returns a numbered ideas menu for human review |
| `post-generator` | Read, Write | brand_kit.yaml, persona.yaml, content_pillars.yaml, memory.yaml | Writes a full post in your voice, saves as .md, updates memory |
| `notion-publisher` | Read, Notion MCP | .env | Appends post as toggle block to Notion page |
