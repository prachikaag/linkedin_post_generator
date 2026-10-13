# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — tailored to your brand voice and the type of news you're covering.

---

## What it does

1. **Reads your topics** — monitors companies like OpenAI, Claude, Perplexity, Gemini, ElevenLabs, Midjourney, plus all major big tech and AI startup news
2. **Fetches fresh news** — pulls from curated RSS feeds every run
3. **Tracks what's trending** — finds the most-discussed AI topics of the past 7 days
4. **Detects the post type** — auto-classifies each story as a feature launch, funding news, big tech move, YouTube release, or experiment
5. **Writes in your voice** — uses your brand kit and tone to draft posts with cited sources
6. **Saves drafts** — each post lands in `posts/` as a markdown file, ready to review and publish

---

## Editable Components

All the parts you'll want to customise live in `config/`. Edit any file and the next run picks up the changes — no restarts needed.

| File | What you edit |
|------|---------------|
| `config/persona.yaml` | Your name, title, bio, audience, LinkedIn headline |
| `config/brand_kit.yaml` | Writing style rules, post structure, hashtags, length |
| `config/post_types.yaml` | Templates per post type — hooks, angles, CTAs, hashtags |
| `config/topics.yaml` | Companies, AI tools, and keywords to track |
| `config/sources.yaml` | RSS feeds and news sources |

### `config/persona.yaml` — Start here
Fill in your name, title, bio, and who your audience is. This drives how the author voice sounds in every post.

### `config/brand_kit.yaml` — Tone and style
Controls your writing style rules, post structure blueprint, hashtag strategy, and what not to say. Edit `tone_of_voice.writing_style` to adjust sentence length, paragraph count, emoji rules etc.

### `config/post_types.yaml` — Five post formats
Each post type has its own hook guidance, angle, CTA examples, and hashtags:

| Type | Triggered by |
|------|-------------|
| `feature_launch` | OpenAI/Claude/Gemini/Perplexity etc. launches feature or model |
| `startup_funding` | AI startup raises funding, gets acquired, or IPOs |
| `big_tech_ai` | Microsoft/Google/Apple/Amazon/Nvidia makes AI move |
| `youtube_release` | AI company ships a YouTube demo or announcement |
| `personal_experiment` | You tried an AI tool and want to share honest results |

### `config/topics.yaml` — What to track
Add any company, product, or keyword. Articles that match get a higher relevance score and are more likely to be used for post generation.

### `config/sources.yaml` — News feeds
Add any RSS feed. Set `enabled: false` to skip without deleting. Priority (`high`, `medium`, `low`) controls fetch order.

---

## Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → detects post type, writes & saves drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file. The orchestrator passes data between them.

---

## How to Run

### Option 1 — Inside Claude Code (recommended)

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Or with options:
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
Run the pipeline in dry-run mode.
Run the pipeline and force post type: startup_funding
```

### Option 2 — Python runner

```bash
# Basic run (2 posts, auto-detect type)
python run_pipeline.py

# Generate 3 posts
python run_pipeline.py --posts 3

# Dry run — fetch news only, no post generation
python run_pipeline.py --dry-run

# Force a specific post type for all posts
python run_pipeline.py --post-type startup_funding
python run_pipeline.py --post-type feature_launch
python run_pipeline.py --post-type big_tech_ai
python run_pipeline.py --post-type youtube_release
python run_pipeline.py --post-type personal_experiment

# Full options
python run_pipeline.py --posts 3 --pool 8 --post-type feature_launch
```

---

## Setup

1. Copy `.env.example` to `.env`
2. Fill in your details:

```bash
# Required for standalone use (not needed inside Claude Code)
ANTHROPIC_API_KEY=sk-ant-...

# Optional: publish drafts to Notion
NOTION_PAGE_ID=your_32char_notion_page_id
NOTION_API_KEY=secret_...

# Optional: additional news sources
NEWSAPI_KEY=your_newsapi_key
```

3. Edit `config/persona.yaml` with your real name, title, and bio
4. Optionally adjust `config/brand_kit.yaml` for your exact writing style
5. Run the pipeline

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2024-01-15_10-30-00_openai-launches-gpt5.md
  2024-01-15_10-32-00_anthropic-funding-round.md
```

Each file contains:
- **YAML frontmatter** — post type, source metadata, matched companies, categories, status
- **Post body** — full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Post Types Reference

### Feature Launch
For when ChatGPT, Claude, Perplexity, Gemini, ElevenLabs, Midjourney etc. ship a new feature or model.

**Default angle**: What does this mean for brand and marketing workflows?

**Example hook**: "This week's AI releases change how brand teams approach [task]."

---

### Startup Funding
For AI startup funding rounds, acquisitions, IPOs.

**Default angle**: What does the money tell us about where AI is heading?

**Example hook**: "Investors just placed a $X bet on [category] — here's what that tells us."

---

### Big Tech AI
For Microsoft, Google, Apple, Amazon, Nvidia, Salesforce, Adobe AI news.

**Default angle**: What does this mean for brands using that company's existing products?

**Example hook**: "If your team uses Microsoft 365, something changed this week."

---

### YouTube Release
For when an AI company ships a YouTube video (demo, announcement, research explainer).

**Default angle**: What does the demo actually show — and what are the brand implications?

**Example hook**: "I just watched [company]'s new demo — one part changed how I think about [capability]."

---

### Personal Experiment
For sharing honest results from your own AI testing. Most authentic to your brand.

**Default angle**: What actually happened when you tried it for a real task?

**Example hook**: "I gave an AI tool one of my most tedious brand research tasks — here's what happened."
