"""
Notion Publisher
----------------
Pushes generated LinkedIn post drafts to a Notion page as daily entries.

Authentication: requires NOTION_API_KEY (a Notion internal integration token)
and NOTION_PAGE_ID set in .env. Both are optional — if absent, this module
silently skips publishing and the rest of the pipeline runs normally.

How to get a Notion integration token:
  1. Go to https://www.notion.so/my-integrations
  2. Click "New integration", give it a name, set it to Internal
  3. Copy the "Internal Integration Token" → NOTION_API_KEY in .env
  4. Open your LinkedIn Post Ideas Notion page
  5. Click the "..." menu → "Connections" → connect your integration
  6. Copy the page ID from the URL (the 32-char hex string) → NOTION_PAGE_ID in .env
"""

import os
from datetime import datetime
from typing import Optional

import requests

_NOTION_API = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"


class NotionPublisher:
    def __init__(self):
        self.api_key: Optional[str] = os.getenv("NOTION_API_KEY")
        self.page_id: Optional[str] = os.getenv(
            "NOTION_PAGE_ID",
            "34a50188f130816280e1f9ec2ef84a0c",  # default: the page created during setup
        )

    def is_configured(self) -> bool:
        return bool(self.api_key and self.page_id)

    def publish(self, post: dict) -> bool:
        """
        Append one post draft to the Notion page as a collapsible toggle block.
        Returns True on success, False on failure.
        """
        if not self.is_configured():
            return False

        blocks = self._build_blocks(post)
        try:
            resp = requests.patch(
                f"{_NOTION_API}/blocks/{self.page_id.replace('-', '')}/children",
                headers=self._headers(),
                json={"children": blocks},
                timeout=15,
            )
            resp.raise_for_status()
            return True
        except Exception as exc:
            print(f"  [Notion] Publish failed: {exc}")
            return False

    def publish_batch(self, posts: list[dict]) -> int:
        """Publish multiple posts. Returns count of successful publishes."""
        return sum(1 for p in posts if self.publish(p))

    # ── Private ────────────────────────────────────────────────────────────────

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": _NOTION_VERSION,
            "Content-Type": "application/json",
        }

    def _build_blocks(self, post: dict) -> list[dict]:
        today = datetime.now().strftime("%B %d, %Y")
        title = post.get("article_title", "LinkedIn Post Draft")[:80]
        content = post.get("content", "")
        source_count = post.get("source_count", 0)
        broken = post.get("broken_urls", 0)

        status_text = f"Draft · {source_count} source(s) cited"
        if broken:
            status_text += f" · ⚠️ {broken} broken link(s) — fix before publishing"

        # Split content into paragraph-sized chunks (Notion has a 2000 char block limit)
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

        children: list[dict] = [
            # Status callout at the top of the toggle
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [_rt(status_text)],
                    "icon": {"emoji": "✏️"},
                    "color": "yellow_background",
                },
            },
        ]

        # Add each paragraph as its own block (max 2000 chars each)
        for para in paragraphs[:40]:
            children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [_rt(para[:2000])],
                    },
                }
            )

        children.append({"object": "block", "type": "divider", "divider": {}})

        return [
            {
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [
                        _rt(f"{today} — ", bold=True),
                        _rt(title, bold=False),
                    ],
                    "children": children,
                },
            }
        ]


def _rt(text: str, bold: bool = False) -> dict:
    """Build a Notion rich_text object."""
    return {
        "type": "text",
        "text": {"content": text},
        "annotations": {"bold": bold},
    }
