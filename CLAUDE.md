# LinkedIn Post Generator

## What This Is

An AI-powered pipeline that:
1. Fetches fresh AI news from RSS feeds and company blogs
2. Searches the web for trending keyword phrases
3. Scores and ranks articles by relevance to your tracked topics
4. Writes research-backed LinkedIn post drafts in your brand voice — with cited sources

---

## Running the Pipeline

When the user asks to **generate posts**, **find AI news**, or **run the pipeline**, read `orchestrator.md` and execute it step by step.

Common user triggers:
- "Generate LinkedIn posts"
- "Run the pipeline"
- "Find what's trending in AI and write posts"
- "What's new in AI this week? Write a post about it"
- "Dry run — show me what articles you found"

### Parameters users can specify
| Parameter | Default | Example |
|-----------|---------|---------|
| Number of posts | 2 | "Generate 3 posts" |
| Articles per cluster | 6 | "Use 8 articles per post" |
| Dry run | false | "Dry run — fetch news only" |

---

## Personalise Before First Run

**The most important file to edit is `config/brand_kit.yaml`.**

Open it and fill in:
- `author.name` — your real name
- `author.title` — your professional title
- `author.tagline` — your LinkedIn headline / one-liner
- `tone_of_voice` — adjust the writing traits to match your voice
- `brand.hashtags` — swap in your preferred hashtags

Everything else works out of the box.

---

## Editable Components

### Daily-use config (edit these to control what gets generated)

| File | What it controls |
|------|-----------------|
| `config/brand_kit.yaml` | Your name, tone of voice, writing style, post structure, hashtags |
| `config/topics.yaml` | Companies and keywords to track; trending seed terms; freshness settings |
| `config/sources.yaml` | RSS feeds and APIs to pull news from |

### Pipeline agents (advanced — only touch these to change pipeline behaviour)

| File | Role |
|------|------|
| `orchestrator.md` | Master pipeline instructions — read and follow this to run the full flow |
| `.claude/agents/news-gatherer.md` | Fetches RSS feeds, scores articles by topic relevance, deduplicates |
| `.claude/agents/trending-tracker.md` | Searches the web for trending AI keyword phrases |
| `.claude/agents/post-generator.md` | Writes and saves a LinkedIn post draft from an article cluster |
| `.claude/agents/notion-publisher.md` | Pushes post drafts to Notion as toggle blocks (optional) |

---

## Output

Generated posts are saved to `posts/` as `.md` files with YAML frontmatter.

Each file contains:
- Metadata: sources, companies, categories, trending keywords, relevance score, status
- Full LinkedIn post body: hook → context → evidence → your take → so what → CTA → sources → hashtags

Workflow:
1. Generate → review the draft in `posts/`
2. Edit the post body directly in the `.md` file if needed
3. Publish to LinkedIn
4. Change `status: draft` to `status: published` to track what's gone live

---

## Optional: Notion Integration

Set `NOTION_PAGE_ID` in `.env` to push every draft to a Notion page automatically.
Setup guide is in `.env.example`.

---

## Topics This Pipeline Covers

By default `config/topics.yaml` tracks:
- **AI labs**: OpenAI, Anthropic, Google DeepMind, Perplexity, ElevenLabs, Midjourney, xAI, Meta AI, Mistral, Runway, and more
- **AI builders**: Cursor, Groq, Cerebras, Scale AI, Harvey AI, Cognition, Suno, Synthesia, and more
- **Big tech**: Microsoft Copilot, Apple Intelligence, Amazon Bedrock, Nvidia, Salesforce, Adobe
- **Event types**: new feature launches, funding rounds, research breakthroughs, AI regulation, AI tools and productivity

To add a company or keyword, edit the relevant section in `config/topics.yaml`.
To add a news source, add an entry to `config/sources.yaml`.
