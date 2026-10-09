# LinkedIn Post Generator

An AI-powered multi-agent pipeline that fetches trending AI news, identifies what's buzzing, and writes research-backed LinkedIn post drafts in your personal voice — all inside Claude Code, no Python required.

---

## How to Run the Pipeline

To run the full pipeline and generate posts, say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude Code will read `orchestrator.md` and:
1. Spawn **news-gatherer** → fetches and scores RSS feeds
2. Spawn **trending-tracker** → searches for trending AI topics
3. Spawn **post-generator** → writes branded LinkedIn drafts
4. Spawn **notion-publisher** → pushes drafts to Notion (if configured)

### Common run options

```
Run the pipeline. Generate 3 posts.
Run the pipeline in dry-run mode.  (fetch + rank only, no post writing)
Run the pipeline. Use 8 articles per cluster.
```

---

## Config Files (edit these to customise)

| File | What it controls |
|------|-----------------|
| `config/brand_kit.yaml` | Your name, title, tone of voice, writing style, hashtags |
| `config/topics.yaml` | Companies, keywords, and freshness settings |
| `config/sources.yaml` | RSS feeds and news API sources |
| `config/my_experiments.yaml` | Your personal AI experiments (for "I tried X" posts) |

---

## Writing "I Tried X" Posts (Experiment Posts)

When you want to write a post about a personal AI experiment:

```
Write an experiment post about my [experiment name] from my_experiments.yaml.
```

Claude will read `config/my_experiments.yaml`, find the matching experiment, read your brand kit, and write a first-person post in your voice.

Or you can describe the experiment inline:

```
Write an experiment post: I spent a week using Perplexity Pages to create client research
briefs. Here's what I found — it cut my prep time in half but the citations needed
manual checking. The output felt more structured than a ChatGPT doc but less polished
than what I'd write myself.
```

---

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter.
Change `status: draft` to `status: published` to track what's gone live.

---

## Agents Reference

| Agent | File | Role |
|-------|------|------|
| news-gatherer | `.claude/agents/news-gatherer.md` | Fetches + scores RSS articles |
| trending-tracker | `.claude/agents/trending-tracker.md` | Finds trending AI keyword phrases |
| post-generator | `.claude/agents/post-generator.md` | Writes branded news-driven posts |
| experiment-post-generator | `.claude/agents/experiment-post-generator.md` | Writes "I tried X" experiment posts |
| notion-publisher | `.claude/agents/notion-publisher.md` | Publishes drafts to Notion |

---

## Setup

1. Copy `.env.example` to `.env`
2. Edit `config/brand_kit.yaml` — fill in your name, title, and tone preferences
3. Edit `config/my_experiments.yaml` — add your AI experiments as you run them
4. (Optional) Set `NOTION_PAGE_ID` in `.env` for Notion publishing
