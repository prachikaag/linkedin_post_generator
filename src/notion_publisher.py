import os
from datetime import datetime
from typing import Optional


class NotionPublisher:
    """Appends LinkedIn post drafts to a Notion page as collapsible toggle blocks."""

    API_BASE = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"

    def __init__(
        self,
        api_key: Optional[str] = None,
        page_id: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("NOTION_API_KEY", "")
        self.page_id = page_id or os.getenv("NOTION_PAGE_ID", "")
        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.API_VERSION,
        }

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.page_id)

    def publish(self, article_title: str, content: str, source_count: int) -> bool:
        if not self.is_configured:
            return False

        today = datetime.now().strftime("%B %d, %Y")
        toggle_title = f"{today} — {article_title}"
        status_text = f"Draft · {source_count} source(s) cited"

        # Convert post lines to Notion paragraph blocks (max 40 lines, 2000 chars each)
        lines = [line for line in content.split("\n") if line.strip()][:40]
        paragraph_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line[:2000]}}]
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
                            "rich_text": [
                                {"type": "text", "text": {"content": status_text}}
                            ],
                            "icon": {"emoji": "✏️"},
                            "color": "yellow_background",
                        },
                    },
                    *paragraph_blocks,
                    {"object": "block", "type": "divider", "divider": {}},
                ],
            },
        }

        import requests
        resp = requests.patch(
            f"{self.API_BASE}/blocks/{self.page_id}/children",
            headers=self._headers,
            json={"children": [toggle_block]},
            timeout=15,
        )

        if resp.status_code not in (200, 201):
            print(f"  [error] Notion API {resp.status_code}: {resp.text[:300]}")
            return False

        return True
