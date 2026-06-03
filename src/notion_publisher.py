"""
notion_publisher.py
Appends a LinkedIn post draft to a Notion page as a collapsible toggle block.

Setup:
  1. Go to https://www.notion.so/my-integrations → New integration (Internal)
  2. Copy the token → set NOTION_API_KEY in .env
  3. Open your "LinkedIn Post Ideas" Notion page
  4. "..." menu → Connections → connect your integration
  5. Copy the 32-char page ID from the URL → set NOTION_PAGE_ID in .env

If NOTION_API_KEY or NOTION_PAGE_ID is blank, this step is silently skipped.
"""
from datetime import datetime, timezone


def publish_to_notion(post_result: dict, page_id: str, notion_api_key: str) -> bool:
    """
    Append the post as a toggle block on the Notion page.
    Returns True on success, False on failure or if not configured.
    """
    if not notion_api_key or not page_id:
        return False

    try:
        from notion_client import Client  # lazy import — optional dependency
    except ImportError:
        print("  ⚠  notion-client not installed. Run: pip install notion-client")
        return False

    try:
        client = Client(auth=notion_api_key)
        block = _build_toggle_block(post_result)
        client.blocks.children.append(block_id=page_id, children=[block])
        return True
    except Exception as exc:
        print(f"  ✗ Notion error: {exc}")
        return False


# ── Block builder ─────────────────────────────────────────────────────────────

def _build_toggle_block(post_result: dict) -> dict:
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    article_title = post_result.get("article_title", "Post")[:80]
    toggle_title = f"{today} — {article_title}"
    status_text = f"Draft · {post_result.get('source_count', 0)} source(s) cited"

    lines = [
        line for line in post_result.get("content", "").split("\n") if line.strip()
    ][:40]

    paragraph_blocks = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": line[:2000]}}
                ]
            },
        }
        for line in lines
    ]

    return {
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
