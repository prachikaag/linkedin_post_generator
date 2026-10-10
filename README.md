# LinkedIn Post Generator

An AI-powered pipeline that fetches trending AI news, tracks what's buzzing, and writes research-backed LinkedIn draft posts — built as a multi-agent Claude Code system.

**What it does:**
- Watches 20+ RSS feeds and YouTube channels from AI companies and tech publications
- Scores every article by relevance to your topics of interest
- Searches the web to find what's trending in AI right now
- Reads your brand kit and writes branded, opinionated LinkedIn posts with cited sources
- Saves all drafts to `posts/` as markdown files — you review and edit before publishing
- Optionally pushes drafts to a Notion page

---

## How to Run

Open this project in Claude Code and say:

```
Run the LinkedIn Post Generator pipeline.
```

Claude reads `orchestrator.md` and executes the full pipeline:

1. Spawns **news-gatherer** → fetches RSS feeds, scores articles by relevance, returns ranked JSON
2. Spawns **trending-tracker** → searches the web for trending AI topics from the last 7 days
3. For each article cluster, spawns **post-generator** → writes and saves a branded draft
4. Spawns **notion-publisher** → pushes drafts to Notion (only if `NOTION_PAGE_ID` is set)

### Variations

```
# Generate a specific number of posts
Run the LinkedIn Post Generator pipeline. Generate 3 posts.

# Dry run — fetch and rank news only, no post generation
Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts.

# Use more source articles per post
Run the pipeline. Use 8 articles per cluster.
```

---

## Configuration — Edit These Files

Everything you need to customise is in `config/`. Changes take effect on the very next run.

| File | Controls |
|------|---------|
| `config/topics.yaml` | Which companies, keywords, and topic categories to track. Freshness rules. |
| `config/brand_kit.yaml` | Your voice, tone traits, writing rules, post structure, hashtags, and length. **Update `author.name` with your real name.** |
| `config/sources.yaml` | RSS feeds and YouTube channels. Add any feed, set `enabled: false` to mute one. |

### Topics tracked

The pipeline watches news about:

- **AI labs** — OpenAI/ChatGPT, Anthropic/Claude, Google DeepMind/Gemini, Perplexity, ElevenLabs, Midjourney, xAI/Grok, Meta AI/LLaMA, Mistral, Runway, Stability AI, and more
- **AI builders** — Cursor, Groq, Cerebras, Harvey AI, Cognition/Devin, Scale AI, Writer, Glean, Suno, Synthesia
- **Big tech** — Microsoft Copilot, Apple Intelligence, Amazon Bedrock, Nvidia, Salesforce Agentforce, Adobe Firefly
- **Categories** — New launches, startup funding rounds, AI for marketing/brands, research breakthroughs, regulation

### Post types generated

- New AI model or feature launches (including YouTube videos and demos)
- Big tech AI announcements
- AI startup funding rounds and acquisitions
- Human-in-the-loop experiments with AI tools
- AI-for-brands and marketing angles

---

## Output

Posts are saved to `posts/` as markdown files with YAML frontmatter:

```
posts/
  2026-01-15_10-30-00_openai-launches-gpt5.md
  2026-01-15_10-30-00_anthropic-funding-round.md
```

Each file has:
- **YAML frontmatter** — source metadata, companies matched, categories, status
- **Post body** — the full LinkedIn draft, ready to review, edit, and publish

Change `status: draft` → `status: published` to track what's gone live.

---

## Architecture

```
orchestrator.md
├── .claude/agents/news-gatherer.md      → fetches + scores RSS articles
├── .claude/agents/trending-tracker.md   → finds trending keyword phrases
├── .claude/agents/post-generator.md     → writes & saves LinkedIn post drafts
└── .claude/agents/notion-publisher.md   → publishes drafts to Notion (optional)
```

Each agent is a self-contained markdown file with its own role, tools, and input/output contract. No Python or external dependencies required — this is a pure Claude Code multi-agent system.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```bash
# Required for Notion publishing (optional feature)
NOTION_PAGE_ID=your_32char_page_id_here

# Optional: direct Notion REST API fallback
NOTION_API_KEY=secret_xxx

# Optional: NewsAPI for additional sources (get a free key at newsapi.org)
NEWSAPI_KEY=your_key_here
```

---

## Personalising Your Brand

Open `config/brand_kit.yaml` and update:

1. **`author.name`** — Your real name as it appears on LinkedIn
2. **`author.title`** — Your LinkedIn headline
3. **`author.tagline`** — One line describing what you help your audience with
4. **`tone_of_voice.primary_traits`** — How you want to come across as a writer
5. **`brand.focus_areas`** — The lenses you write through (already set for AI/brand/marketing focus)
6. **`brand.hashtags.rotate_from`** — Add or remove hashtags from the rotation

Everything else — post structure, writing rules, citation standards, emoji limits — is already tuned for clear, opinionated, research-backed LinkedIn content.

---

## Adding a News Source

Edit `config/sources.yaml` and add any RSS feed:

```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high
      enabled: true
```

Priority levels: `high` (fetched first), `medium`, `low` (fetched last if time permits).
