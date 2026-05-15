# LinkedIn Post Generator

A multi-agent pipeline that tracks AI news, identifies trending topics, and writes branded LinkedIn post drafts — ready to review and publish.

## How to Run

Type `/generate-posts` in Claude Code, or just say:

```
Run the LinkedIn Post Generator pipeline.
```

Optional parameters:
```
/generate-posts — generate 3 posts
/generate-posts — 5 articles per cluster, dry run
Run the pipeline in dry-run mode — fetch and rank news only, skip post generation.
```

---

## Pipeline Flow

```
orchestrator (generate-posts command)
  ├── 1. news-gatherer       → fetches RSS feeds, scores by relevance
  ├── 2. trending-tracker    → web searches for hot AI topics this week
  ├── 3. post-generator      → writes a branded draft per article cluster
  └── 4. notion-publisher    → pushes to Notion (optional, needs NOTION_PAGE_ID)
```

All agents live in `.claude/agents/`. The orchestrator is in `.claude/commands/generate-posts.md`.

---

## Config Files — Edit These

| File | What to edit |
|------|-------------|
| `config/brand_kit.yaml` | **Start here.** Your name, title, tone of voice, writing style, hashtag strategy, post length |
| `config/topics.yaml` | Companies and keywords to track, topic categories, trending seed terms, freshness settings |
| `config/sources.yaml` | RSS feeds and APIs — add/remove/enable/disable any source |
| `.env` | `NOTION_PAGE_ID` to push to Notion, `NEWSAPI_KEY` for extra coverage |

---

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-05-14_22-55-00_enterprise-ai-market-shift.md
  2026-05-14_23-10-00_vertical-ai-depth-over-horizontal.md
```

Each file has:
- `status: draft` — change to `published` once you've posted it to LinkedIn
- All cited source URLs in the frontmatter and inline in the post body

---

## First-Time Setup

1. Edit `config/brand_kit.yaml` — set your `author.name`, `author.title`, `author.tagline`
2. Review `config/topics.yaml` — add or remove companies and keywords you care about
3. Copy `.env.example` → `.env` and fill in `NOTION_PAGE_ID` if you use Notion
4. Run `/generate-posts`

---

## Agent Reference

### `news-gatherer`
Reads `config/sources.yaml` and `config/topics.yaml`. Fetches all enabled RSS feeds via WebFetch, scores each article by keyword relevance, deduplicates, and returns a ranked JSON array.

### `trending-tracker`
Reads `config/topics.yaml` seed terms. Uses WebSearch to find the hottest AI topics from the past 7 days. Returns 15–20 short keyword phrases.

### `post-generator`
Reads `config/brand_kit.yaml`. Takes a cluster of articles + trending keywords, writes a branded LinkedIn post following your voice and structure rules exactly, and saves it as a `.md` draft.

### `notion-publisher`
Takes a post draft and appends it as a collapsible toggle block on your Notion page. Requires `NOTION_PAGE_ID` in `.env`.
