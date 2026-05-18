"""
Publishes LinkedIn post drafts to a Notion page as collapsible toggle blocks.

Requires NOTION_API_KEY and NOTION_PAGE_ID in your .env file.
If either is missing, is_configured() returns False and the pipeline skips this step.

Setup:
  1. notion.so/my-integrations → New integration → copy the token → NOTION_API_KEY
  2. Open your LinkedIn Ideas Notion page → "..." → Connections → add your integration
  3. Copy the 32-char ID from the page URL → NOTION_PAGE_ID
"""

import os
from datetime import datetime
from typing import Dict

import requests


class NotionPublisher:
    _BASE = "https://api.notion.com/v1"
    _VERSION = "2022-06-28"

    def __init__(self):
        self.token = os.environ.get("NOTION_API_KEY", "")
        self.page_id = os.environ.get("NOTION_PAGE_ID", "")

    def is_configured(self) -> bool:
        return bool(self.token and self.page_id)

    # ── Block builders ──────────────────────────────────────────────────────

    def _paragraph(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text[:2000]}}]
            },
        }

    def _callout(self, text: str) -> Dict:
        return {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": text}}],
                "icon": {"emoji": "✏️"},
                "color": "yellow_background",
            },
        }

    def _divider(self) -> Dict:
        return {"object": "block", "type": "divider", "divider": {}}

    # ── Publish ─────────────────────────────────────────────────────────────

    def publish(self, post: Dict) -> bool:
        """Append the post as a toggle block on the configured Notion page."""
        today = datetime.now().strftime("%B %d, %Y")
        toggle_title = f"{today} — {post['article_title'][:80]}"
        status_text = f"Draft · {post['source_count']} source(s) cited"

        lines = [line for line in post["content"].split("\n") if line.strip()]
        paragraph_blocks = [self._paragraph(line) for line in lines[:40]]

        toggle_block = {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": toggle_title}}],
                "children": [
                    self._callout(status_text),
                    *paragraph_blocks,
                    self._divider(),
                ],
            },
        }

        resp = requests.patch(
            f"{self._BASE}/blocks/{self.page_id}/children",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self._VERSION,
                "Content-Type": "application/json",
            },
            json={"children": [toggle_block]},
            timeout=30,
        )
        return resp.status_code in (200, 201)
