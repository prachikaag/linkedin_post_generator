# LinkedIn Post Generator

A Claude Code multi-agent pipeline that fetches trending AI news, identifies what's buzzing, and writes research-backed LinkedIn post drafts in your personal brand voice.

---

## Running the Pipeline

When the user asks to run the pipeline (e.g. "Run the LinkedIn Post Generator", "Generate LinkedIn posts", "Run the pipeline"), invoke the **orchestrator** agent.

Default parameters unless the user specifies otherwise:
- `MAX_POSTS` = 2
- `SOURCE_POOL_SIZE` = 6 (articles per post cluster)
- `DRY_RUN` = false

Common variations the user may ask for:
- "Generate 3 posts" → set MAX_POSTS = 3
- "Dry run" or "just fetch news" → set DRY_RUN = true
- "Use 8 articles per post" → set SOURCE_POOL_SIZE = 8

---

## How the Pipeline Works

The orchestrator coordinates four subagents in sequence:

```
orchestrator
├── news-gatherer      → reads RSS feeds → returns scored articles JSON
├── trending-tracker   → searches web → returns trending keyword phrases JSON
├── post-generator     → writes post draft → saves to posts/ → returns metadata JSON
└── notion-publisher   → pushes draft to Notion (only if NOTION_PAGE_ID is set in .env)
```

Posts are saved as markdown files in `posts/` with YAML frontmatter.

---

## Editable Components

Every component is a separate file. Edit any of these to change behaviour:

| File | What it controls |
|------|-----------------|
| `config/brand_kit.yaml` | Your name, tone of voice, writing style, post structure, hashtags |
| `config/topics.yaml` | Companies and keywords to monitor, freshness settings |
| `config/sources.yaml` | RSS feeds and optional API sources |
| `.claude/agents/news-gatherer.md` | How articles are fetched, scored, and filtered |
| `.claude/agents/trending-tracker.md` | How trending keyword phrases are discovered |
| `.claude/agents/post-generator.md` | How LinkedIn posts are written and saved |
| `.claude/agents/notion-publisher.md` | How drafts are published to Notion |
| `orchestrator.md` | The master pipeline that sequences all subagents |

---

## First-Time Setup

1. **Fill in your details** in `config/brand_kit.yaml`:
   - `author.name` — your full name
   - `author.title` — your LinkedIn headline / job title
   - `author.tagline` — one-line description of what you do

2. **Optional — enable Notion**:
   - Copy `.env.example` to `.env`
   - Set `NOTION_PAGE_ID` to your Notion page ID
   - See `.env.example` for step-by-step Notion setup instructions

3. **Optional — enable NewsAPI** for broader coverage:
   - Add `NEWSAPI_KEY` to `.env`
   - Set `enabled: true` under `optional_apis.newsapi` in `config/sources.yaml`

---

## Output

Generated posts are saved to `posts/` as:
```
posts/YYYY-MM-DD_HH-MM-SS_slug-from-article-title.md
```

Each file has YAML frontmatter (sources, companies, categories, status) followed by the full post body. Change `status: draft` to `status: published` to track what's gone live.
