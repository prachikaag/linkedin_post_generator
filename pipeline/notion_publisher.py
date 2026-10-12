"""
Publish LinkedIn post drafts to a Notion page.

Appends each post as a collapsible toggle block so drafts can be reviewed
and edited in Notion before publishing to LinkedIn.

Uses only stdlib (urllib + json). No third-party packages required.

Setup:
  1. Go to https://www.notion.so/my-integrations → New Integration (Internal)
  2. Copy the Integration Token → NOTION_API_KEY in .env
  3. Open your LinkedIn Post Ideas Notion page
  4. "..." menu → Connections → connect your integration
  5. Copy the 32-char page ID from the URL → NOTION_PAGE_ID in .env
"""

import json
import logging
import urllib.request
import urllib.error
from datetime import datetime

logger = logging.getLogger(__name__)

_API = "https://api.notion.com/v1"
_VERSION = "2022-06-28"
_MAX_LINES = 40
_MAX_TEXT = 2000


def publish_to_notion(
    article_title: str,
    content: str,
    source_count: int,
    page_id: str,
    api_key: str,
) -> bool:
    """Append a post draft as a toggle block on a Notion page. Returns True on success."""

    today = datetime.now().strftime("%B %d, %Y")
    toggle_title = f"{today} — {article_title}"
    status_text = f"Draft · {source_count} source(s) cited"

    lines = [ln for ln in content.split("\n") if ln.strip()][:_MAX_LINES]

    children: list[dict] = [
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": status_text[:_MAX_TEXT]}}],
                "icon": {"emoji": "✏️"},
                "color": "yellow_background",
            },
        }
    ]

    for line in lines:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": line[:_MAX_TEXT]}}]
            },
        })

    children.append({"object": "block", "type": "divider", "divider": {}})

    payload = {
        "children": [{
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": toggle_title[:_MAX_TEXT]}}],
                "children": children,
            },
        }]
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{_API}/blocks/{page_id}/children",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Notion-Version": _VERSION,
                "content-type": "application/json",
            },
            method="PATCH",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        logger.error("Notion API %s: %s", exc.code, body)
        return False
    except Exception as exc:
        logger.error("Notion publish failed: %s", exc)
        return False
