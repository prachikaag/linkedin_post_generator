# LinkedIn Post Generator

AI-powered pipeline that fetches trending AI news and writes research-backed LinkedIn post drafts in your brand voice.

## How to Run

```
Run the LinkedIn Post Generator pipeline.
```

That's it. Claude Code reads `orchestrator.md` and runs the full pipeline automatically.

### Variations

```
Run the pipeline — generate 3 posts.
Run the pipeline in dry-run mode (fetch news only, no posts).
Run the pipeline and publish to Notion.
```

## What Happens Each Run

1. **news-gatherer** — fetches RSS feeds from `config/sources.yaml`, scores articles using keywords from `config/topics.yaml`, returns top 25 most relevant
2. **trending-tracker** — web-searches for the most-discussed AI topics of the past 7 days
3. **post-generator** — synthesises a cluster of articles into a branded LinkedIn post saved to `posts/`
4. **notion-publisher** — pushes each draft to Notion (only if `NOTION_PAGE_ID` is set in `.env`)

## Config Files (edit these)

| File | What to change |
|------|---------------|
| `config/brand_kit.yaml` | Your name, title, tone, writing rules, hashtags |
| `config/topics.yaml` | Companies to track, keywords, freshness settings |
| `config/sources.yaml` | RSS feeds and news sources |

## Setup

1. Copy `.env.example` to `.env`
2. Fill in `NOTION_PAGE_ID` (optional — get from your Notion page URL)
3. Update `config/brand_kit.yaml` with your actual name and title
4. Run the pipeline

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter.
Change `status: draft` → `status: published` after posting on LinkedIn.
