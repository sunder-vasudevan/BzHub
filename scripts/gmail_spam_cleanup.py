#!/usr/bin/env python3
"""Move spam-like Gmail threads to a label using the gog CLI.

Requires:
  - gog CLI (brew install steipete/tap/gogcli)
  - gog auth already configured for your Gmail account

Environment variables:
  GMAIL_SPAM_LABEL   Label to add (default: Spam-Filtered)
  GMAIL_SPAM_QUERY   Gmail search query (default: in:inbox newer_than:7d)
  GMAIL_SPAM_MAX     Max threads to process (default: 200)
  GMAIL_DRY_RUN      true/false (default: true)

Example:
  GOG_ACCOUNT=you@gmail.com \
  GMAIL_SPAM_QUERY='in:inbox newer_than:7d (from:(promo@ OR noreply@) OR subject:(free money winner))' \
  GMAIL_DRY_RUN=false \
  python3 scripts/gmail_spam_cleanup.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import List


def run_gog(args: List[str], capture: bool = True) -> subprocess.CompletedProcess:
    cmd = ["gog", *args]
    return subprocess.run(
        cmd,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def ensure_label(label: str) -> None:
    result = run_gog(["gmail", "labels", "list", "--json"])
    if result.returncode != 0:
        print(result.stderr or "Failed to list labels.", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout or "{}")
    labels = {item.get("name") for item in data.get("labels", [])}
    if label not in labels:
        create = run_gog(["gmail", "labels", "create", label], capture=True)
        if create.returncode != 0:
            print(create.stderr or f"Failed to create label: {label}", file=sys.stderr)
            sys.exit(1)
        print(f"Created label: {label}")


def chunk(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def main() -> None:
    label = os.getenv("GMAIL_SPAM_LABEL", "Spam-Filtered")
    query = os.getenv("GMAIL_SPAM_QUERY", "in:inbox newer_than:7d")
    max_threads = int(os.getenv("GMAIL_SPAM_MAX", "200"))
    dry_run = os.getenv("GMAIL_DRY_RUN", "true").strip().lower() in {"1", "true", "yes"}

    ensure_label(label)

    search = run_gog(["gmail", "search", query, "--max", str(max_threads), "--json"])
    if search.returncode != 0:
        print(search.stderr or "Search failed.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(search.stdout or "{}")
    thread_ids = [t.get("id") for t in data.get("threads", []) if t.get("id")]

    if not thread_ids:
        print("No matching threads found.")
        return

    print(f"Found {len(thread_ids)} threads matching query.")

    if dry_run:
        print("Dry run enabled. No changes made.")
        print("Threads:")
        for tid in thread_ids:
            print(f"  {tid}")
        return

    for tid in thread_ids:
        modify = run_gog(["gmail", "labels", "modify", tid, "--add", label, "--remove", "INBOX"])
        if modify.returncode != 0:
            print(modify.stderr or f"Failed to modify thread {tid}", file=sys.stderr)
            continue
        print(f"Moved thread {tid} to label {label} (removed INBOX).")


if __name__ == "__main__":
    main()
