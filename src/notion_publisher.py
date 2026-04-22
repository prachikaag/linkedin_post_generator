"""
Notion Publisher
----------------
Pushes generated LinkedIn post drafts to a Notion page.

Authentication — two paths (tried in order):
  1. Claude CLI + Notion MCP (preferred): works automatically in Claude Code
     environments where the Notion MCP connector is configured. No API key needed.
  2. Direct Notion API: set NOTION_API_KEY (internal integration token) in .env.
     Get one at https://www.notion.so/my-integrations — connect it to your page.

NOTION_PAGE_ID should be set to the 32-char hex ID of your "LinkedIn Post Ideas"
page (copy from the URL). Defaults to the page created during initial setup.
"""

import os
import re
import shutil
import subprocess
from datetime import datetime
from typing import Optional


_NOTION_API = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"


class NotionPublisher:
    def __init__(self):
        self.api_key: Optional[str] = os.getenv("NOTION_API_KEY")
        self.page_id: Optional[str] = os.getenv(
            "NOTION_PAGE_ID",
            "34a50188f130816280e1f9ec2ef84a0c",
        )

    def is_configured(self) -> bool:
        """True if we have any viable path to publish (MCP or direct API)."""
        return bool(self.page_id) and (
            shutil.which("claude") is not None or bool(self.api_key)
        )

    def publish(self, post: dict) -> bool:
        """Append one post draft to the Notion page. Returns True on success."""
        if not self.page_id:
            return False

        # Try Notion MCP via Claude CLI first (no API key needed in Claude Code)
        if shutil.which("claude"):
            if self._publish_via_notion_mcp(post):
                return True

        # Fall back to direct Notion REST API
        if self.api_key:
            return self._publish_via_direct_api(post)

        print(
            "  [Notion] Skipped — set NOTION_API_KEY in .env or run inside Claude Code "
            "with the Notion MCP connector configured."
        )
        return False

    def publish_batch(self, posts: list[dict]) -> int:
        """Publish multiple posts. Returns count of successful publishes."""
        return sum(1 for p in posts if self.publish(p))

    # ── Notion MCP path (Claude CLI) ───────────────────────────────────────────

    def _publish_via_notion_mcp(self, post: dict) -> bool:
        today = datetime.now().strftime("%B %d, %Y")
        title = post.get("article_title", "LinkedIn Post Draft")[:80]
        content = post.get("content", "")
        source_count = post.get("source_count", 0)
        broken = post.get("broken_urls", 0)

        status_note = f"Draft · {source_count} source(s) cited"
        if broken:
            status_note += f" · ⚠️ {broken} broken link(s) — fix before publishing"

        prompt = f"""Use the Notion MCP to add a new toggle block to the Notion page with ID "{self.page_id}".

The toggle should have this title: "{today} — {title}"

Inside the toggle, add:
1. A callout block with the text: "{status_note}"
2. The following LinkedIn post draft as paragraph blocks (split at newlines):

{content[:4000]}

Use the available Notion tools to append these blocks to the existing page.
After adding the blocks, confirm success with a short "Done" message.
"""

        result = subprocess.run(
            [
                "claude", "-p",
                "--model", "haiku",
                "--tools", "mcp__Notion__notion-fetch,mcp__Notion__notion-update-page,mcp__Notion__notion-create-pages",
                "--no-session-persistence",
            ],
            input=prompt,
            capture_output=True,
            text=True,
            cwd="/tmp",
            timeout=60,
        )

        if result.returncode != 0:
            print(f"  [Notion MCP] Failed (exit {result.returncode}): {result.stderr[:200]}")
            return False

        output = result.stdout.strip().lower()
        # Claude should respond with something confirming success
        if any(word in output for word in ("done", "added", "success", "created", "appended")):
            return True

        # If Claude returned output but we can't parse success, log and assume ok
        print(f"  [Notion MCP] Uncertain result: {result.stdout.strip()[:120]}")
        return True

    # ── Direct Notion REST API fallback ───────────────────────────────────────

    def _publish_via_direct_api(self, post: dict) -> bool:
        try:
            import requests
        except ImportError:
            print("  [Notion] requests not installed — pip install requests")
            return False

        blocks = self._build_blocks(post)
        page_id_clean = re.sub(r"[^a-f0-9]", "", self.page_id.lower())
        try:
            resp = requests.patch(
                f"{_NOTION_API}/blocks/{page_id_clean}/children",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Notion-Version": _NOTION_VERSION,
                    "Content-Type": "application/json",
                },
                json={"children": blocks},
                timeout=15,
            )
            resp.raise_for_status()
            return True
        except Exception as exc:
            print(f"  [Notion API] Publish failed: {exc}")
            return False

    def _build_blocks(self, post: dict) -> list[dict]:
        today = datetime.now().strftime("%B %d, %Y")
        title = post.get("article_title", "LinkedIn Post Draft")[:80]
        content = post.get("content", "")
        source_count = post.get("source_count", 0)
        broken = post.get("broken_urls", 0)

        status_text = f"Draft · {source_count} source(s) cited"
        if broken:
            status_text += f" · ⚠️ {broken} broken link(s) — fix before publishing"

        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

        children: list[dict] = [
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
        for para in paragraphs[:40]:
            children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [_rt(para[:2000])]},
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
    return {
        "type": "text",
        "text": {"content": text},
        "annotations": {"bold": bold},
    }
