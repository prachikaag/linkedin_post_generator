# LinkedIn Post Generator

An AI-powered pipeline that watches for fresh AI news, spots what's trending, and writes research-backed LinkedIn draft posts in your voice — entirely through Claude agents. No Python, no servers, no manual setup beyond editing a few YAML files.

---

## What It Does

1. Reads your **topics of interest** and monitors 30+ news feeds for relevant stories
2. Searches the web for **what's actually trending** in AI right now
3. Reads your **brand kit and tone of voice** to understand how you write
4. Generates **LinkedIn post drafts** with cited sources, structured to your brand
5. Saves every post as a reviewable draft — you edit and publish when ready
6. **Remembers** which articles it already covered so it never repeats itself

The goal: show you're following AI news and have an opinion on how brands can leverage it. Every post comes with sources, your take, and a CTA — ready for a human review pass before publishing.

---

## Architecture

The pipeline is a **multi-agent system** where an orchestrator spawns specialised subagents:

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles, skips seen ones
├── .claude/agents/trending-tracker.md   → finds trending AI keyword phrases
├── .claude/agents/post-generator.md     → writes & saves drafts, updates memory
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and input/output contract. Edit any agent file to change how that step behaves — no code changes needed.

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code will read `orchestrator.md` and execute the full pipeline:
1. Spawns **news-gatherer** → reads RSS feeds, returns scored articles (skipping already-processed ones)
2. Spawns **trending-tracker** → searches for trending AI topics
3. For each article cluster, spawns **post-generator** → writes and saves a draft, updates memory
4. Spawns **notion-publisher** → pushes drafts to Notion (if `NOTION_PAGE_ID` is set)

### Custom parameters

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Configuration — Everything You Can Edit

All settings live in `config/`. **Edit these files directly** — changes take effect on the next run.

### `config/brand_kit.yaml` — Your Voice & Brand
The most important file. Controls how every post is written.

| Section | What to edit |
|---------|-------------|
| `author` | Your name, title, tagline, location — **fill these in first** |
| `tone_of_voice.primary_traits` | How you come across — curious, pragmatic, opinionated, etc. |
| `tone_of_voice.writing_style` | Rules for every post — paragraph length, hook style, emoji use |
| `tone_of_voice.post_structure` | The blueprint every post follows (HOOK → CONTEXT → EVIDENCE → YOUR TAKE → SO WHAT → CTA) |
| `tone_of_voice.dos` / `donts` | What makes your posts great vs. what undermines them |
| `brand.focus_areas` | The lenses you write through — practical AI tools, human-in-loop workflows, etc. |
| `brand.content_angles` | Your favourite post angles — "I tried X for Y — here's what happened" |
| `brand.hashtags` | Always-include + rotation pool; set `max_hashtags` |
| `brand.post_length` | `short` (300–500 chars) / `medium` (500–900) / `long` (900–1300) |
| `research_standards.min_sources` | Minimum sources cited per post (default 4) |

### `config/topics.yaml` — What News to Track
Controls which companies and topics the news-gatherer looks for.

| Section | What to edit |
|---------|-------------|
| `companies_to_track.ai_labs` | AI labs to follow: OpenAI, Anthropic, Gemini, ElevenLabs, Midjourney, etc. |
| `companies_to_track.ai_builders` | AI infrastructure & tool companies: Cursor, Scale AI, Harvey, etc. |
| `companies_to_track.big_tech` | Microsoft, Apple, Amazon, Nvidia, Salesforce, Adobe |
| `topic_categories` | Scoring categories: Product Launches, Funding, Marketing, Research, Regulation, Productivity |
| `freshness.max_article_age_hours` | Only articles published this recently (default 48h) |
| `freshness.min_relevance_score` | Minimum score to include an article (default 2) |
| `freshness.max_articles_per_run` | Cap articles fetched per run (default 25) |

### `config/sources.yaml` — News Feeds
Controls which RSS feeds are fetched.

| Section | What to edit |
|---------|-------------|
| `rss_feeds.ai_news` | General AI news: TechCrunch, The Verge, VentureBeat, Wired, MIT Tech Review |
| `rss_feeds.company_blogs` | Official blogs: OpenAI, Anthropic, Google AI, DeepMind, Meta, ElevenLabs, etc. |
| `rss_feeds.funding_news` | Startup & funding: TechCrunch Startups, Crunchbase, SiliconAngle |
| `rss_feeds.youtube_channels` | YouTube RSS feeds for AI channels |
| `optional_apis.newsapi` | NewsAPI (requires free key at newsapi.org) |

To add any RSS feed:
```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high    # high / medium / low
      enabled: true
```

### `config/seen_articles.yaml` — Cross-Run Memory
Tracks which article URLs have already been turned into posts. Automatically updated after each run.

- **To reset** (allow all articles again): change `seen_urls` to `[]`
- **To un-skip a specific article**: delete its URL line
- **To inspect**: open the file and review which stories have been covered

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# Required for Notion publishing (optional feature)
NOTION_PAGE_ID=your_32char_page_id_here

# Optional: direct Notion REST API fallback
NOTION_API_KEY=secret_xxx

# Optional: NewsAPI for additional sources
NEWSAPI_KEY=your_key_here
```

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-35-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft — review and publish when ready

Change `status: draft` to `status: published` to track what's gone live.

---

## Agents Reference

### `news-gatherer`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`, `config/seen_articles.yaml`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, skips already-seen articles, returns top articles as JSON

### `trending-tracker`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days

### `post-generator`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`
- **Writes**: `posts/<filename>.md`, `config/seen_articles.yaml`
- **Does**: Synthesises a cluster of articles into a branded LinkedIn post, validates URLs, saves as `.md` draft, appends article URLs to memory

### `notion-publisher`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a toggle block on a Notion page

---

## Customising Your Brand

Edit `config/brand_kit.yaml` — the agent reads it on every run, no restart needed.

1. **Fill in `author`** — your real name, title, and tagline
2. **Tune `tone_of_voice`** — adjust the traits and writing style rules to match your actual voice
3. **Update `brand.focus_areas`** — the angles you care about most
4. **Set `post_length`** — `medium` works well for most LinkedIn content

---

## Typical Post Flow

```
News is fetched + scored
      ↓
Already-seen articles are filtered out
      ↓
Trending keywords are identified
      ↓
Articles are clustered (6 per post)
      ↓
Post is generated in your voice with citations
      ↓
Draft saved to posts/ + memory updated
      ↓
(Optional) Pushed to Notion
      ↓
You review, edit, and publish
```
