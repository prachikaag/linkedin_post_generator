# LinkedIn Post Generator

An AI-powered pipeline that monitors AI news, tracks trending topics, and writes research-backed LinkedIn draft posts — in your voice, with cited sources.

---

## How to Run

Say any of these prompts inside Claude Code:

**Full pipeline (default: 2 posts):**
> Run the LinkedIn Post Generator pipeline.

**Generate more posts:**
> Run the LinkedIn Post Generator. Generate 3 posts.

**Preview only (fetch and rank news, no post writing):**
> Run the LinkedIn Post Generator in dry-run mode.

**Custom cluster size:**
> Run the LinkedIn Post Generator. Generate 2 posts, 8 articles per cluster.

Claude will read `orchestrator.md` and run the full pipeline end-to-end.

---

## Architecture

```
orchestrator.md                        ← read this to run the pipeline
├── .claude/agents/news-gatherer.md    → fetches + scores RSS feeds and YouTube channels
├── .claude/agents/trending-tracker.md → searches trending AI topics across the web
├── .claude/agents/post-generator.md   → writes and saves a branded LinkedIn draft
└── .claude/agents/notion-publisher.md → pushes drafts to Notion (optional)
```

Each file is a self-contained agent definition with its own role, tools, and input/output contract. No Python required.

---

## The Five Configuration Files

| File | What it controls | Edit when you want to… |
|------|-----------------|----------------------|
| `config/brand_kit.yaml` | Your name, voice, writing style, hashtags, post structure | Change how posts sound |
| `config/topics.yaml` | Companies + keywords to track, trending seed terms, freshness | Add/remove AI companies to follow |
| `config/sources.yaml` | RSS feeds and YouTube channels — toggle on/off per source | Add a new news source |
| `orchestrator.md` | Pipeline flow, clustering algorithm, dry-run logic | Change how many posts to generate |
| `.env` | Notion page ID, optional API keys | Connect Notion or NewsAPI |

Edit any file directly — changes take effect on the next run.

---

## Setting Up Notion (optional but recommended)

1. Copy `.env.example` → `.env`
2. Open your LinkedIn drafts Notion page
3. Copy the 32-char page ID from the URL (the hex string after the last `/`)
4. Paste it as `NOTION_PAGE_ID` in `.env`

Generated posts will be appended to that page as collapsible toggle blocks — one per run, with status callout and full sources.

If Notion is not configured, posts are saved as markdown files in `posts/`.

---

## Output Format

Posts are saved to `posts/YYYY-MM-DD_HH-MM-SS_slug.md` with:
- **YAML frontmatter**: source URLs, matched companies, categories, status
- **Post body**: the full LinkedIn draft, ready to review and copy-paste

Change `status: draft` → `status: published` to track what's gone live.

---

## Customising Your Topics

Edit `config/topics.yaml`:
- Under `companies_to_track` → add any AI company with its keyword list
- Under `topic_categories` → add new categories (funding, launches, policy, etc.)
- Under `trending_keywords.seed_terms` → seed terms drive what's searched for trending topics
- `freshness.max_article_age_hours` → how far back to look (default: 48h)

## Customising Your Brand Voice

Edit `config/brand_kit.yaml`:
- `author` → your name, title, tagline
- `tone_of_voice.primary_traits` → how you want to come across
- `tone_of_voice.writing_style` → line-by-line rules for every post
- `tone_of_voice.post_structure` → the exact blueprint: hook → context → evidence → your take → so what → CTA → sources → hashtags
- `brand.content_types` → the types of posts you write (feature launches, funding, experiments, etc.)
- `brand.hashtags` → always-include plus rotation pool

## Adding News Sources

Edit `config/sources.yaml` — add any RSS feed or YouTube channel:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

Set `enabled: false` to pause a feed without deleting it.

---

## Post Types This Pipeline Covers

1. **New AI Feature or Product Launch** — e.g. "ChatGPT launches X — here's what brands should know"
2. **Big Tech AI News** — e.g. "What Microsoft's Copilot numbers actually tell us"
3. **AI Startup Funding** — e.g. "What this $500M round signals about where AI is heading"
4. **AI Research Breakthroughs** — e.g. "New benchmark just raised the bar — here's why it matters"
5. **Human-in-the-Loop Experiments** — e.g. "I spent 3 hours with [tool] — here's the honest result"
6. **AI for Marketing and Brands** — e.g. "What [development] means for your creative team today"
