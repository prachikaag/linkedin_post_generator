#!/usr/bin/env python3
"""
LinkedIn Post Generator — pipeline launcher.

Requires Claude Code CLI to be installed and authenticated.

Usage:
  python run_pipeline.py              # generate 2 posts (default)
  python run_pipeline.py 3            # generate 3 posts
  python run_pipeline.py --dry-run    # fetch and rank news only, no post generation
"""

import sys
import subprocess


def build_prompt(n_posts: int, dry_run: bool) -> str:
    if dry_run:
        return (
            "Run the LinkedIn Post Generator pipeline in dry-run mode — "
            "fetch and rank news only, don't generate posts."
        )
    noun = "post" if n_posts == 1 else "posts"
    return f"Run the LinkedIn Post Generator pipeline. Generate {n_posts} {noun}."


def main():
    n_posts = 2
    dry_run = False

    for arg in sys.argv[1:]:
        if arg in ("--dry-run", "-d"):
            dry_run = True
        elif arg.isdigit():
            n_posts = int(arg)
        else:
            print(f"Unknown argument: {arg}")
            print(__doc__)
            sys.exit(1)

    prompt = build_prompt(n_posts, dry_run)

    label = "dry-run" if dry_run else f"{n_posts} post{'s' if n_posts != 1 else ''}"
    print(f"Starting LinkedIn Post Generator ({label})")
    print("-" * 50)

    try:
        subprocess.run(["claude", "-p", prompt], check=True)
    except FileNotFoundError:
        print("Error: 'claude' command not found.")
        print("Install Claude Code CLI: https://claude.ai/code")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Pipeline exited with code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
