#!/usr/bin/env python3
"""Independent-verdict gate for claude/* pull requests (SOTA VER-3, IVV.md).

A pull request from a ``claude/*`` branch is "done" only when an independent
assessor has posted a verdict comment for its current head commit, in the
IVV.md format::

    ### 独立评估 · SOTA v1.0 · <first 7 characters of the head sha>
    判定：PASS | FAIL（…） | N/A（…）

The script reads the pull request and its comments through the GitHub API and
sets the commit status ``ivv/verdict`` on the head commit:

- success: not a claude/* branch, or a PASS / N/A verdict exists for the head;
- failure: the latest verdict for the head is FAIL;
- pending: no verdict for the head yet (a new push resets it).

Environment: GITHUB_TOKEN, GITHUB_REPOSITORY (owner/name), PR_NUMBER.
The status is the signal; the script exits 0 unless the API call fails.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from typing import Any

CONTEXT = "ivv/verdict"
HEADING = re.compile(r"^###\s*独立评估\s*·\s*SOTA[^·\n]*·\s*([0-9a-f]{7,40})\s*$", re.MULTILINE)
RULING = re.compile(r"判定[:：]\s*(PASS|FAIL|N/A)")


def verdict_state(head_ref: str, head_sha: str, comments: list[str]) -> tuple[str, str]:
    """Return (state, description) for the ivv/verdict commit status."""
    if not head_ref.startswith("claude/"):
        return "success", "not a claude/* branch; no verdict required"
    latest = None
    for body in comments:  # oldest first; the last matching verdict wins
        m = HEADING.search(body)
        if m and head_sha.startswith(m.group(1)):
            r = RULING.search(body[m.end():])
            if r:
                latest = r.group(1)
    if latest is None:
        return "pending", f"waiting for an independent verdict on {head_sha[:7]}"
    if latest == "FAIL":
        return "failure", f"independent verdict FAIL on {head_sha[:7]}"
    return "success", f"independent verdict {latest} on {head_sha[:7]}"


def _api(method: str, path: str, token: str, body: dict[str, Any] | None = None) -> Any:
    req = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"Accept": "application/vnd.github+json", "Authorization": "Bearer " + token},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> int:
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    number = os.environ["PR_NUMBER"]
    pr = _api("GET", f"/repos/{repo}/pulls/{number}", token)
    bodies: list[str] = []
    page = 1
    while True:
        chunk = _api("GET", f"/repos/{repo}/issues/{number}/comments?per_page=100&page={page}", token)
        bodies += [c.get("body") or "" for c in chunk]
        if len(chunk) < 100:
            break
        page += 1
    state, desc = verdict_state(pr["head"]["ref"], pr["head"]["sha"], bodies)
    _api("POST", f"/repos/{repo}/statuses/{pr['head']['sha']}", token,
         {"state": state, "context": CONTEXT, "description": desc[:140]})
    print(f"{CONTEXT}: {state} - {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
