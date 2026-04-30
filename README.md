# LinkedIn Post Generator

An AI-powered system that monitors AI news, tracks what's trending, and drafts opinionated LinkedIn posts in your voice — with cited sources, woven with your personal AI experiments, ready for your review before anything goes live.

**You are always the editor. The tool drafts; you decide what ships.**

---

## How It Works

```
config/topics.yaml        → What companies and topics to watch
config/sources.yaml       → Which RSS feeds and APIs to pull from
config/brand_kit.yaml     → Your voice, tone, writing style, and hashtags
config/my_experiments.yaml → Your personal AI experiments (human-in-the-loop)
config/post_ideas.yaml    → Your pre-written angles and talking points
         ↓
[News Fetcher]  Pulls latest articles from RSS feeds (TechCrunch, VentureBeat,
                company blogs, YouTube channels, funding news, etc.)
         ↓
[Relevance Scorer]  Scores each article against your tracked companies
                    and topic categories
         ↓
[Trending Tracker]  Finds what's trending in AI via web search
         ↓
[Post Generator]  Claude writes a research-style post synthesising 6 sources,
                  matching your tone, weaving in your experiments and angles
         ↓
posts/  → Draft markdown files for you to edit and publish
         ↓ (optional)
Notion  → Pushed directly to your LinkedIn Post Ideas page
```

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy the env file and add your API key
cp .env.example .env
# Edit .env — paste your ANTHROPIC_API_KEY
# (Not needed if running inside Claude Code — it connects automatically)

# 3. Personalise your config (do this before first run)
nano config/brand_kit.yaml     # Your name, title, tone, hashtags
nano config/topics.yaml        # Companies and topics to track
nano config/my_experiments.yaml  # Your personal AI experiments
```

---

## Running the Pipeline

```bash
# Generate up to 3 posts from today's top AI news
python main.py run

# Generate more posts in one run
python main.py run --max-posts 5

# See what news would be fetched without generating posts
python main.py run --dry-run

# List all saved drafts
python main.py list-posts

# Read a specific draft
python main.py show 1

# Show all config file paths
python main.py config
```

Or use the minimal runner (no click/rich required):

```bash
python run_pipeline.py
```

---

## The 7 Components — Edit These to Customise Everything

### 1. `config/topics.yaml` — What to Track

Controls what news gets fetched and scored.

```yaml
companies_to_track:
  ai_labs:
    - name: "OpenAI"
      keywords: ["OpenAI", "ChatGPT", "GPT-5", "Sora"]

topic_categories:
  - name: "AI Startup Funding"
    keywords: ["funding", "raises", "Series A", "valuation"]

freshness:
  max_article_age_hours: 48   # Only articles from the last 48 hours
  min_relevance_score: 2      # Minimum score to include an article
  max_articles_per_run: 25    # Total articles scored per run
```

**Add a company:** Copy an existing entry under `ai_labs` or `big_tech`, change the name and keywords, save.

**Add a topic category:** Copy an existing category entry, update the name, description, and keywords list.

---

### 2. `config/sources.yaml` — Where News Comes From

All the RSS feeds, company blogs, YouTube channels, and optional APIs the news fetcher pulls from.

```yaml
rss_feeds:
  ai_news:
    - name: "TechCrunch AI"
      url: "https://techcrunch.com/category/artificial-intelligence/feed/"
      priority: high    # high | medium | low
      enabled: true     # set false to pause without deleting

  company_blogs:
    - name: "Anthropic Blog"
      url: "https://www.anthropic.com/rss.xml"
      priority: high
      enabled: true
```

**Add a feed:** Copy any feed entry, fill in `name` and `url`, set `priority` and `enabled: true`.

**Pause a feed:** Set `enabled: false`.

**Optional — NewsAPI:** For broader coverage, get a free key at [newsapi.org](https://newsapi.org/), add `NEWSAPI_KEY` to `.env`, and set `enabled: true` under `optional_apis.newsapi`.

---

### 3. `config/brand_kit.yaml` — Your Voice

This is the most important file. It controls everything about how posts are written.

```yaml
author:
  name: "Your Name"              # ← update this
  title: "Your Professional Title"
  tagline: "Helping brands understand and leverage AI"

tone_of_voice:
  primary_traits:
    - "Curious and experimental — you try AI tools and share honest results"
    - "Pragmatic and business-focused — you connect AI news to real brand outcomes"

  writing_style:
    - "Write in first person. Share personal experiments and real observations."
    - "Short paragraphs only — 1 to 3 sentences max."
    - "Start with a hook. Never start with 'I'."

  post_structure:
    - "HOOK: Bold statement or question that stops the scroll"
    - "CONTEXT: The broader picture across the AI landscape"
    - "EVIDENCE: Data, quotes, developments from multiple sources"
    - "YOUR TAKE: Your synthesis and personal opinion"
    - "SO WHAT: What this means for brands — 1-2 actionable things"
    - "CTA: A question that invites genuine discussion"
    - "SOURCES: Numbered list with full URLs"
    - "HASHTAGS: 4-5 relevant hashtags on the last line"

brand:
  post_length: "medium"   # short (300-500) | medium (500-900) | long (900-1300)
  max_hashtags: 5
  hashtags:
    always_include: ["#AI", "#ArtificialIntelligence"]
    rotate_from: ["#GenerativeAI", "#AITools", "#MarketingAI", ...]
```

**To update your voice:** Edit `primary_traits` and `writing_style` to match how you actually write.

**To change post length:** Set `post_length` to `short`, `medium`, or `long`.

---

### 4. `config/my_experiments.yaml` — Your Personal AI Experiments

**This is the human-in-the-loop component.** When you test an AI tool, log it here. The pipeline automatically detects when news covers that company and weaves your real experience into the "YOUR TAKE" section of the post.

```yaml
experiments:
  - id: exp001
    date: "2025-01-08"
    tool: "ChatGPT"
    company: "OpenAI"
    use_case: "Competitor research brief using Deep Research mode"
    what_i_tried: |
      Used Deep Research to analyse three competitor brands — their messaging,
      content cadence, and audience positioning.
    what_happened: |
      The research output was thorough — about 80% of what a junior strategist
      would produce in half a day. It hallucinated one company claim I had to verify.
    key_takeaway: |
      Use it as a first draft, not a final report. Always fact-check before
      it goes into a client document.
    time_saved_hours: 3
    would_recommend: true
    include_in_posts: true
    tags:
      - research
      - brand strategy
```

**Add an experiment quickly via CLI:**

```bash
python main.py add-experiment
# It will prompt you for each field
```

**Or add directly via CLI flags:**

```bash
python main.py add-experiment \
  --tool "Perplexity" \
  --company "Perplexity" \
  --use-case "Industry landscape research for client brief" \
  --tried "Asked 12 specific questions about AI in retail..." \
  --happened "Surfaced niche trade pubs I wouldn't have found otherwise..." \
  --takeaway "Faster than Google for landscape questions. Always verify paywalled sources." \
  --tags "research,productivity" \
  --hours-saved 2.5
```

**To stop an experiment being used in posts:** Set `include_in_posts: false`.

---

### 5. `config/post_ideas.yaml` — Your Pre-written Angles

Ideas and talking points you've already developed that should be woven into posts when the news is relevant.

```yaml
ideas:
  - id: idea001
    title: "AI doesn't replace the brief — it makes a bad brief painfully obvious"
    status: "queued"       # queued | done | skip
    trigger_keywords:
      - "content creation"
      - "copywriting"
      - "ChatGPT"
    angle: |
      Every time someone says AI-generated content is generic, I ask them what brief
      they gave it. The brands getting the best AI content already had strong brand
      guidelines — not the most expensive tools.
    talking_points:
      - "AI output quality is directly proportional to brief quality"
      - "Prompting is the new briefing"
      - "AI has exposed a widespread problem: brands don't know what they sound like"
```

**How matching works:** When an article's companies/categories overlap with an idea's `trigger_keywords`, that angle is injected into the Claude prompt. The post will reflect your pre-existing thinking, not just what the article says.

**Mark as done:** Change `status: "done"` after you've published a post using that idea.

---

### 6. `posts/` — Generated Draft Posts

Every generated post is saved here as a markdown file with YAML frontmatter:

```
posts/
  2025-01-15_10-30-00_openai-launches-new-model.md
  2025-01-15_10-30-05_elevenlabs-raises-funding.md
```

Each file contains:
- **YAML frontmatter** — source metadata, matched companies, trending keywords, URL validation report
- **The draft post** — ready to copy into LinkedIn

**Workflow:**
1. Run the pipeline
2. Read drafts: `python main.py show 1`
3. Edit the `.md` file directly if needed
4. Copy the post body into LinkedIn
5. Change `status: draft` → `status: published` to track what's been posted

---

### 7. `.env` — API Keys and Model

```bash
# Required for standalone use (not needed inside Claude Code)
ANTHROPIC_API_KEY=sk-ant-...

# Claude model for post generation
# CLI aliases: sonnet | opus | haiku
# SDK full IDs: claude-sonnet-4-6 | claude-opus-4-7 | claude-haiku-4-5-20251001
ANTHROPIC_MODEL=sonnet

# Optional: push drafts to Notion
NOTION_API_KEY=secret_...
NOTION_PAGE_ID=34a50188f130816280e1f9ec2ef84a0c

# Optional: NewsAPI for broader news coverage
NEWSAPI_KEY=...
```

---

## What Gets Written

The pipeline generates posts for three types of stories:

| Story type | What triggers it | What the post covers |
|------------|-----------------|---------------------|
| **New AI feature / product launch** | Any AI company ships something | What it is, practical implication for marketers, your take |
| **AI startup funding** | Funding round, acquisition, valuation news | What the investment signals about where AI is heading |
| **Big tech AI move** | Microsoft, Apple, Google, Amazon, Nvidia | How it affects the marketing/brand landscape |
| **YouTube video / demo** | Company publishes a new video (via YouTube RSS) | What they're showing, what it means for practitioners |
| **Research / breakthrough** | Paper, benchmark, capability milestone | Plain-language explanation + brand/marketing angle |

Posts always cite **minimum 4 sources**, follow the 8-part structure in your brand kit, and end with a question to invite comments.

---

## Notion Integration (Optional)

Generated drafts can be pushed directly to a Notion page for easier review and scheduling.

**Setup:**
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New integration
2. Copy the "Internal Integration Token" → paste as `NOTION_API_KEY` in `.env`
3. Open your LinkedIn Post Ideas page in Notion
4. Click `...` → Connections → connect your integration
5. Copy the 32-char page ID from the URL → paste as `NOTION_PAGE_ID` in `.env`

---

## File Structure

```
linkedin_post_generator/
├── config/
│   ├── topics.yaml           # Companies and topics to track
│   ├── sources.yaml          # RSS feeds and news APIs
│   ├── brand_kit.yaml        # Your voice, tone, writing style
│   ├── my_experiments.yaml   # Your personal AI experiments
│   └── post_ideas.yaml       # Your pre-written angles
├── src/
│   ├── news_gatherer.py      # RSS fetching and relevance scoring
│   ├── trending_tracker.py   # Trending keyword detection
│   ├── post_generator.py     # Claude prompt + post generation
│   ├── pipeline.py           # Full pipeline orchestration
│   └── notion_publisher.py   # Notion integration
├── posts/                    # Generated draft posts (markdown)
├── main.py                   # CLI (click + rich)
├── run_pipeline.py           # Minimal runner (no external deps)
├── requirements.txt
└── .env                      # Your API keys (gitignored)
```
