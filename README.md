# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks what's trending, and writes research-backed LinkedIn posts in your voice — with cited sources. Runs entirely inside Claude Code as a multi-agent system. No Python required.

---

## What It Does

1. **Fetches fresh AI news** from 20+ RSS feeds and company blogs (TechCrunch, VentureBeat, Anthropic, OpenAI, ElevenLabs, etc.)
2. **Tracks trending keywords** across the web for the past 7 days
3. **Scores articles** by relevance to your tracked companies and topics
4. **Picks the right post format** based on the story type (feature launch, funding news, YouTube reaction, personal experiment, big tech move, or weekly roundup)
5. **Writes a LinkedIn post** that synthesises multiple sources, follows your brand voice, and cites every source
6. **Saves drafts** to `posts/` as markdown files with full metadata
7. **Optionally pushes to Notion** for review before publishing

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude reads `orchestrator.md` and runs the full pipeline.

### Useful variations:

```
Run the LinkedIn Post Generator. Generate 3 posts.
```

```
Run the pipeline with the funding_news template for all posts.
```

```
Run the pipeline in dry-run mode — fetch and score news only, don't generate posts.
```

```
Run the pipeline. Use the personal_experiment template for the first post.
```

```
Run the pipeline. Use 8 articles per cluster.
```

---

## File Structure — Your Editable Components

Everything you need to customise lives in `config/`. Each file is a separate component you can edit independently.

```
config/
  topics.yaml          → What to track: AI companies, keywords, topic categories
  sources.yaml         → Where to get news: RSS feeds, YouTube channels, APIs
  brand_kit.yaml       → How to write: your voice, tone, style, structure, hashtags
  post_templates.yaml  → What format: 6 post types with hooks, angles, and structure
  my_experiments.yaml  → Your personal voice: real experiments, hot takes, opinions
```

### `config/topics.yaml`
Controls **what news gets tracked and scored**. Add/remove companies, keywords, and categories. Higher keyword matches → higher relevance score → included in posts.

Key settings:
- `companies_to_track` — the AI companies you want to write about (OpenAI, Anthropic, ElevenLabs, Midjourney, etc.)
- `topic_categories` — what types of stories count (launches, funding, marketing, research, etc.)
- `freshness.max_article_age_hours` — how old articles can be (default: 48 hours)
- `freshness.min_relevance_score` — minimum score to include (default: 2)

### `config/sources.yaml`
Controls **where news is fetched from**. Toggle individual feeds with `enabled: true/false`. Add any RSS feed URL.

Includes: TechCrunch AI, The Verge AI, VentureBeat, Wired, MIT Tech Review, OpenAI Blog, Anthropic Blog, Google AI Blog, DeepMind, Meta AI, ElevenLabs, Mistral, Perplexity, Crunchbase, and YouTube channels for major AI companies.

To add a source:
```yaml
rss_feeds:
  ai_news:
    - name: "My New Source"
      url: "https://example.com/feed.xml"
      priority: high   # high / medium / low
      enabled: true
```

### `config/brand_kit.yaml`
Controls **how every post is written**. This is the most important file for making posts sound like you.

Key sections:
- `author` — your name, title, and tagline ← **fill this in first**
- `tone_of_voice.primary_traits` — how you come across to your audience
- `tone_of_voice.writing_style` — specific rules for every sentence
- `tone_of_voice.post_structure` — the ordered blueprint for every post
- `tone_of_voice.dos` and `donts` — what makes a post great vs. what undermines it
- `brand.hashtags` — always-include hashtags and rotation pool
- `brand.post_length` — target length (short / medium / long)
- `research_standards.min_sources` — minimum sources per post (default: 4)

### `config/post_templates.yaml`
Controls **what kind of post gets written** based on the news type.

6 templates — each with a distinct hook style, angle, and structure:

| Template ID | When It's Used | Example Hook |
|---|---|---|
| `feature_launch` | New AI model or feature released | "The gap between what AI could do and what it can do just narrowed — again." |
| `youtube_reaction` | AI company ships a demo video | "I watched [company]'s new video twice. Here's the moment that got me." |
| `funding_news` | AI startup funding or acquisition | "When serious investors write large cheques into one category, they're making a directional bet." |
| `bigtech_move` | Microsoft / Google / Apple / Meta AI news | "When AI ships inside tools a billion people already use, the adoption question disappears." |
| `personal_experiment` | I tested this — honest results | "I spent [time] doing [task] with AI instead of [old way]. Here's what I found." |
| `weekly_roundup` | Multiple stories forming one pattern | "Five things happened in AI this week. They look unrelated. They're not." |

The pipeline auto-selects the best template based on keywords in the top article. You can override it by saying "use the funding_news template" when running the pipeline.

### `config/my_experiments.yaml` ← **Update this regularly**
This is the "human in the loop" layer — your personal voice file.

The post-generator reads this file on every run and weaves your real experiments, opinions, and observations into the posts. This is what makes the posts sound like you, not a generic AI summary.

Sections to fill in:
- `tools_in_my_workflow` — what AI tools you actually use and what you've learned
- `recent_experiments` — your real AI tests: what you tried, what happened, what you learned
- `hot_takes` — your strong opinions on AI (contrarian takes welcome)
- `watching` — what you're paying attention to right now
- `company_takes` — your honest public opinions on OpenAI, Anthropic, Perplexity, etc.

**The more specific and recent your entries, the better the posts sound.**

---

## First-Time Setup

### Step 1 — Fill in your brand kit

Open `config/brand_kit.yaml` and update the `author` section:

```yaml
author:
  name: "Prachi"
  last_name: "Your Last Name"
  title: "Your Title — e.g. Brand Strategist | AI Enthusiast"
  tagline: "Helping brands understand and leverage AI in the real world"
  location: "Your City, Country"
```

### Step 2 — Add your personal voice

Open `config/my_experiments.yaml` and add:
- At least one real AI experiment you've done recently
- 2–3 of your honest hot takes on AI
- Your takes on the companies you want to write about

This takes 10–15 minutes and makes every post significantly more personal.

### Step 3 — Configure environment variables (optional)

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Fill in what you want to use:
- `NOTION_PAGE_ID` — to automatically push drafts to a Notion page for review
- `NEWSAPI_KEY` — for broader news coverage via the NewsAPI (free tier available)

Neither is required. Without them, posts are saved locally to `posts/`.

### Step 4 — Run it

```
Run the LinkedIn Post Generator pipeline.
```

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2026-05-21_09-00-00_openai-launches-gpt5-model.md
  2026-05-21_09-01-00_anthropic-raises-funding-round.md
```

Each file contains:
- **YAML frontmatter**: source metadata, template used, companies, categories, status
- **Post body**: the full LinkedIn draft, ready to review and publish

When you publish a post, change `status: draft` to `status: published` to track it.

---

## Understanding the Post Structure

Every post follows this structure (set in `brand_kit.yaml` and shaped by the chosen template):

```
HOOK        → Stops the scroll. Never starts with "I".
CONTEXT     → What's happening broadly, not just one story.
EVIDENCE    → Data, quotes, developments from multiple sources.
YOUR TAKE   → Your synthesis and opinion. The most important part.
SO WHAT     → What brands or marketers should do about it.
CTA         → A question that invites discussion.
SOURCES     → Numbered list with full URLs.
HASHTAGS    → 4–5 relevant hashtags.
```

---

## Agents Reference

### `orchestrator.md`
The master pipeline. Reads all config, spawns subagents, passes data between them, prints a summary. This is what runs when you say "Run the LinkedIn Post Generator pipeline."

### `.claude/agents/news-gatherer.md`
- **Tools**: Read, WebFetch
- **Reads**: `config/sources.yaml`, `config/topics.yaml`
- **Does**: Fetches all enabled RSS feeds, scores articles by keyword relevance, deduplicates, returns top articles as JSON

### `.claude/agents/trending-tracker.md`
- **Tools**: Read, WebSearch
- **Reads**: `config/topics.yaml`
- **Does**: Searches the web for trending AI topics from the past 7 days across multiple angles (launches, funding, research, regulation)

### `.claude/agents/post-generator.md`
- **Tools**: Read, Write
- **Reads**: `config/brand_kit.yaml`, `config/post_templates.yaml`, `config/my_experiments.yaml`
- **Does**: Selects the best template, loads personal voice from experiments, writes a branded post, validates URLs, saves as `.md` draft

### `.claude/agents/notion-publisher.md`
- **Tools**: Read, Notion MCP
- **Does**: Appends the post as a collapsible toggle block on a Notion page for review
- **Requires**: `NOTION_PAGE_ID` set in `.env`

---

## Customising Your Content Strategy

### To track a new AI company or tool:

Add to `config/topics.yaml` under `companies_to_track`:
```yaml
- name: "New Company"
  keywords:
    - "NewCompany"
    - "their product name"
    - "their model name"
```

### To add a news source:

Add to `config/sources.yaml` under the appropriate category:
```yaml
- name: "Source Name"
  url: "https://example.com/feed.xml"
  priority: high
  enabled: true
```

### To change how posts are written:

Edit `config/brand_kit.yaml`:
- `tone_of_voice.writing_style` — change the sentence rules
- `tone_of_voice.post_structure` — change what goes in each section
- `brand.post_length` — change target length (short / medium / long)
- `brand.hashtags.rotate_from` — add or remove hashtags from the rotation

### To force a specific post format:

When running the pipeline, specify the template:
```
Run the LinkedIn Post Generator. Use the personal_experiment template.
```

Or:
```
Run the pipeline. Generate 2 posts — use funding_news for both.
```

### To add your own post template:

Add a new entry to `config/post_templates.yaml` following the existing structure. Give it a unique `id` and add it to `selection_rules.priority_order`.
