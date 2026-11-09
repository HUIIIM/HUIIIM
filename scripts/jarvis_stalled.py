#!/usr/bin/env python3
"""Flags jarvis-task issues that stopped moving (#16).

claude.yml moves a jarvis-task issue through jarvis-task:working and then to
jarvis-task:review or jarvis-task:blocked. An issue is stalled when:

- it has no state label (working, review, blocked or done) and was opened more
  than QUEUED_HOURS ago: nothing picked it up;
- it is still jarvis-task:working more than WORKING_HOURS after its last
  update: the run died without recording an outcome.

Issues whose title contains 待中枢裁 are decision requests for Jarvis, not tasks,
and are skipped. Each stalled issue gets one marker comment (never repeated),
and the script exits 1 while any issue is stalled, so the scheduled run is red.
A GitHub API failure exits 2 with an "api error:" line, so it reads differently
from a stall in the run log.

Environment: GITHUB_TOKEN, GITHUB_REPOSITORY (owner/name).
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

QUEUED_HOURS = 6
WORKING_HOURS = 2
MOVED = {"jarvis-task:working", "jarvis-task:review", "jarvis-task:blocked", "jarvis-task:done"}
MARKER = "<!-- jarvis-stalled -->"


def _ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def stalled_reason(issue: dict[str, Any], now: dt.datetime) -> str | None:
    """Why this issue is stalled, or None when it is moving or not a task."""
    if "pull_request" in issue or "待中枢裁" in issue["title"]:
        return None
    labels = {lbl["name"] for lbl in issue["labels"]}
    if "jarvis-task" not in labels:
        return None
    if "jarvis-task:working" in labels:
        age = now - _ts(issue["updated_at"])
        if age > dt.timedelta(hours=WORKING_HOURS):
            return f"jarvis-task:working with no update for {age.total_seconds() / 3600:.0f}h"
        return None
    if not labels & MOVED:
        age = now - _ts(issue["created_at"])
        if age > dt.timedelta(hours=QUEUED_HOURS):
            return f"queued {age.total_seconds() / 3600:.0f}h with no run picking it up"
    return None


def _api(method: str, path: str, token: str, body: dict[str, Any] | None = None) -> Any:
    req = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer " + token},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _paged(path: str, token: str) -> list[Any]:
    items, page = [], 1
    while True:
        chunk = _api("GET", f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}", token)
        items += chunk
        if len(chunk) < 100:
            return items
        page += 1


def check() -> int:
    token, repo = os.environ["GITHUB_TOKEN"], os.environ["GITHUB_REPOSITORY"]
    now = dt.datetime.now(dt.UTC)
    stalled = 0
    for issue in _paged(f"/repos/{repo}/issues?state=open&labels=jarvis-task", token):
        reason = stalled_reason(issue, now)
        if not reason:
            continue
        stalled += 1
        print(f"#{issue['number']}: {reason}")
        comments = _paged(f"/repos/{repo}/issues/{issue['number']}/comments", token)
        if not any(MARKER in (c.get("body") or "") for c in comments):
            body = (
                f"{MARKER}\n**Stalled jarvis-task:** {reason}. Re-label `jarvis-task` to start a run, "
                "or record the blocker here.\n\n---\n"
                "_Posted by the jarvis-stalled check (.github/workflows/jarvis-stalled.yml)_"
            )
            _api("POST", f"/repos/{repo}/issues/{issue['number']}/comments", token, {"body": body})
    print(f"{stalled} stalled jarvis-task issue(s)")
    return 1 if stalled else 0


def main() -> int:
    try:
        return check()
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        print(f"api error: {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
