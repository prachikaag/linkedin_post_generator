# LinkedIn Post Generator

Monitors AI news from 25+ sources, tracks what's trending, and drafts LinkedIn posts in your voice — with cited sources, personal experiment references, and the right angle for each type of news.

You are always in the loop. The tool drafts; you decide what ships.

## How it works

1. **Fetches news** from curated RSS feeds — TechCrunch, VentureBeat, company blogs (OpenAI, Anthropic, Google DeepMind, ElevenLabs…), funding news, and YouTube channel updates
2. **Scores articles** by relevance to your tracked companies and topic categories
3. **Pulls trending keywords** via Claude WebSearch to understand what people are searching right now
4. **Selects a post angle** — automatically matches each article cluster to the right template (Feature Launch, YouTube Video, Funding News, Big Tech Move, Personal Experiment, etc.)
5. **Injects your experiments** — if you've personally tried a tool that's in the news, your real finding gets woven in as first-person evidence
6. **Generates draft posts** via Claude, following your brand kit and tone of voice exactly
7. **Saves drafts** as markdown files in `/posts/` for you to review, edit, and publish
8. **Optionally pushes to Notion** for a shared draft board

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY if running outside Claude Code

# 3. Personalise your config (most important step)
#    See "Config files" below

# 4. Run
python main.py run
```

If you're running inside **Claude Code**, no API key is needed — it uses the active session automatically.

## Usage

```bash
# Generate up to 3 posts from today's top AI news
python main.py run

# Generate up to 5 posts
python main.py run --max-posts 5

# See what news would be picked, without generating posts
python main.py run --dry-run

# List all saved draft posts
python main.py list-posts

# Read a specific draft
python main.py show 1
python main.py show --file posts/2025-05-01_10-30-00_openai-launches.md

# Show paths to all config files
python main.py config
```

---

## Config files — everything editable, nothing hardcoded

All six files live in `config/`. Each controls a distinct part of the system. Change any of them and every future run adapts instantly.

### `config/brand_kit.yaml`
**Who you are, what you write about, your hashtag strategy.**

Fill in your name, title, and tagline. Adjust the `focus_areas` to describe your professional lens. Tweak the `hashtags` list. Set `post_length` to `short`, `medium`, or `long`.

```yaml
author:
  name: "Your Name"
  title: "Brand Strategist | AI Enthusiast"
  tagline: "Helping brands understand and leverage AI in the real world"
```

---

### `config/tone_of_voice.yaml`
**How every post sounds — your style, structure, rules.**

This controls the actual writing. Edit `primary_traits` to describe your voice. Edit `writing_style` to add or remove writing rules. Edit `post_structure` to change the sections in every post. Edit `dos` and `donts` to enforce your own standards.

```yaml
primary_traits:
  - "Curious and experimental — you try AI tools yourself and share honest results"
  - "Pragmatic — you always connect AI news to real brand outcomes"
```

---

### `config/post_templates.yaml`
**Per-angle framing for different types of news.**

Each template activates when its `trigger_keywords` match the article cluster. The `framing` text gets injected into the generation prompt to steer the post angle. Add your own templates or edit the framing on existing ones.

Templates included:
- **Feature or Product Launch** — what the feature unlocks for brands
- **YouTube Video Release** — "just watched" reaction post
- **AI Startup Funding** — what the investment signals about the market
- **Big Tech AI Move** — second-order effects on brands already using these platforms
- **AI Research Breakthrough** — plain-language implication for marketers
- **Personal AI Experiment** — honest first-person results post
- **AI Industry Trend** — connecting the dots across multiple signals
- **AI Regulation and Ethics** — practical implications for brand legal and marketing teams

---

### `config/my_experiments.yaml`
**Your personal AI experiments log.**

This is what makes your posts genuinely different. Every entry you add here is a potential first-person data point the generator can weave into a relevant post. When a post is about a tool you've experimented with, your real finding gets referenced as authentic evidence.

```yaml
experiments:
  - date: "2025-05-01"
    tool: "Claude"
    use_case: "Writing brand strategy briefs from a client questionnaire"
    what_happened: "80% complete brief in 5 minutes vs 2 hours from scratch"
    verdict: "positive"
    time_saved: "~1.5–2 hours per brief"
    usable_in_posts: true
    tags:
      - "brand strategy"
      - "workflow"
```

Add entries for every tool you try. Set `usable_in_posts: false` to keep private experiments out of posts.

---

### `config/topics.yaml`
**Companies and keywords to track.**

Add any company under `companies_to_track`. The keywords you list are what the scorer looks for in article titles and summaries. Add topic categories with their keywords to score articles by type (Funding, Launch, Marketing, etc.).

Companies already tracked: OpenAI, Anthropic, Google DeepMind, Perplexity, ElevenLabs, Midjourney, Stability AI, xAI, Meta AI, Mistral, Runway, Pika, Microsoft, Apple, Amazon, Nvidia, Salesforce, Adobe, and more.

```yaml
companies_to_track:
  ai_labs:
    - name: "ElevenLabs"
      keywords:
        - "ElevenLabs"
        - "voice AI"
        - "AI voice cloning"
```

---

### `config/sources.yaml`
**RSS feeds and optional APIs.**

Add any RSS feed by dropping it into the right category. Set `priority: high` for feeds fetched first, `enabled: false` to pause a feed without deleting it.

YouTube channel RSS feeds are already included for Google DeepMind, OpenAI, and Anthropic — video releases flow through the same pipeline and get matched to the YouTube Video template automatically.

```yaml
rss_feeds:
  youtube_channels:
    - name: "OpenAI YouTube"
      url: "https://www.youtube.com/feeds/videos.xml?channel_id=UCXZCJLdBC09xxGZ6gcdrc6A"
      priority: medium
      enabled: true
```

Optional: add a free [NewsAPI](https://newsapi.org/) key in `.env` and set `enabled: true` under `optional_apis.newsapi` in this file for broader coverage.

---

## Generated posts

Posts are saved in `posts/` as markdown files with YAML frontmatter:

```
posts/
  2025-05-13_10-30-00_openai-launches-new-model.md
  2025-05-13_10-30-05_elevenlabs-raises-series-b.md
```

Each file includes the post draft plus metadata: primary source URL, all cited sources, matched companies, trending keywords, post angle, relevance score, and status. Edit the file directly before posting. Change `status: draft` to `status: published` to track what's gone live.

---

## Optional: Notion integration

Set `NOTION_API_KEY` and `NOTION_PAGE_ID` in `.env` to push every draft to a Notion page automatically. Setup instructions are in `.env.example`.
