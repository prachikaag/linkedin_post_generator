"""
Find trending AI keyword phrases by calling the Anthropic Messages API.

Uses only stdlib (urllib + json). No third-party packages required.
"""

import json
import logging
import urllib.request
import urllib.error
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

_API_URL = "https://api.anthropic.com/v1/messages"
_API_VERSION = "2023-06-01"

_SYSTEM = (
    "You are a real-time AI industry analyst. "
    "Return ONLY a raw JSON array starting with [ and ending with ]. "
    "No markdown fences, no explanation, no other text."
)

_USER = """
Today is {date}.

List the 15-20 most buzzworthy, currently trending keyword phrases in AI and tech —
things people are actively searching and discussing RIGHT NOW in {date}.

Focus on:
1. Recent model releases and feature launches (ChatGPT, Claude, Gemini, Grok, Llama, Perplexity...)
2. AI startup funding and acquisitions
3. Research breakthroughs and benchmarks
4. Big tech AI moves (Microsoft Copilot, Google AI, Apple Intelligence, Nvidia, Meta AI...)
5. AI tools for marketing, creative work, voice (ElevenLabs), image (Midjourney), video (Runway)

Phrases should be SHORT (2-5 words) and SPECIFIC to real, recent events.
Not generic: prefer "GPT-5 reasoning benchmark" over just "AI tools".

Prioritise topics related to: {seed_terms}

Return exactly the JSON array. 15-20 phrases. Nothing else.
"""


def get_trending_keywords(
    api_key: str,
    seed_terms: list[str],
    model: str = "claude-sonnet-4-6",
) -> list[str]:
    """Return 15-20 trending AI keyword phrases from Claude."""

    today = datetime.now().strftime("%B %Y")
    user_msg = _USER.format(
        date=today,
        seed_terms=", ".join(seed_terms[:12]),
    )

    try:
        result = _call_api(
            api_key=api_key,
            model=model,
            max_tokens=1024,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = result.get("content", [{}])[0].get("text", "").strip()

        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            keywords = json.loads(text[start:end])
            if isinstance(keywords, list) and keywords:
                return [str(k) for k in keywords]
    except Exception as exc:
        logger.error("Trending tracker failed: %s", exc)

    # Fallback — generic recent phrases if API call fails
    logger.warning("Using fallback trending keywords")
    return [
        "AI agent frameworks",
        "multimodal model capabilities",
        "enterprise AI adoption",
        "AI startup funding",
        "generative AI for marketing",
        "open source AI models",
        "AI productivity tools",
        "large language model benchmarks",
    ]


# ── Anthropic API client (stdlib only) ────────────────────────────────────

def _call_api(
    api_key: str,
    model: str,
    max_tokens: int,
    messages: list[dict],
    system: Optional[str] = None,
) -> dict:
    """POST to Anthropic Messages API using only urllib."""
    payload: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        payload["system"] = system

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        _API_URL,
        data=data,
        headers={
            "x-api-key": api_key,
            "anthropic-version": _API_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read())
