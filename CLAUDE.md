# LinkedIn Post Generator — How to Run

## Quick Start

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

That's it. The orchestrator will:
1. Fetch fresh AI news from RSS feeds
2. Find what's trending in AI right now
3. Generate 2 branded LinkedIn post drafts (saved to `posts/`)
4. Optionally publish them to Notion

## Custom Runs

**Generate more posts:**
```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

**Dry run (fetch + rank news only, no posts):**
```
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.
```

**Use more source articles per post:**
```
Run the LinkedIn Post Generator pipeline. Use 8 articles per cluster.
```

## What Gets Generated

Each post is saved to `posts/` as a markdown file, e.g.:
```
posts/2026-09-15_10-30-00_openai-launches-gpt5.md
```

The file contains:
- YAML frontmatter: sources, companies, categories, trending keywords, status
- Full LinkedIn post body, ready to copy-paste and publish

Change `status: draft` to `status: published` to track what's gone live.

---

## Customise Your Brand Voice

Edit **`config/brand_kit.yaml`** to change:
- Your name, title, tagline
- Tone traits (curious, pragmatic, opinionated, etc.)
- Writing style rules
- Post structure preferences
- Hashtag strategy
- Post length limits

Changes take effect on the next run — no restarts needed.

---

## Customise Your Topics

Edit **`config/topics.yaml`** to:
- Add/remove companies and AI tools to track
- Add/remove topic categories (funding, launches, research, etc.)
- Adjust freshness settings (how old articles can be)
- Change minimum relevance score

---

## Add or Remove News Sources

Edit **`config/sources.yaml`** to:
- Enable/disable any RSS feed (`enabled: true/false`)
- Add new feeds under the relevant category
- Enable NewsAPI by setting `enabled: true` and adding `NEWSAPI_KEY` to `.env`

---

## Article Memory

The file **`data/seen_articles.json`** tracks which article URLs have already been used to generate posts. On every run, the news-gatherer filters these out so you never get duplicate posts.

To reset memory and allow all articles to be considered fresh:
```
Edit data/seen_articles.json and set "seen_article_urls" to []
```

---

## Notion Integration

To publish drafts directly to Notion:
1. Create a Notion integration at https://www.notion.so/my-integrations
2. Copy the integration token
3. Connect the integration to your LinkedIn Post Ideas page
4. Copy the 32-char page ID from the URL
5. Add to `.env`:
   ```
   NOTION_API_KEY=secret_xxx
   NOTION_PAGE_ID=your_32char_id
   ```

---

## Pipeline Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles (reads seen memory)
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases via web search
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a standalone markdown file. Edit any agent to change how that step works.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in what you need:
```bash
cp .env.example .env
```

Only `NOTION_PAGE_ID` and `NOTION_API_KEY` are needed for Notion publishing. The pipeline runs without any API keys when used inside Claude Code.
