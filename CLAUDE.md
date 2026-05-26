# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn post drafts — built entirely with Claude agents and subagents, no traditional code.

---

## Before Your First Run

Open `config/brand_kit.yaml` and fill in your name and title:

```yaml
author:
  name: "Your Full Name"
  title: "Your Professional Title"
```

Everything else in the brand kit is ready to go — edit it any time to change your tone, post length, or hashtag strategy.

---

## How to Run the Pipeline

Say any of the following to Claude Code:

**Standard run (generates 2 posts):**
```
Run the LinkedIn Post Generator pipeline.
```

**Custom number of posts:**
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

**Dry run — fetch and rank news only, skip writing:**
```
Run the pipeline in dry-run mode.
```

**More articles per post:**
```
Run the pipeline. Generate 2 posts. Use 8 articles per cluster.
```

The orchestrator (`orchestrator.md`) handles the full flow automatically.

---

## Pipeline Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending AI keyword phrases
├── .claude/agents/post-generator.md     → writes + saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → (optional) publishes to Notion
```

Each agent is a self-contained markdown file — edit any of them directly to change how that step behaves.

---

## Configuration Files

All settings live in `config/` — edit these files directly, changes take effect on the next run.

| File | What it controls | Edit when... |
|------|-----------------|--------------|
| `config/brand_kit.yaml` | Your name, voice, tone, post structure, hashtags | Changing how posts are written |
| `config/topics.yaml` | AI companies, keywords, freshness thresholds | Adding or removing companies to track |
| `config/sources.yaml` | RSS feeds and news sources | Adding or disabling news sources |

---

## What Gets Tracked

Configured in `config/topics.yaml` and `config/sources.yaml`:

**AI companies and products:** ChatGPT / OpenAI, Claude / Anthropic, Gemini / Google DeepMind, Perplexity, ElevenLabs, Midjourney, xAI (Grok), Meta AI, Mistral, Runway, Cohere, HuggingFace, and more.

**Big tech AI moves:** Microsoft Copilot, Apple Intelligence, Amazon Bedrock, Nvidia, Salesforce Agentforce, Adobe Firefly.

**Startup funding:** TechCrunch Startups, Crunchbase News, SiliconAngle.

**YouTube releases:** Official channels from OpenAI, Anthropic, Google DeepMind, and Two Minute Papers.

**Research and breakthroughs:** MIT Technology Review, Wired, Ars Technica, VentureBeat.

---

## Output

Posts save to `posts/` as `.md` files with YAML frontmatter:

```
posts/
  2026-01-15_10-30-00_openai-launches-gpt5.md
  2026-01-15_10-31-00_anthropic-funding-round.md
```

Each file contains source metadata, matched companies, trending keywords used, and the full post body — ready to review and publish.

Change `status: draft` → `status: published` once a post goes live on LinkedIn.

---

## Notion Setup (optional)

Copy `.env.example` to `.env`, then fill in:

```bash
NOTION_PAGE_ID=your_32char_page_id_here
```

The pipeline auto-detects this and appends each draft as a collapsible toggle block on your Notion page after generating it.

---

## Adding News Sources

Add any RSS feed to `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

Set `enabled: false` to pause a source without removing it.

---

## Customising the Brand Voice

`config/brand_kit.yaml` controls everything about how posts are written:

- `tone_of_voice.primary_traits` — the personality traits that define your voice
- `tone_of_voice.writing_style` — sentence-level rules applied to every post
- `tone_of_voice.post_structure` — the ordered blueprint (hook → context → evidence → take → CTA → sources → hashtags)
- `brand.hashtags` — always-include tags and the rotation pool
- `brand.post_length` — `short` (300–500 chars) / `medium` (500–900) / `long` (900–1300)
- `research_standards.min_sources` — minimum cited sources per post (default: 4)
