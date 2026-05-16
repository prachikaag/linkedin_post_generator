"""Publishes LinkedIn post drafts to Notion as collapsible toggle blocks."""
import os
from datetime import datetime, timezone


class NotionPublisher:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API_KEY", "")
        self.page_id = os.getenv("NOTION_PAGE_ID", "")
        self._client = None

    def _get_client(self):
        if self._client is None:
            from notion_client import Client
            self._client = Client(auth=self.api_key)
        return self._client

    def is_configured(self) -> bool:
        return bool(self.api_key and self.page_id)

    def publish_post(self, post: dict) -> bool:
        if not self.is_configured():
            return False

        today = datetime.now(timezone.utc).strftime("%B %d, %Y")
        article_title = post.get("article_title", "LinkedIn Post")
        source_count = post.get("source_count", 0)
        content = post.get("content", "")

        toggle_title = f"{today} — {article_title}"
        status_text = f"Draft · {source_count} source(s) cited"

        lines = [line for line in content.split("\n") if line.strip()][:40]
        paragraph_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                },
            }
            for line in lines
        ]

        toggle_block = {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": toggle_title}}],
                "children": [
                    {
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "rich_text": [{"type": "text", "text": {"content": status_text}}],
                            "icon": {"type": "emoji", "emoji": "✏️"},
                            "color": "yellow_background",
                        },
                    },
                    *paragraph_blocks,
                    {"object": "block", "type": "divider", "divider": {}},
                ],
            },
        }

        try:
            client = self._get_client()
            response = client.blocks.children.append(
                block_id=self.page_id,
                children=[toggle_block],
            )
            return bool(response.get("results"))
        except Exception as e:
            print(f"Notion publish error: {e}")
            return False

    def publish_batch(self, posts: list[dict]) -> int:
        return sum(1 for post in posts if self.publish_post(post))
