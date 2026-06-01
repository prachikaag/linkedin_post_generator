# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — entirely through Claude agents and subagents. No traditional code steps.

**Goal:** Stay visibly current on AI, write as someone who experiments with these tools, and show brands how AI is changing their world — with cited sources and a clear point of view.

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude will read `orchestrator.md` and execute the full pipeline automatically.

**Custom parameters:**
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```
```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

---

## Architecture

```
orchestrator.md                          ← master pipeline (reads + orchestrates)
├── memory/seen_articles.json            ← tracks processed articles (auto-updated)
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases via web search
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file you can read and edit directly. The orchestrator passes data between them — no Python or shell scripts required.

---

## Configuration Files (Edit These)

All settings live in `config/`. Everything is plain text — edit any file and the change takes effect on the next run.

| File | What it controls | Edit frequency |
|------|-----------------|----------------|
| `config/topics.yaml` | Companies, keywords, and freshness settings | Occasionally |
| `config/sources.yaml` | RSS feeds and news sources to pull from | Occasionally |
| `config/brand_kit.yaml` | Author info, tone rules, hashtags, post length | Set once, tweak as needed |
| `config/tone_of_voice.md` | Plain-English writing guide — how every post sounds | Whenever your voice evolves |
| `config/personal_context.md` | **Your AI experiments, opinions, and positioning** | Add to this regularly |

---

## The Most Important File: `personal_context.md`

This is what makes posts sound like **you** — not a generic AI newsletter.

Open `config/personal_context.md` and fill in:
- Your professional context and brand positioning
- AI tools you've actually tested and what happened
- Your current opinions on AI + brands
- Topics you're most interested in right now

The post-generator reads this every run and weaves your experiments and opinions into the **MY TAKE** section. The more specific you are, the more authentic the posts.

---

## Topics & Sources

### What gets tracked (edit `config/topics.yaml`)
- **AI companies:** OpenAI, Anthropic, Google DeepMind, Perplexity, ElevenLabs, Midjourney, Runway, xAI, Meta AI, Mistral, and more
- **Big Tech AI:** Microsoft Copilot, Apple Intelligence, Amazon Bedrock, Nvidia, Salesforce Agentforce, Adobe Firefly
- **AI builders:** Cerebras, Groq, Harvey, Cognition/Devin, Cursor, Suno, Synthesia, and more
- **Topic categories:** launches, funding rounds, research breakthroughs, AI for marketing, regulation, productivity tools

### Where news comes from (edit `config/sources.yaml`)
- **AI news:** TechCrunch AI, The Verge, VentureBeat, Wired, MIT Technology Review, Ars Technica
- **Company blogs:** OpenAI, Anthropic, Google AI, DeepMind, Meta AI, Microsoft AI, Hugging Face, Mistral, Perplexity, ElevenLabs
- **Startup/funding:** TechCrunch Startups, Crunchbase News, SiliconAngle
- **YouTube channels:** Google DeepMind, OpenAI, Anthropic, Two Minute Papers (via RSS)

---

## Post Structure (Every Post Follows This)

1. **HOOK** — stops the scroll (bold claim, surprising stat, or question)
2. **CONTEXT** — what's happening across the AI space broadly
3. **EVIDENCE** — data points from multiple sources, cited
4. **MY TAKE** — your synthesis and opinion (draws from `personal_context.md`)
5. **SO WHAT** — what brands and marketers should actually do
6. **CALL TO ACTION** — invites real comments
7. **SOURCES** — numbered list with full URLs
8. **HASHTAGS** — 4–5 relevant tags

---

## Output

Generated posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-06-01_10-30-00_openai-launches-new-model.md
  2026-06-01_10-30-00_ai-startup-raises-200m-series-b.md
```

Each file contains:
- **YAML frontmatter**: source metadata, companies, categories, trending keywords, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Memory & Deduplication

The pipeline automatically tracks which articles it has already processed in `memory/seen_articles.json`. On each run, articles that were used in previous posts are skipped — so you never get duplicate posts about the same story.

To reset and reprocess everything, clear the `seen_urls` array in `memory/seen_articles.json`.

---

## Notion Integration (Optional)

Set `NOTION_PAGE_ID` in your `.env` file to automatically push each draft to Notion as a child page for review.

```bash
cp .env.example .env
# Edit .env and fill in NOTION_PAGE_ID
```

---

## Environment Variables

```bash
# Required for Notion publishing (optional feature)
NOTION_PAGE_ID=your_32char_page_id_here

# Optional: NewsAPI for additional sources beyond RSS
NEWSAPI_KEY=your_key_here
```

---

## Customising Your Brand

Edit `config/brand_kit.yaml` to set:
- Your name, title, and professional tagline
- Tone traits (curious, pragmatic, opinionated, etc.)
- Writing style rules
- Post structure preferences
- Hashtag strategy
- Minimum sources per post

Edit `config/tone_of_voice.md` for a plain-English version of your writing guide.

Edit `config/personal_context.md` to keep your AI experiments log current.

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

Add YouTube channels (they have RSS feeds):
```yaml
youtube_channels:
  - name: "Channel Name"
    url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE"
    priority: medium
    enabled: true
```
