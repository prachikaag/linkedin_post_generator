# Setup Guide — Personalise Your LinkedIn Post Generator

> Complete this once. Then run `orchestrator.md` any time to generate posts.

---

## Step 1 — Fill in your brand kit (5 minutes)

Open `config/brand_kit.yaml` and update the `author` block at the top:

```yaml
author:
  name: "Your Full Name"
  title: "Your LinkedIn Headline"
  tagline: "Helping brands understand and leverage AI in the real world"
  location: "Your City, Country"
```

Everything else in `brand_kit.yaml` (tone, structure rules, hashtags) is already tuned for an
AI-focused marketing & brand perspective — you can use it as-is or tweak any of the rules.

---

## Step 2 — Review your topics (optional, 2 minutes)

Open `config/topics.yaml`. The following are already tracked out of the box:

**AI Labs:** OpenAI / ChatGPT, Anthropic / Claude, Google / Gemini, Perplexity, ElevenLabs, Midjourney, Meta AI, Mistral, Runway, xAI / Grok, Stability AI, HuggingFace

**Big Tech:** Microsoft Copilot, Apple Intelligence, Amazon Bedrock, Nvidia, Salesforce Agentforce, Adobe Firefly

**AI Builders & Startups:** Cursor, Glean, Harvey AI, Cognition / Devin, Suno, Synthesia, Scale AI, Writer, Together AI, Groq, Cerebras

**Topic Categories:** New Feature Launches, Startup Funding, AI for Marketing, Research Breakthroughs, AI Regulation, AI Tools & Productivity

To add a new company or keyword, just append to the relevant list.

---

## Step 3 — Review your news sources (optional)

Open `config/sources.yaml`. These RSS feeds are enabled by default:

- TechCrunch AI, The Verge AI, VentureBeat AI, Wired AI, MIT Tech Review
- OpenAI Blog, Anthropic Blog, Google AI Blog, DeepMind Blog, Meta AI Blog
- TechCrunch Startups, Crunchbase News, SiliconAngle
- YouTube channels: Google DeepMind, OpenAI, Anthropic, Two Minute Papers

To add a source, paste any RSS feed URL into the appropriate section.

---

## Step 4 — (Optional) Connect Notion

If you want drafts automatically saved to a Notion page:

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations) → New integration
2. Copy the token → paste as `NOTION_API_KEY` in `.env`
3. Open your LinkedIn draft page in Notion → "..." → Connections → connect your integration
4. Copy the page ID from the URL → paste as `NOTION_PAGE_ID` in `.env`

---

## Step 5 — Run the pipeline

Open this project in **Claude Code** and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude will spawn subagents to:
1. Fetch fresh AI news from all RSS feeds
2. Find trending keyword phrases from the last 7 days
3. Generate 2 LinkedIn post drafts (edit `orchestrator.md` to change this)
4. Save drafts to `posts/` as markdown files
5. Optionally push to your Notion page

### Custom run options

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

```
Run the pipeline and focus only on AI startup funding news.
```

---

## How posts are stored

Each generated post is saved in `posts/` as a markdown file:

```
posts/
  2026-09-21_10-30-00_openai-launches-o3-model.md
  2026-09-21_10-30-00_anthropic-raises-series-d.md
```

Each file has YAML frontmatter (sources, companies, status) and the full post body.

Change `status: draft` → `status: published` to track what's gone live.

---

## What each config file controls

| File | What it does | How often to edit |
|------|-------------|-------------------|
| `config/brand_kit.yaml` | Your voice, tone, post structure, hashtag rules | Once (then as your brand evolves) |
| `config/topics.yaml` | Companies and keywords to track | When a new AI company launches |
| `config/sources.yaml` | RSS feeds and news sources | When you find a new source you trust |

---

## Troubleshooting

**"No relevant articles found"** — Try increasing `max_article_age_hours` or lowering `min_relevance_score` in `config/topics.yaml`.

**Posts feel off-brand** — Tune `tone_of_voice.writing_style` and `tone_of_voice.dos` in `config/brand_kit.yaml`.

**Wrong companies mentioned** — Check `config/topics.yaml` → add or remove keywords from the relevant company.
