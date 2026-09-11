# LinkedIn Post Generator

An AI-powered pipeline that tracks AI news, identifies trending topics, and writes research-backed LinkedIn drafts — in your voice, with cited sources, ready to review and publish.

---

## What It Does

1. **Tracks your topics** — reads `config/topics.yaml` to know which AI companies, themes, and events to follow (ChatGPT, Claude, Perplexity, Gemini, ElevenLabs, Midjourney, big tech, startup funding, etc.)
2. **Fetches fresh news** — scans RSS feeds from TechCrunch, VentureBeat, The Verge, company blogs, and YouTube channels, scoring articles by relevance
3. **Tracks what's trending** — searches the web for the most-discussed AI keywords from the past 7 days
4. **Picks the right angle** — selects a post format from `config/content_angles.yaml` (tool experiment, feature launch, funding news, YouTube reaction, etc.)
5. **Writes in your voice** — generates posts following `config/brand_kit.yaml`: your tone, your structure, your human-in-the-loop stance
6. **Cites sources** — every post includes numbered source links, minimum 4 per post
7. **Remembers what it's covered** — writes to `config/memory.yaml` to avoid repeating the same story twice within 7 days
8. **Publishes to Notion** — optional: pushes drafts to your Notion "LinkedIn Post Ideas" page

---

## Architecture

The pipeline is a **multi-agent system**. An orchestrator reads a task, spawns specialised subagents, and passes data between them:

```
orchestrator.md
├── .claude/agents/news-gatherer.md       → fetch + score RSS articles
├── .claude/agents/trending-tracker.md   → find trending keyword phrases
├── .claude/agents/post-generator.md     → write + save LinkedIn draft
└── .claude/agents/notion-publisher.md   → push draft to Notion (optional)
```

No Python. No external dependencies. Runs entirely inside Claude Code using native tools (WebFetch, WebSearch, Read, Write) and the Notion MCP connector.

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude reads `orchestrator.md` and runs the full pipeline. Typical run time: 3–6 minutes.

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration Files

All settings are stored as separate editable files. Change any file and it takes effect on the next run — no restarts needed.

| File | What it controls |
|------|-----------------|
| `config/topics.yaml` | AI companies, keywords, and categories to track |
| `config/sources.yaml` | RSS feeds, company blogs, YouTube channels to scan |
| `config/brand_kit.yaml` | Your name, tone of voice, writing rules, post structure, hashtags |
| `config/content_angles.yaml` | Post format templates (tool experiment, funding news, etc.) |
| `config/memory.yaml` | History of what's been covered — prevents duplicate stories |

### Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# For Notion publishing (optional)
NOTION_PAGE_ID=your_32char_page_id_here
NOTION_API_KEY=secret_xxx

# For broader news coverage (optional)
NEWSAPI_KEY=your_key_here
```

---

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-new-reasoning-model.md
  2024-01-15_10-35-00_anthropic-raises-series-d.md
```

Each file contains:
- **YAML frontmatter**: title, date, sources, companies, categories, post angle, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Editing Your Brand Kit (`config/brand_kit.yaml`)

The most important file to personalise. Key sections:

**`author`** — your name, title, tagline, location. Fill this in first.

**`tone_of_voice.primary_traits`** — how you come across. The default is: curious, pragmatic, accessible, opinionated, human.

**`tone_of_voice.writing_style`** — rules every post follows: short paragraphs, hooks that aren't "I", generous whitespace, max 15 words per sentence.

**`tone_of_voice.post_structure`** — the post blueprint: Hook → Context → Evidence → Your Take → So What → CTA → Sources → Hashtags.

**`brand.editorial_stance`** — the human-in-the-loop principle: you are the experimenter and editor, AI is the assistant. Every post should feel like a field report.

---

## Editing Your Topics (`config/topics.yaml`)

Add or remove companies and keywords to control what gets tracked.

**Key sections:**
- `companies_to_track.ai_labs` — OpenAI, Anthropic, Google, Perplexity, ElevenLabs, Midjourney, etc.
- `companies_to_track.big_tech` — Microsoft, Apple, Amazon, Nvidia, Salesforce, Adobe
- `topic_categories` — New launches, Funding, Marketing/Brands, Research, Regulation, Tools
- `freshness.max_article_age_hours` — only articles newer than this (default: 48h)
- `freshness.min_relevance_score` — minimum score to include an article (default: 2)

---

## Post Angles (`config/content_angles.yaml`)

Seven named formats the post-generator picks from based on the article type:

| Angle | When it's used |
|-------|---------------|
| `tool_experiment` | New feature/model you can test — frame it as your experiment |
| `feature_launch` | Product launch — what brands should know |
| `funding_news` | Series A/B/C, valuations, acquisitions |
| `big_tech_move` | Microsoft, Apple, Google, Meta, Amazon AI moves |
| `youtube_reaction` | New video from an AI company |
| `pattern_recognition` | Multiple related stories forming a bigger trend |
| `contrarian_take` | When the mainstream narrative is missing something |

Edit the `hook_examples` and `structure_notes` in each angle to match your voice further.

---

## Memory (`config/memory.yaml`)

After each run, the orchestrator records:
- Which companies were covered
- Which source URLs were used
- A one-line topic summary

On the next run, it filters out articles that repeat the same company within `dedup_window_days` (default: 7 days) or reuse the same source URL within `url_dedup_window_days` (default: 14 days).

To reset memory or allow a topic again sooner: open `config/memory.yaml` and delete the relevant entry.

---

## Notion Integration

Set `NOTION_PAGE_ID` in your `.env` file. After post generation, the pipeline pushes each draft as a toggle block on your Notion page — collapsible, with a status callout showing how many sources were cited.

Set up steps:
1. Go to https://www.notion.so/my-integrations → New integration
2. Copy the token → paste as `NOTION_API_KEY` in `.env`
3. Open your LinkedIn Post Ideas page in Notion
4. `...` → Connections → connect your integration
5. Copy the 32-char page ID from the URL → paste as `NOTION_PAGE_ID` in `.env`

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

Set `enabled: false` to pause a feed without deleting it.
