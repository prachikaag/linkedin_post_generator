#!/usr/bin/env bash
# ============================================================
# run.sh — LinkedIn Post Generator
# Launches the pipeline via Claude Code CLI.
#
# Usage:
#   ./run.sh                        # Generate 2 posts (default)
#   ./run.sh --posts 3              # Generate 3 posts
#   ./run.sh --posts 1 --dry-run    # Fetch news only, no post generation
#   ./run.sh --posts 5 --cluster 8  # 5 posts, 8 articles per cluster
# ============================================================

set -euo pipefail

POSTS=2
CLUSTER=6
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --posts)    POSTS="$2";   shift 2 ;;
    --cluster)  CLUSTER="$2"; shift 2 ;;
    --dry-run)  DRY_RUN=true; shift   ;;
    *)          echo "Unknown option: $1"; exit 1 ;;
  esac
done

PROMPT="Run the LinkedIn Post Generator pipeline. Generate ${POSTS} posts. Use ${CLUSTER} articles per cluster."
if [[ "$DRY_RUN" == "true" ]]; then
  PROMPT="Run the pipeline in dry-run mode — fetch and rank news only, don't generate posts."
fi

echo "╔══════════════════════════════════════════════════════╗"
echo "║  LinkedIn Post Generator                             ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Posts requested : ${POSTS}                                    ║"
echo "║  Articles/cluster: ${CLUSTER}                                    ║"
echo "║  Dry-run         : ${DRY_RUN}                              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

if ! command -v claude &>/dev/null; then
  echo "ERROR: 'claude' CLI not found."
  echo "Install Claude Code: https://claude.ai/code"
  exit 1
fi

exec claude --allowedTools "WebFetch,WebSearch,Read,Write,mcp__Notion__*" \
  --print \
  --system-prompt-file orchestrator.md \
  "$PROMPT"
