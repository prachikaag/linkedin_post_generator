# LinkedIn Post Generator

An AI-powered pipeline that monitors trending AI news, tracks what's buzzing, and writes research-backed LinkedIn post drafts — in your voice and brand style. Built entirely on Claude agents with no traditional code.

---

## What It Does

1. **Fetches fresh AI news** from 20+ RSS feeds (TechCrunch, VentureBeat, Anthropic, OpenAI, Google DeepMind, YouTube channels, and more)
2. **Tracks trending keywords** by searching the web for what's buzzing in the last 7 days
3. **Deduplicates against memory** — never writes a post about an article it already covered
4. **Generates branded posts** in your exact tone of voice, with cited sources
5. **Reviews post quality** against your brand kit before saving
6. **Saves drafts** to `posts/` as markdown files you can edit before publishing
7. **Publishes to Notion** (optional) so you can review and schedule from there

**Topics tracked:** ChatGPT, Claude, Gemini, Perplexity, ElevenLabs, Midjourney, Runway, Suno, Cursor, and 20+ more AI companies. Plus big tech AI moves and startup funding rounds.

---

## Architecture — All Components Are Editable Files

```
orchestrator.md                    ← master pipeline controller
├── .claude/agents/
│   ├── news-gatherer.md           ← fetches + scores RSS articles
│   ├── trending-tracker.md        ← finds trending AI keywords
│   ├── memory-manager.md          ← deduplicates across runs
│   ├── post-generator.md          ← writes LinkedIn post drafts
│   ├── post-reviewer.md           ← quality-checks posts before saving
│   └── notion-publisher.md        ← publishes approved drafts to Notion
├── config/
│   ├── topics.yaml                ← companies, keywords, freshness settings
│   ├── brand_kit.yaml             ← YOUR voice, tone, writing rules, hashtags
│   └── sources.yaml               ← RSS feeds + optional APIs
├── memory.json                    ← tracks covered article URLs (auto-managed)
└── posts/                         ← generated draft posts (markdown)
```

Every file is meant to be read and edited. You own all the components.

---

## Quick Start

### 1. Personalise your brand kit

Open `config/brand_kit.yaml` and fill in:
- Your name, title, and tagline
- Your LinkedIn URL
- Your location

Everything else (tone, writing style, hashtags) is already set up — tweak as you like.

### 2. Set up Notion (optional)

Copy `.env.example` to `.env` and fill in:

```bash
NOTION_PAGE_ID=your_32char_page_id_here   # from your Notion page URL
NOTION_API_KEY=secret_xxx                 # from notion.so/my-integrations
```

If left blank, posts are saved only as local `.md` files.

### 3. Run the pipeline

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with options:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration Reference

### `config/topics.yaml` — What to Track

Controls which companies and topics trigger article collection.

| Section | Purpose |
|---------|---------|
| `companies_to_track.ai_labs` | Core AI companies (OpenAI, Anthropic, Google, etc.) |
| `companies_to_track.ai_builders` | Tools and startups (Cursor, Groq, Runway, etc.) |
| `companies_to_track.big_tech` | Microsoft, Apple, Amazon, Nvidia, Salesforce, Adobe |
| `topic_categories` | Labels for scoring: launches, funding, marketing, research, regulation |
| `trending_keywords.seed_terms` | Starting points for the trending keyword search |
| `freshness` | Age limit for articles, minimum score, max articles per run |

**To add a company:** add a block under the relevant section with `name` and `keywords`.

**To raise/lower the news bar:** adjust `min_relevance_score` (default 2) and `max_article_age_hours` (default 48).

### `config/brand_kit.yaml` — Your Voice

Controls every word of every post.

| Section | Purpose |
|---------|---------|
| `author` | Your name, title, tagline, location |
| `tone_of_voice.primary_traits` | How you come across |
| `tone_of_voice.writing_style` | Per-sentence rules (hooks, line breaks, length) |
| `tone_of_voice.post_structure` | The HOOK → CONTEXT → EVIDENCE → TAKE → SO WHAT → CTA → SOURCES → HASHTAGS blueprint |
| `tone_of_voice.dos` / `donts` | What makes a great vs weak post for you |
| `brand.focus_areas` | The lenses you write through |
| `brand.hashtags` | Always-include + rotation pool |
| `brand.post_length` | `short` / `medium` / `long` |
| `research_standards` | Minimum sources, quote format, citation format |

### `config/sources.yaml` — Where to Fetch News

All enabled RSS feeds and optional APIs.

| Section | Contents |
|---------|---------|
| `rss_feeds.ai_news` | TechCrunch, The Verge, VentureBeat, Wired, MIT Tech Review, Ars Technica |
| `rss_feeds.company_blogs` | OpenAI, Anthropic, Google AI, DeepMind, Meta AI, Microsoft, Hugging Face, Mistral, Perplexity, ElevenLabs |
| `rss_feeds.funding_news` | TechCrunch Startups, Crunchbase News, SiliconAngle |
| `rss_feeds.youtube_channels` | Google DeepMind, OpenAI, Anthropic, Two Minute Papers |
| `optional_apis.newsapi` | NewsAPI (requires free key — set `enabled: true` after adding key) |

**To add a feed:** add a block with `name`, `url`, `priority` (high/medium/low), and `enabled: true`.

---

## Agents Reference

| Agent | Tools | What it does |
|-------|-------|-------------|
| `news-gatherer` | Read, WebFetch | Fetches all enabled RSS feeds, scores by keyword match, deduplicates |
| `trending-tracker` | Read, WebSearch | Finds the 15–20 most-discussed AI phrases from the past 7 days |
| `memory-manager` | Read, Write | Filters out already-covered articles; records newly published posts |
| `post-generator` | Read, Write | Synthesises a cluster of articles into a branded post and saves it |
| `post-reviewer` | Read | Runs 14 quality checks against the brand kit; returns APPROVED / APPROVED_WITH_NOTES / NEEDS_REVISION |
| `notion-publisher` | Read, Notion MCP | Appends the post as a toggle block on a Notion page |

---

## Output

Generated posts are saved to `posts/` as markdown with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5-model.md
  2024-01-15_11-00-00_ai-startup-funding-round.md
```

Each file includes:
- **YAML frontmatter**: source metadata, matched companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` → `status: published` to track what's gone live.

### `memory.json`

Auto-managed. Tracks every article URL already used across all runs, so the pipeline never repeats itself.

To reset memory (re-allow all articles): clear the `seen_urls` array and the `generated_posts` list.

---

## Content Types This Pipeline Targets

- **New AI feature/product launches** — when ChatGPT, Claude, Gemini, ElevenLabs, Midjourney, etc. ship something new
- **YouTube video releases** — when AI companies post new demo videos (tracked via RSS)
- **Big tech AI moves** — Microsoft Copilot, Apple Intelligence, Amazon Bedrock, Nvidia announcements
- **AI startup funding** — Series A/B/C rounds, acquisitions, IPOs
- **AI for brands and marketing** — practical use cases for marketing teams
- **Research breakthroughs** — benchmarks, capability milestones worth writing about
- **Human-in-the-loop experimentation** — posts about using AI tools in your own workflow

---

## Customising Without Breaking Anything

- **Add a topic:** edit `config/topics.yaml` — add keywords under an existing company or add a new company block
- **Change your voice:** edit `config/brand_kit.yaml` — every style rule is a bullet point you can rewrite
- **Add a news source:** edit `config/sources.yaml` — any RSS URL works
- **Change post length:** set `brand.post_length` to `short`, `medium`, or `long` in `brand_kit.yaml`
- **Reset and start fresh:** delete `memory.json` contents (keep the file, just set `seen_urls: []`)
- **Adjust quality bar:** the post-reviewer checks 14 rules — lower the bar in `post-reviewer.md` if too many posts are flagged
