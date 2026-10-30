#!/usr/bin/env python3
"""Checks that the profile README renders the way it reads.

Static checks (always, stdlib only):
  - a line that opens with an HTML comment must hold nothing but comments.
    CommonMark turns such a line into a raw HTML block, so any Markdown after
    the comment is shown literally (the "Graded daily" line did this);
  - every <img> has non-empty alt text;
  - every local image or link target exists in the repository.

Optional network checks:
  --render  renders README.md through the GitHub Markdown API (gfm) and fails if
            literal Markdown (``**`` or ``](``) survives into the visible text.
            Uses GITHUB_TOKEN when set.
  --links   requests every external link and fails on errors or timeouts.

Exit code 0 = clean, 1 = findings (printed one per line).
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMENT = re.compile(r"<!--.*?-->", re.S)
IMG = re.compile(r"<img\b[^>]*>", re.I)
ATTR = re.compile(r'(\w+)\s*=\s*"([^"]*)"')
SRCSET = re.compile(r'<source\b[^>]*\bsrcset="([^"]+)"', re.I)
MD_LINK = re.compile(r"\]\(([^)\s]+)\)")
HREF = re.compile(r'\bhref="([^"]+)"', re.I)
# Hosts that refuse automated clients but are reachable for people.
BOT_HOSTILE = {999: "linkedin.com", 403: "x.com"}


def static_findings(text: str, root: Path = ROOT) -> list[str]:
    out: list[str] = []
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("<!--"):
            rest = COMMENT.sub("", line).strip()
            if rest:
                out.append(f"README.md:{n}: Markdown after an HTML comment on one line renders literally: {rest[:60]!r}")
    for tag in IMG.findall(text):
        attrs = dict(ATTR.findall(tag))
        if not attrs.get("alt", "").strip():
            out.append(f"img without alt text: {tag[:80]}")
        src = attrs.get("src", "")
        if src and not re.match(r"[a-z]+:", src) and not (root / src).is_file():
            out.append(f"image not found: {src}")
    for src in SRCSET.findall(text):
        if not re.match(r"[a-z]+:", src) and not (root / src).is_file():
            out.append(f"image not found: {src}")
    for target in MD_LINK.findall(text) + HREF.findall(text):
        if re.match(r"([a-z]+:|#)", target):
            continue
        if not (root / target.split("#")[0]).exists():
            out.append(f"link target not found: {target}")
    return out


def visible_text(rendered_html: str) -> str:
    no_code = re.sub(r"<code>.*?</code>", "", rendered_html, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", no_code))


def render_findings(text: str) -> list[str]:
    body = json.dumps({"text": text, "mode": "gfm", "context": "HUIIIM/HUIIIM"}).encode()
    req = urllib.request.Request("https://api.github.com/markdown", data=body, method="POST",
                                 headers={"Accept": "application/vnd.github+json", "Content-Type": "application/json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        shown = visible_text(resp.read().decode())
    return [f"rendered README shows literal Markdown: {m!r}" for m in ("**", "](") if m in shown]


def external_links(text: str) -> list[str]:
    seen: list[str] = []
    for url in MD_LINK.findall(text) + HREF.findall(text):
        if url.startswith(("http://", "https://")) and url not in seen:
            seen.append(url)
    return seen


def link_findings(text: str, timeout: float = 30) -> list[str]:
    out = []
    for url in external_links(text):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (profile-readme-check)"})
        try:
            with urllib.request.urlopen(req, timeout=timeout):
                pass
        except urllib.error.HTTPError as e:
            host = BOT_HOSTILE.get(e.code)
            if not (host and host in url):
                out.append(f"{url}: HTTP {e.code}")
        except Exception as e:  # timeouts, DNS, TLS
            out.append(f"{url}: {type(e).__name__}: {e}")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--links", action="store_true")
    ap.add_argument("readme", nargs="?", default=str(ROOT / "README.md"))
    a = ap.parse_args(argv)
    text = Path(a.readme).read_text(encoding="utf-8")
    findings = static_findings(text)
    if a.render:
        findings += render_findings(text)
    if a.links:
        findings += link_findings(text)
    for f in findings:
        print(f)
    print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
