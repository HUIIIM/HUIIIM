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

Only verdicts from an independent assessor identity count (IVV.md rule 1:
the author never grades itself). Every authoring session here comments as the
repository owner, so the allowlist names the assessor's identity instead: a
login or a GitHub App slug, from IVV_ASSESSORS (comma-separated; default
``github-actions[bot]``). Edited comments are NOT excluded: verdicts are delivered
through claude-code-action as a placeholder comment edited in place, so an edit
exclusion would starve the gate forever. Tampering is contained by three layers
instead: (1) the verdict is bound to the full current head sha, so a verdict
tampered to point at another head mismatches the live head and fails closed;
(2) only identities in the assessor list count; (3) a comment can only be edited
by its author, and its edit history is visible and auditable.

Environment: GITHUB_TOKEN, GITHUB_REPOSITORY (owner/name), PR_NUMBER,
optional IVV_ASSESSORS.
The status is the signal; the script exits 0 unless the API call fails.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from typing import Any

CONTEXT = "ivv/verdict"
DEFAULT_ASSESSORS = "github-actions[bot]"
HEADING = re.compile(r"^###\s*独立评估\s*·\s*SOTA[^·\n]*·\s*([0-9a-f]{7,40})\s*$", re.MULTILINE)
RULING = re.compile(r"判定[:：]\s*(PASS|FAIL|N/A)")


@dataclass(frozen=True)
class Comment:
    body: str
    author: str  # user.login
    app: str = ""  # performed_via_github_app.slug, if any


def parse_assessors(raw: str | None) -> frozenset[str]:
    return frozenset(x.strip() for x in (raw or DEFAULT_ASSESSORS).split(",") if x.strip())


def verdict_state(head_ref: str, head_sha: str, comments: list[Comment],
                  assessors: frozenset[str]) -> tuple[str, str]:
    """Return (state, description) for the ivv/verdict commit status."""
    if not head_ref.startswith("claude/"):
        return "success", "not a claude/* branch; no verdict required"
    latest = None
    for c in comments:  # oldest first; the last counting verdict wins
        if not ({c.author, c.app} & assessors):
            continue
        m = HEADING.search(c.body)
        if m and head_sha.startswith(m.group(1)):
            r = RULING.search(c.body[m.end():])
            if r:
                latest = r.group(1)
    if latest is None:
        return "pending", f"waiting for an independent assessor verdict on {head_sha[:7]}"
    if latest == "FAIL":
        return "failure", f"independent verdict FAIL on {head_sha[:7]}"
    return "success", f"independent verdict {latest} on {head_sha[:7]}"


def to_comment(raw: dict[str, Any]) -> Comment:
    app = raw.get("performed_via_github_app") or {}
    return Comment(body=raw.get("body") or "", author=(raw.get("user") or {}).get("login", ""),
                   app=app.get("slug", ""))


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
    comments: list[Comment] = []
    page = 1
    while True:
        chunk = _api("GET", f"/repos/{repo}/issues/{number}/comments?per_page=100&page={page}", token)
        comments += [to_comment(c) for c in chunk]
        if len(chunk) < 100:
            break
        page += 1
    state, desc = verdict_state(pr["head"]["ref"], pr["head"]["sha"], comments,
                                parse_assessors(os.environ.get("IVV_ASSESSORS")))
    _api("POST", f"/repos/{repo}/statuses/{pr['head']['sha']}", token,
         {"state": state, "context": CONTEXT, "description": desc[:140]})
    print(f"{CONTEXT}: {state} - {desc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
