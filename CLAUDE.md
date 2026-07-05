# LinkedIn Post Generator

## What This Is

A multi-agent pipeline that fetches trending AI news, finds what's buzzing,
and writes research-backed LinkedIn posts — entirely through Claude agents.
No code to run. Just talk to Claude Code.

---

## How to Run

### Generate posts (standard run)

```
Run the LinkedIn Post Generator pipeline.
```

Claude will:
1. Fetch RSS feeds from all enabled sources in `config/sources.yaml`
2. Score and rank articles by relevance to your topics in `config/topics.yaml`
3. Search the web for what's trending in AI this week
4. Generate 2 LinkedIn post drafts, saved to `posts/`
5. Push drafts to Notion (if `NOTION_PAGE_ID` is set in `.env`)

### Generate more posts

```
Run the LinkedIn Post Generator pipeline. Generate 3 posts.
```

### Preview news without generating posts

```
Run the pipeline in dry-run mode — fetch and rank news only.
```

### Regenerate a post on a specific topic

```
Run the post-generator agent only. Write a post about [topic].
Use these articles: [paste URLs or article titles]
```

---

## Config Files — Edit These to Personalise

| File | What It Controls | How Often to Edit |
|------|-----------------|-------------------|
| `config/brand_kit.yaml` | Your name, tone of voice, writing style, hashtags | Once to set up; tweak anytime |
| `config/topics.yaml` | Companies, keywords, trending seed terms | Add/remove as AI landscape evolves |
| `config/sources.yaml` | RSS feeds and news sources | Add new sources anytime |
| `config/experiments_log.yaml` | Your personal AI experiments (the "human in the loop" angle) | After every experiment you run |

---

## First-Time Setup

1. **Fill in your author details:**
   Open `config/brand_kit.yaml` and update the `author` section:
   - `name`: Your name
   - `title`: Your professional title
   - `tagline`: Your LinkedIn headline
   - `location`: Your city/country

2. **Set up Notion (optional but recommended):**
   - Copy `.env.example` to `.env`
   - Add your `NOTION_PAGE_ID` (32-char hex ID from your Notion page URL)
   - Add your `NOTION_API_KEY` (from notion.so/my-integrations)

3. **Test with a dry run:**
   ```
   Run the LinkedIn Post Generator pipeline in dry-run mode.
   ```

---

## The "Human in the Loop" Angle

Your posts don't just report AI news — they show you *experiencing* it.

**Log your AI experiments in `config/experiments_log.yaml`:**

```yaml
- tool: "Perplexity Deep Research"
  company: "Perplexity"
  date_tested: "2026-07-05"
  use_case: "Researching competitor brand strategy"
  what_worked: "Synthesised 40 sources in 3 minutes"
  what_surprised_me: "It cited sources I hadn't thought to look for"
  what_didnt_work: "Some citations needed manual verification"
  honest_verdict: "Yes — cuts research time by 80% for first-pass work"
  hook_ideas:
    - "I gave Perplexity a brief that would take me 2 hours. It took 3 minutes."
  status: "unused"
```

The post-generator reads this file and weaves your real experiments into posts
as first-person evidence — turning news analysis into authentic insight.

---

## Output

Generated posts are saved to `posts/` as markdown files:

```
posts/
  2026-07-05_10-30-00_openai-launches-new-reasoning-model.md
  2026-07-05_10-30-00_ai-startup-funding-round-series-b.md
```

Each file contains:
- **YAML frontmatter**: sources, companies, categories, status
- **Post body**: the full LinkedIn draft, ready to review and publish

Change `status: draft` → `status: published` to track what's gone live.

---

## Pipeline Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file. To change how any step works,
edit the relevant agent file directly.

---

## Adding News Sources

Edit `config/sources.yaml`:

```yaml
rss_feeds:
  ai_news:
    - name: "My Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

YouTube channels work too — use the YouTube RSS feed URL format:
`https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE`

---

## Troubleshooting

**No articles found:**
Increase `max_article_age_hours` or lower `min_relevance_score` in `config/topics.yaml`.

**Notion publish failed:**
Check that `NOTION_PAGE_ID` is set in `.env` and your integration has access to the page
(Notion page → ... → Connections → add your integration).

**Post is too long:**
The post-generator enforces a 1,457 character / 251 word hard limit.
If you want shorter posts, change `post_length: "short"` in `config/brand_kit.yaml`.
