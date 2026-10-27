# Config Editing Guide

Three YAML files control everything about how the pipeline works.
Edit any of them — no restart needed.

---

## brand_kit.yaml — Your voice and post structure

**What it controls:** how every post is written — tone, structure, style rules, content angles, hashtags, length.

**Change these first:**
- `author.name` — your name (used as the first-person voice in posts)
- `author.title` — your professional title
- `author.tagline` — one line that describes your positioning
- `author.location` — your city / country

**Tune these to match your real voice:**
- `tone_of_voice.primary_traits` — adjectives and qualities that describe how you come across
- `tone_of_voice.writing_style` — sentence-level rules (paragraph length, punctuation style, etc.)
- `tone_of_voice.dos` / `donts` — things that make your posts great vs. things that undermine them

**Control what type of post gets written:**
- `brand.content_angles` — six named post types (tool launch, big tech move, funding, human-in-the-loop, YouTube, research). Each has a `trigger`, an `angle` (the headline framing), an `example_hook`, and `notes`. Edit these to steer what the AI writes when it detects each scenario.

**Change hashtags:**
- `brand.hashtags.always_include` — always appear in every post
- `brand.hashtags.rotate_from` — pool to pick from to complete the set

**Change post length:**
- `brand.post_length` — `"short"`, `"medium"`, or `"long"`

---

## topics.yaml — What news you track

**What it controls:** which companies and keywords score articles as relevant, which topic categories get flagged.

**Add a new company to track:**
```yaml
companies_to_track:
  ai_labs:
    - name: "New Company Name"
      keywords:
        - "keyword one"
        - "keyword two"
```

**Add a new topic category:**
```yaml
topic_categories:
  - name: "My New Category"
    description: "What this covers"
    keywords:
      - "keyword"
      - "another keyword"
```

**Tune freshness:**
- `freshness.max_article_age_hours` — how old an article can be (default: 48 hours)
- `freshness.min_relevance_score` — minimum score to include (default: 2; lower = more articles)
- `freshness.max_articles_per_run` — how many articles to work with (default: 25)

---

## sources.yaml — Where news comes from

**What it controls:** every RSS feed and API the pipeline reads.

**Disable a feed without deleting it:**
```yaml
- name: "The Information AI"
  url: "..."
  priority: low
  enabled: false   # ← change this
```

**Add a new RSS feed:**
```yaml
rss_feeds:
  ai_news:
    - name: "My Custom Source"
      url: "https://example.com/feed.xml"
      priority: high    # high | medium | low
      enabled: true
```

**Add a YouTube channel** (uses YouTube's RSS feed — no API key needed):
```yaml
youtube_channels:
  - name: "Channel Display Name"
    url: "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID_HERE"
    priority: medium
    enabled: true
```
To find a channel's ID: go to the channel on YouTube → right-click page → View Page Source → search for `"channelId"`.

**Enable NewsAPI** (broader coverage with a free API key):
1. Get a free key at https://newsapi.org/
2. Add `NEWSAPI_KEY=your_key` to your `.env` file
3. Set `optional_apis.newsapi.enabled: true` in this file

---

## posts/ — Your draft posts

Generated posts land here as `.md` files with YAML frontmatter.

**Track publication status** by editing the frontmatter in each file:
```yaml
status: "draft"       # not yet reviewed
status: "reviewed"    # you've read and edited it
status: "published"   # live on LinkedIn
```

The files are yours to edit freely — the pipeline only writes new ones, never overwrites.
