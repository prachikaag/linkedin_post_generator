# LinkedIn Post Generator — Project Guide

This project is a multi-agent AI pipeline that monitors AI news, tracks trending topics, and writes research-backed LinkedIn post drafts in your personal brand voice.

## How to Run

To generate new LinkedIn post drafts, say:

```
Run the LinkedIn Post Generator pipeline.
```

To generate more posts or use more source articles:

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts. Use 8 articles per cluster.
```

To preview what news is available without writing posts:

```
Run the pipeline in dry-run mode.
```

## What Happens Each Run

1. **Memory check** — Scans `posts/` for previously used article URLs so nothing repeats
2. **News gathering** — Fetches live RSS feeds from `config/sources.yaml`, scores articles by relevance against `config/topics.yaml`
3. **Trend tracking** — Web-searches trending AI topics from the past 7 days
4. **Post generation** — Writes 2 (default) LinkedIn posts in your brand voice from `config/brand_kit.yaml`
5. **Notion publishing** — If `NOTION_PAGE_ID` is set in `.env`, posts are appended to your Notion page as collapsible drafts

## Files You'll Edit Regularly

| File | What to change |
|------|---------------|
| `config/brand_kit.yaml` | Your name, title, tone, writing style, hashtags |
| `config/topics.yaml` | Companies to track, keywords, freshness settings |
| `config/sources.yaml` | RSS feeds — add/remove/enable/disable sources |
| `.env` | API keys and Notion page ID |

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/2026-07-10_14-00-00_openai-launches-new-feature.md
```

Each file has:
- **Frontmatter**: sources, companies, categories, relevance score, status
- **Post body**: ready-to-review LinkedIn draft with cited sources

Change `status: draft` → `status: published` to track what's gone live.

## Agents Reference

| Agent | File | Does |
|-------|------|------|
| Orchestrator | `orchestrator.md` | Runs the full pipeline, coordinates all agents |
| News Gatherer | `.claude/agents/news-gatherer.md` | Fetches + scores RSS articles |
| Trending Tracker | `.claude/agents/trending-tracker.md` | Finds trending AI keyword phrases |
| Post Generator | `.claude/agents/post-generator.md` | Writes branded LinkedIn drafts |
| Notion Publisher | `.claude/agents/notion-publisher.md` | Pushes drafts to Notion (optional) |

## Tracked News Categories

- **New product launches** — ChatGPT, Claude, Gemini, Perplexity, ElevenLabs, Midjourney, and 20+ other AI tools
- **BigTech AI moves** — Microsoft Copilot, Apple Intelligence, Amazon Bedrock, Google AI, Nvidia
- **Startup funding** — Series A/B/C, acquisitions, IPOs, valuations
- **AI research** — papers, benchmarks, capability milestones
- **AI for brands** — how marketers and CMOs are using AI in campaigns and strategy
- **YouTube drops** — new videos from OpenAI, Anthropic, Google DeepMind channels

## Personalising Your Brand

Edit `config/brand_kit.yaml`:
- Set your `author.name`, `author.title`, and `author.tagline`
- Adjust `tone_of_voice` traits to match how you actually sound
- Add your own `signature_phrases`
- Tune `brand.hashtags` to your niche
