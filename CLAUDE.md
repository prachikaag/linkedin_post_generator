# LinkedIn Post Generator

## How to run

Say any of the following to Claude Code:

```
Run the LinkedIn Post Generator pipeline.
```

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

Claude will read `orchestrator.md` and execute the full pipeline automatically.

---

## What to customise

| File | What to edit |
|------|-------------|
| `config/brand_kit.yaml` | Your name, title, tagline, tone of voice, writing rules, and hashtag strategy |
| `config/topics.yaml` | Companies to track, topic categories, and freshness settings |
| `config/sources.yaml` | RSS feeds and API sources |
| `.env` | Notion page ID and optional API keys |

All changes take effect on the next run — no restarts required.

---

## Pipeline components

```
orchestrator.md                          ← master pipeline (edit parameters here)
├── .claude/agents/news-gatherer.md      ← fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   ← finds trending keyword phrases via web search
├── .claude/agents/post-generator.md     ← writes LinkedIn draft posts
└── .claude/agents/notion-publisher.md   ← saves drafts to Notion (optional)
```

Generated posts are saved to `posts/` as markdown files. Change `status: draft` to `status: published` once a post goes live.

---

## Personalising your brand kit

Open `config/brand_kit.yaml` and update:

1. **`author.name`** — your name as it appears on LinkedIn
2. **`author.title`** — your LinkedIn headline
3. **`author.tagline`** — one sentence describing what you help people with
4. **`author.location`** — your city and country
5. **`brand.focus_areas`** — the lenses you write through (AI tools you experiment with, industries you serve)
6. **`brand.hashtags`** — your hashtag strategy

The post-generator agent reads this file on every run and writes every post in your voice.

---

## Notion setup (optional)

If you want drafts pushed to Notion automatically:

1. Go to <https://www.notion.so/my-integrations> → New integration
2. Copy the token → paste as `NOTION_API_KEY` in `.env`
3. Open your LinkedIn Post Ideas page in Notion → "..." → Connections → connect the integration
4. Copy the 32-char page ID from the URL → paste as `NOTION_PAGE_ID` in `.env`
