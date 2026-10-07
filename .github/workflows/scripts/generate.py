#!/usr/bin/env python3
"""Self-hosted GitHub stats SVG generator (vertciti brand).

Fetches public data for the target user from the GitHub REST API and renders
two branded SVG cards:
  - stats.svg : total stars, forks, public repos, followers
  - langs.svg : language distribution across public repos (bytes, top 8)

v1: dependency-free (stdlib only), honest data only (no private contributions,
no fabricated numbers). Replace the github-readme-stats.vercel.app cards with
the raw.githubusercontent.com links to these files.

Usage:
    GH_USER=HUIIIM GH_TOKEN=<token> python3 generate.py [--user HUIIIM] [--out ./assets]

The workflow (stats.yml) runs this daily and commits the SVGs to this repo.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

# --- vertciti brand palette (dark card, green accent) -------------------------
BG = "#0d1117"
BORDER = "#2ea043"
ACCENT = "#3fb950"
ACCENT_DIM = "#238636"
TEXT = "#e6edf3"
TEXT_DIM = "#8b949e"
FONT = "font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif'"

LANG_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572A5",
    "Java": "#b07219", "Go": "#00ADD8", "Rust": "#dea584", "Ruby": "#701516",
    "Shell": "#89e051", "C": "#555555", "HTML": "#e34c26", "Markdown": "#083fa1",
    "PHP": "#4F5D95", "Makefile": "#427819", "C++": "#f34b7d", "CSS": "#563d7c",
}
FALLBACK_LANG = "#6e7681"


def api(path: str, token: str | None, params: dict | None = None):
    url = "https://api.github.com" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def paged(path: str, token: str | None):
    items, page = [], 1
    while True:
        chunk = api(path, token, {"per_page": 100, "page": page})
        if not chunk:
            break
        items.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return items


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def stats_svg(name: str, stars: int, forks: int, repos: int, followers: int,
              generated: str) -> str:
    items = [
        ("★", "Total Stars", stars),
        ("⑂", "Forks", forks),
        ("▤", "Public Repos", repos),
        ("◉", "Followers", followers),
    ]
    rows = []
    y = 78
    for icon, label, value in items:
        rows.append(
            f"<text x='28' y='{y}' {FONT} font-size='15' fill='{ACCENT}'>{icon}</text>"
            f"<text x='52' y='{y}' {FONT} font-size='15' fill='{TEXT_DIM}'>{esc(label)}</text>"
            f"<text x='372' y='{y}' text-anchor='end' {FONT} font-size='15' "
            f"font-weight='700' fill='{TEXT}'>{value:,}</text>")
        y += 34
    rows_svg = "\n".join(rows)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="236" role="img" aria-label="GitHub stats for {esc(name)}">
<rect x="0.5" y="0.5" width="399" height="235" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<text x="28" y="40" {FONT} font-size="18" font-weight="700" fill="{TEXT}">{esc(name)}'s GitHub Stats</text>
<text x="372" y="40" text-anchor="end" {FONT} font-size="11" fill="{ACCENT}">vertciti</text>
{rows_svg}
<text x="28" y="228" {FONT} font-size="10" fill="{TEXT_DIM}">public data · generated {esc(generated)} · github.com/{esc(name)}</text>
</svg>
"""


def langs_svg(langs: list[tuple[str, float]], generated: str) -> str:
    if not langs:
        langs = [("No public code yet", 100.0)]
    bar_w = 344
    segs, labels = [], []
    x, y = 28, 78
    for i, (lang, pct) in enumerate(langs):
        color = LANG_COLORS.get(lang, FALLBACK_LANG)
        w = max(bar_w * pct / 100.0, 2)
        segs.append(f"<rect x='{x:.1f}' y='{y}' width='{w:.1f}' height='10' rx='5' fill='{color}'/>")
        lx = 28 + (i % 2) * 172
        ly = y + 34 + (i // 2) * 24
        labels.append(
            f"<circle cx='{lx}' cy='{ly - 4}' r='5' fill='{color}'/>"
            f"<text x='{lx + 12}' y='{ly}' {FONT} font-size='12' fill='{TEXT}'>{esc(lang)}</text>"
            f"<text x='{lx + 150}' y='{ly}' text-anchor='end' {FONT} font-size='12' fill='{TEXT_DIM}'>{pct:.1f}%</text>")
        x += w
    rows_h = ((len(langs) - 1) // 2) * 24
    height = 150 + rows_h
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{height}" role="img" aria-label="Top languages">
<rect x="0.5" y="0.5" width="399" height="{height - 1}" rx="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
<text x="28" y="40" {FONT} font-size="18" font-weight="700" fill="{TEXT}">Top Languages</text>
<text x="372" y="40" text-anchor="end" {FONT} font-size="11" fill="{ACCENT}">vertciti</text>
{"".join(segs)}
{"".join(labels)}
<text x="28" y="{height - 8}" {FONT} font-size="10" fill="{TEXT_DIM}">by code bytes across public repos · generated {esc(generated)}</text>
</svg>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GH_USER", "HUIIIM"))
    ap.add_argument("--out", default=os.environ.get("SVG_OUT", "./assets"))
    args = ap.parse_args()
    token = os.environ.get("GH_TOKEN")

    user = api(f"/users/{args.user}", token)
    repos = [r for r in paged(f"/users/{args.user}/repos", token) if not r.get("private")]

    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)
    followers = user.get("followers", 0)

    lang_bytes: dict[str, int] = {}
    for r in repos:
        try:
            for lang, n in api(r["languages_url"].replace("https://api.github.com", ""), token).items():
                lang_bytes[lang] = lang_bytes.get(lang, 0) + n
        except Exception as e:  # per-repo failure must not kill the whole card
            print(f"warn: languages for {r['full_name']} failed: {e}", file=sys.stderr)
    total = sum(lang_bytes.values()) or 1
    top = sorted(lang_bytes.items(), key=lambda kv: -kv[1])[:8]
    langs = [(l, b / total * 100) for l, b in top]

    generated = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "stats.svg"), "w", encoding="utf-8") as f:
        f.write(stats_svg(args.user, stars, forks, len(repos), followers, generated))
    with open(os.path.join(args.out, "langs.svg"), "w", encoding="utf-8") as f:
        f.write(langs_svg(langs, generated))

    print(json.dumps({
        "user": args.user, "stars": stars, "forks": forks,
        "public_repos": len(repos), "followers": followers,
        "top_languages": [l for l, _ in langs], "generated": generated,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
