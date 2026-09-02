# LinkedIn Post Generator — Claude Code Project

## What This Does

Runs a multi-agent pipeline that fetches fresh AI news, tracks trending keywords, and writes research-backed LinkedIn post drafts — personalised to your voice and brand.

Every output is saved to `posts/` as a markdown file you review before posting.

---

## How to Run

### Generate news-based posts (default)
```
Run the LinkedIn Post Generator pipeline.
```

### Generate posts from your personal AI experiments
```
Run the LinkedIn Post Generator pipeline in experiment mode.
```

### Generate both news posts and experiment posts
```
Run the LinkedIn Post Generator pipeline in full mode.
```

### Dry-run (fetch news, don't write posts)
```
Run the LinkedIn Post Generator pipeline in dry-run mode.
```

### Custom options
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 5 articles per cluster.
```

---

## Key Files to Personalise

| File | What to Edit |
|------|-------------|
| `config/brand_kit.yaml` | Your name, title, tone of voice, post style |
| `config/topics.yaml` | AI companies and topics you want to track |
| `config/sources.yaml` | RSS feeds and news sources |
| `config/experiments.yaml` | Your personal AI experiments (for "human in the loop" posts) |

**Start here:** Open `config/brand_kit.yaml` and fill in your name, title, and tagline.
Then open `config/experiments.yaml` to log your AI experiments.

---

## Output

Generated posts land in `posts/` as `.md` files with YAML frontmatter.

```
posts/
  2026-09-01_10-30-00_openai-launches-gpt5.md
  2026-09-01_10-45-00_i-tested-claude-for-brand-briefs.md
```

Each file has:
- **Frontmatter**: sources, companies, categories, status
- **Post body**: full LinkedIn draft ready to copy-paste

Change `status: draft` → `status: published` to track what's gone live.

---

## Pipeline Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md         → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md      → finds trending keyword phrases
├── .claude/agents/post-generator.md        → writes news-based LinkedIn drafts
├── .claude/agents/experiment-post-generator.md  → writes "I tried X" experiment drafts
└── .claude/agents/notion-publisher.md      → publishes drafts to Notion (optional)
```

---

## Notion Integration (optional)

Set `NOTION_PAGE_ID` in `.env` to push drafts directly to your Notion workspace.
See `.env.example` for setup instructions.
