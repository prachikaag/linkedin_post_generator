# LinkedIn Post Generator

Watches AI news, matches it to your topics, and drafts LinkedIn posts in your voice — complete with cited sources and your own firsthand observations woven in. You review and publish. The tool does the research and drafting.

## What it does

1. **Fetches news** from 20+ RSS feeds: TechCrunch, VentureBeat, company blogs (OpenAI, Anthropic, Google, Meta, ElevenLabs, Mistral, etc.), YouTube channels, and startup funding trackers
2. **Scores articles** by relevance to the companies and topics you track — each article gets a relevance score based on keyword matches
3. **Pulls trending keywords** to understand what's being searched right now (via Claude WebSearch, with Google Trends as fallback)
4. **Matches your experiments** — if you've logged a relevant personal AI experiment, it gets woven into the post as a firsthand observation
5. **Drafts posts** via Claude, following your brand kit: your voice, structure, hashtag strategy, and citation standards
6. **Saves drafts** as markdown files in `/posts/` for your review before publishing
7. **Publishes to Notion** (optional) so drafts appear in your content workspace

You are always the editor. The tool drafts — you decide what ships.

---

## Components — What Each File Controls

All components are plain text files you can edit in any editor.

### `config/topics.yaml` — What to track
The master list of companies, products, and topic categories you follow. Edit this to:
- Add or remove companies (every major AI lab is pre-loaded)
- Adjust keywords per company (e.g. add "GPT-5" when it launches)
- Add new topic categories (e.g. "AI in Healthcare")
- Change trending keyword seeds and the geographic region for Google Trends

### `config/brand_kit.yaml` — How to write
Everything that defines your LinkedIn voice. Edit this to:
- Set your name, title, and tagline (replace the placeholder values before first run)
- Adjust your tone traits (curious, pragmatic, accessible, opinionated — tweak to match you)
- Modify the post structure (hook → context → evidence → your take → so what → CTA → sources)
- Update your hashtag strategy (always-include list + rotation pool)
- Change target post length: `short` (300–500 chars) / `medium` (500–900) / `long` (900–1300)

### `config/sources.yaml` — Where to fetch news
The RSS feed list. Edit this to:
- Enable or disable any feed (`enabled: false` to pause without deleting)
- Change feed priority (`high` = fetched first, `low` = fallback)
- Add any custom RSS feed
- Enable NewsAPI for broader coverage (requires a free key from newsapi.org)

### `config/experiments.yaml` — Your firsthand AI experiments
A structured log of the AI tools you've tested personally. This is the "human in the loop" component — when the generator finds a news story about a tool you've experimented with, it weaves one of your real observations into the post as a first-person note.

Each experiment has:
- `tool` — what you tested
- `use_case` — what you were trying to do
- `what_I_did` — exactly what you did
- `key_finding` — your honest conclusion
- `surprise` — the thing you didn't expect (most shareable)
- `brand_relevance` — why it matters for brands or marketers
- `keywords` — controls which news stories it gets matched to
- `published: false` — set to `true` once you've used it in a post

The file ships with example experiments. Replace them with your own.

### `.env` — API keys
Copy `.env.example` to `.env` and fill in:
- `ANTHROPIC_API_KEY` — only needed if running outside Claude Code (Claude Code uses OAuth automatically)
- `NOTION_API_KEY` + `NOTION_PAGE_ID` — optional, enables Notion publishing
- `NEWSAPI_KEY` — optional, enables broader news coverage

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your API key (skip if running inside Claude Code)
cp .env.example .env
# Edit .env and paste your ANTHROPIC_API_KEY

# 3. Personalise before first run — these three files matter most:
#    config/brand_kit.yaml  → set your name, title, and tone
#    config/experiments.yaml → add your own AI experiments
#    config/topics.yaml     → adjust companies/keywords if needed
```

---

## Usage

```bash
# Generate up to 3 posts from today's top AI news
python main.py run

# Generate up to 5 posts
python main.py run --max-posts 5

# See what news would be picked up, without generating posts
python main.py run --dry-run

# List all saved draft posts
python main.py list-posts

# Read a specific draft
python main.py show 1

# Show paths to all config files
python main.py config
```

Or use the minimal runner (no click/rich dependency):

```bash
python run_pipeline.py
```

---

## Generated Posts

Posts are saved in `posts/` as markdown files:

```
posts/
  2026-05-04_10-30-00_elevenlabs-raises-series-c.md
  2026-05-04_10-30-12_openai-operator-now-available.md
```

Each file has YAML frontmatter (source URLs, matched companies, trending keywords, relevance score) followed by the post text. Edit directly, then copy to LinkedIn when ready. Change `status: draft` to `status: published` to track what's gone live.

---

## Adding Your Own Experiments

Open `config/experiments.yaml` and add a block following the template at the top of the file:

```yaml
- id: "my-experiment-slug"
  date: "2026-05"
  tool: "Tool Name (Company)"
  use_case: "What you were trying to do"
  what_I_did: "The actual steps you took"
  key_finding: "Your honest conclusion"
  surprise: "The thing you didn't expect"
  brand_relevance: "Why this matters for brands or marketers"
  keywords:
    - "tool name"
    - "relevant keyword"
  published: false
```

The generator matches experiments to articles by keyword overlap. If a news story about Midjourney comes in and you have a Midjourney experiment logged, one firsthand observation gets woven naturally into the post.

---

## Adding News Sources

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

---

## Optional: Notion Integration

Set `NOTION_API_KEY` and `NOTION_PAGE_ID` in `.env`. Each generated post gets added to your Notion page as a toggle block containing the draft and a status callout. Works via the Notion MCP connector inside Claude Code, or directly via the Notion REST API.

---

## Optional: NewsAPI

Broader news coverage beyond RSS. Get a free key at [newsapi.org](https://newsapi.org/), add it to `.env` as `NEWSAPI_KEY`, and set `enabled: true` under `optional_apis.newsapi` in `config/sources.yaml`.
