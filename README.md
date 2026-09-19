# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — built entirely with Claude Code agents. No traditional code steps.

---

## What This Does

1. Reads your **topics of interest** and **brand guidelines**
2. Fetches **fresh AI news** from RSS feeds and YouTube channels
3. Tracks **trending keywords** across the web
4. Generates **LinkedIn posts** in your voice — cited sources included
5. Skips stories **already covered** (so every run produces fresh content)
6. Publishes drafts to **Notion** (optional) and saves them to `posts/`

---

## Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md         → fetches + scores RSS articles, skips seen URLs
├── .claude/agents/trending-tracker.md      → finds trending keyword phrases
├── .claude/agents/post-generator.md        → writes & saves LinkedIn post drafts
├── .claude/agents/experiment-post-generator.md → writes "I tried X" posts from your experiments
└── .claude/agents/notion-publisher.md      → publishes drafts to Notion (optional)

config/
├── topics.yaml            ← Edit: companies and topics to track
├── sources.yaml           ← Edit: RSS feeds and YouTube channels
├── brand_kit.yaml         ← Edit: your name, voice, and writing style
└── human_experiments.yaml ← Edit: AI tools you're personally testing

data/
└── seen_stories.json      ← Auto-managed: URLs already used in posts (edit to reset memory)

posts/                     ← Output: generated draft posts as .md files
```

Each file is independent and editable. Changing a config file takes effect on the next run.

---

## How to Run

### In Claude Code (primary method)

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or be more specific:

```
Run the pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts yet.
```

```
Generate an experiment post about my ElevenLabs testing.
```

Claude Code reads `orchestrator.md` and runs the full pipeline:
1. **news-gatherer** → fetches fresh RSS articles, skips already-seen stories
2. **trending-tracker** → finds what's buzzing in AI this week
3. **post-generator** (×N) → writes branded posts with cited sources
4. **memory update** → records covered URLs so next run is always fresh
5. **notion-publisher** → pushes drafts to Notion (if configured)

---

## Configuration Files

All editable settings live in `config/`. Change any file — no restart needed.

### `config/topics.yaml`
Controls what news gets tracked and how it's scored.

**Edit this to:**
- Add new companies to watch (AI startups, tools you're following)
- Add new topic categories (e.g. "AI in Healthcare", "AI Ethics")
- Adjust freshness settings (how old an article can be)
- Change scoring weights

**Structure:**
```yaml
companies_to_track:
  ai_labs:
    - name: "OpenAI"
      keywords: ["ChatGPT", "GPT-5", "Operator", ...]  # +3 score per match
  big_tech:
    - name: "Microsoft"
      keywords: ["Microsoft Copilot", "Azure AI", ...]

topic_categories:
  - name: "AI Startup Funding"
    keywords: ["funding", "Series A", "raises", ...]    # +1 score per match

freshness:
  max_article_age_hours: 48   # Only articles from the last N hours
  min_relevance_score: 2      # Minimum score to include an article
  max_articles_per_run: 25    # Cap per pipeline run
```

---

### `config/sources.yaml`
Controls which RSS feeds and YouTube channels are fetched.

**Edit this to:**
- Add new news sources (any RSS feed URL works)
- Add YouTube channels (the pipeline tracks new video uploads)
- Disable sources temporarily (`enabled: false`)
- Adjust priority (high sources are fetched first)

**Add any RSS feed:**
```yaml
rss_feeds:
  ai_news:
    - name: "My Source"
      url: "https://example.com/feed.xml"
      priority: high    # high | medium | low
      enabled: true
```

**Feeds already configured:**
- TechCrunch AI, The Verge, VentureBeat, Wired, MIT Tech Review
- OpenAI Blog, Anthropic Blog, Google AI, DeepMind, Meta AI, Microsoft AI
- TechCrunch Startups, Crunchbase News, SiliconAngle (for funding news)
- YouTube: Google DeepMind, OpenAI, Anthropic, Two Minute Papers

---

### `config/brand_kit.yaml`
The most important file — defines how your posts are written.

**Edit this to:**
- Update your name, title, and tagline
- Adjust your tone traits (curious / pragmatic / opinionated etc.)
- Add or change your writing style rules
- Update focus areas as your positioning evolves
- Add signature phrases that are distinctly yours
- Change hashtag strategy

**Key sections:**
```yaml
author:
  name: "Prachi Kaag"
  title: "Brand Strategist | AI Practitioner"
  tagline: "Helping brands understand and leverage AI in the real world"

tone_of_voice:
  primary_traits: [...]    # How you come across
  writing_style: [...]     # Rules applied to every post
  post_structure: [...]    # The ordered blueprint for every post
  dos: [...]               # What makes a great post from you
  donts: [...]             # What undermines your credibility

brand:
  focus_areas: [...]       # The lenses you write through
  content_angles: [...]    # Angle templates for posts
  hashtags:
    always_include: ["#AI", "#ArtificialIntelligence"]
    rotate_from: [...]     # Pool to pick from per post
  post_length: "medium"    # short | medium | long
```

---

### `config/human_experiments.yaml`
Tracks your hands-on AI tool experiments so the pipeline can write "I tried X" style posts.

**Edit this to:**
- Add new tools you're testing (`active_experiments`)
- Record your honest verdict, what worked, and what didn't
- Add specific post angles for each tool
- Move completed experiments to `completed_experiments`
- Queue tools you plan to test in `upcoming_experiments`

**Structure:**
```yaml
active_experiments:
  - tool: "Claude"
    vendor: "Anthropic"
    use_case: "Brand strategy briefs"
    honest_verdict: "Best for long-form strategic thinking..."
    best_for: "Strategy docs, briefing frameworks"
    limitations: "Less snappy for short punchy copy without tight prompting"
    would_recommend_to: "Brand strategists, senior marketers"
    post_angles:
      - "How I use Claude to write brand strategy briefs in 30 minutes"
```

**To generate an experiment post:**
```
Generate an experiment post about my Claude testing.
```

---

## Memory (Seen Stories)

`data/seen_stories.json` is automatically maintained by the pipeline.

After every run, the URLs of all articles used in generated posts are recorded here. On the next run, the news-gatherer skips any article whose URL is already in this file — ensuring every post covers fresh ground.

**To reset memory** (re-cover any story): Edit `data/seen_stories.json` and remove URLs from the `seen_urls` array.

**To clear all memory**: Replace `seen_urls` with an empty array `[]`.

---

## Output

Generated posts are saved to `posts/` as Markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-35-00_anthropic-funding-round.md
  2024-01-15_11-00-00_experiment-elevenlabs.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

**Workflow:**
1. Pipeline saves posts with `status: draft`
2. You review and edit in the `posts/` folder
3. Change `status: draft` to `status: published` to track what's gone live
4. Posts are plain Markdown — paste directly into LinkedIn, no reformatting needed

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `NOTION_PAGE_ID` | Optional | Pushes posts to your Notion page |
| `NOTION_API_KEY` | Optional | Direct Notion REST API (fallback) |
| `NEWSAPI_KEY` | Optional | Additional news sources via NewsAPI |

Notion is the only integration that requires setup. Without it, posts are saved locally to `posts/` — which is fine.

---

## Agents Reference

| Agent | Reads | Does | Output |
|-------|-------|------|--------|
| `news-gatherer` | `config/sources.yaml`, `config/topics.yaml`, `data/seen_stories.json` | Fetches RSS feeds, scores articles, skips seen URLs | JSON array of articles |
| `trending-tracker` | `config/topics.yaml` | Searches web for trending AI topics | JSON array of keyword phrases |
| `post-generator` | `config/brand_kit.yaml` | Writes branded post from article cluster | Saved `.md` + JSON metadata |
| `experiment-post-generator` | `config/brand_kit.yaml`, `config/human_experiments.yaml` | Writes "I tried X" post from your experiment notes | Saved `.md` + JSON metadata |
| `notion-publisher` | Notion MCP | Appends post as toggle block to Notion page | `success` or `failed` |

---

## Customising

**Add a topic to track:**
Edit `config/topics.yaml` → `companies_to_track` or `topic_categories`

**Add a news source:**
Edit `config/sources.yaml` → add an RSS feed entry with `enabled: true`

**Change your writing style:**
Edit `config/brand_kit.yaml` → `tone_of_voice.writing_style`

**Track a new AI tool experiment:**
Edit `config/human_experiments.yaml` → add to `active_experiments`

**Reset seen stories:**
Edit `data/seen_stories.json` → clear `seen_urls`

**Generate more posts per run:**
Say "Generate 5 posts" or set `MAX_POSTS` in your prompt to the orchestrator
