# My AI Experiments Journal

This file is your "human in the loop" content bank.

Every time you try something interesting with an AI tool — a workflow, a prompt, a comparison, a failure, a surprise — log it here. When `post_ready: true`, the experiment-writer agent will turn it into a LinkedIn post in your voice.

**Format for each entry:**

```
## [Date] — [Tool]: [Use case in 10 words or fewer]
tool: ToolName
date: YYYY-MM-DD
use_case: One-line description of what you tried
post_ready: true / false
status: draft / posted
post_file: posts/filename.md  ← filled in by the agent after posting

### What I tried
Describe the experiment. What were you trying to accomplish? What inputs did you give the tool?

### What happened
Honest results. What worked? What didn't? What surprised you?

### My take
Your personal opinion. Would you use this again? What would you change? What does this mean for how brands should think about this tool?
```

---
---

## 2026-06-12 — Claude Code: Writing a complete project from a voice memo

tool: Claude Code (claude.ai/code)
date: 2026-06-12
use_case: Turning a 4-minute voice memo into a working project
post_ready: false
status: draft
post_file:

### What I tried
I recorded a 4-minute voice memo describing what I wanted to build — a LinkedIn post generator that tracks AI news and writes in my brand voice. No outline, just talking. Then I pasted the transcript into Claude Code and said "build this".

### What happened
Claude Code read the transcript, asked two clarifying questions, then built the config files, agent definitions, and orchestrator in about 12 minutes. The output structure was clean and editable. It also wrote a CLAUDE.md explaining how to run it — which I didn't ask for.

The surprising part: it preserved my language from the memo. When I described the "human in the loop" angle, that phrase showed up in the brand kit. It listened more carefully than I expected.

What didn't work: it made assumptions about my job title and left placeholder values I had to fill in manually. Small thing, but worth knowing.

### My take
This is genuinely useful for founders and marketers who have ideas but not time to spec them out properly. The voice-memo-to-working-prototype workflow is underrated. The quality of the output depends entirely on how clearly you can articulate the idea — garbage in, garbage out still applies. But if you can describe the thing, Claude Code can build the scaffold. That's a meaningful shift.

---

## 2026-07-03 — Perplexity: Research for a client brand audit

tool: Perplexity Pro
date: 2026-07-03
use_case: Competitor research for a mid-market fashion brand
post_ready: false
status: draft
post_file:

### What I tried
Used Perplexity Pro (with the "Pro Search" mode) to research the brand positioning of 5 direct competitors for a client brand audit. Same work I'd normally spend 2-3 hours doing manually with tabs and bookmarks.

### What happened
Perplexity surfaced clean summaries with cited sources in about 8 minutes. The sources were recent (within 6 months), which was the key requirement. It also picked up on patterns I'd missed — two competitors had quietly shifted from "luxury" to "accessible luxury" language in the past year.

One issue: it hallucinated one brand's revenue figure ($43M vs the correct $18M). I caught it because I cross-referenced with Crunchbase. Would not have caught it if I'd been in a rush.

### My take
Perplexity is genuinely good for competitive research when you need recent information fast. But it's not a replacement for verification — it's a starting point. The correct workflow is: Perplexity for synthesis and speed, then manual spot-checks on any number that matters. Treat it like a very fast research assistant who's occasionally overconfident. The hallucination risk is real. The time savings are also real.

---

## 2026-07-28 — ElevenLabs: Cloning my voice for client presentations

tool: ElevenLabs Voice Cloning
date: 2026-07-28
use_case: Testing whether AI voice cloning could replace recorded voiceovers for slide decks
post_ready: true
status: draft
post_file:

### What I tried
Uploaded 3 minutes of clean audio from a previous podcast appearance. ElevenLabs generated a voice clone. I then used it to narrate a 7-slide client presentation instead of re-recording myself.

### What happened
The output was about 85% convincing. Pace and tone were accurate. The intonation on questions was slightly flat — it didn't quite nail the rising inflection I use. Client didn't notice on first listen. I noticed immediately.

Total time saved: about 45 minutes of recording and editing.

### My take
This is not about replacing your voice — it's about saving the hours spent re-recording when you change one slide. The use case isn't replacing you; it's handling the revision loop. Brands doing regular video content should be paying attention here. The time savings compound. The quality is already good enough for internal presentations and lower-stakes external content. For hero brand content, you still want the real thing.

---

## 2026-08-05 — Midjourney v7: Brand identity visuals for a startup pitch deck

tool: Midjourney v7
date: 2026-08-05
use_case: Generating moodboard and placeholder visuals for a startup's first pitch deck
post_ready: true
status: draft
post_file:

### What I tried
A startup founder asked me to help with their pitch deck and couldn't afford a photographer or illustrator. Used Midjourney v7 to generate 12 images across 3 visual directions — clean tech minimalism, warm human-focused, and bold geometric brand identity. Used detailed prompts referencing specific photographers and visual styles.

### What happened
Generated 48 images in about 25 minutes. The founder picked a direction on the first pass. No revision rounds needed. Two of the images made it into the final deck without modification. The rest were reference-only.

What didn't work: logos and text in images were still unusable (Midjourney's known limitation). Had to keep all text-on-image elements separate.

### My take
This changes the economics of early-stage brand work. A founder who previously couldn't afford visual direction can now test 3 distinct identities before committing to a designer. The design phase didn't go away — it got faster and cheaper to reach the point where a human designer adds real value. Designers who adapt to this workflow will be more productive. Designers who ignore it will be slower.

---

<!-- 
TO ADD A NEW EXPERIMENT:
Copy the template below, paste it above this comment, and fill it in.

## YYYY-MM-DD — [Tool]: [Use case]
tool: ToolName
date: YYYY-MM-DD
use_case: One-line description
post_ready: false
status: draft
post_file:

### What I tried

### What happened

### My take

-->
