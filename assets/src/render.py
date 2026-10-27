import os
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(BASE)
# Logo sources live in the website repo's asset tree, not this one: point
# VERTCITI_LOGO_LIGHT / VERTCITI_LOGO_DARK at local copies, or drop logo.svg /
# logo-reverse.svg next to this script (the default lookup below).
LOGO_LIGHT = os.environ.get('VERTCITI_LOGO_LIGHT', os.path.join(BASE, 'logo.svg'))
LOGO_DARK = os.environ.get('VERTCITI_LOGO_DARK', os.path.join(BASE, 'logo-reverse.svg'))
for _logo in (LOGO_LIGHT, LOGO_DARK):
    if not os.path.isfile(_logo):
        raise SystemExit(f'missing logo {_logo}: set VERTCITI_LOGO_LIGHT / VERTCITI_LOGO_DARK (a missing file renders a broken image in the hero)')
# Any Playwright Chromium works; CHROMIUM_PATH picks a specific binary.
CHROMIUM = os.environ.get('CHROMIUM_PATH')
CSS = '*{margin:0;padding:0;box-sizing:border-box}body{font-family:"Nunito Sans",sans-serif}.mono{font-family:"JetBrains Mono",monospace}'

def hero(theme):
    dark = theme == 'dark'
    bg = '#000' if dark else '#FFF'
    ink = '#FFF' if dark else '#000'
    stone = '#9A9A9A' if dark else '#6B6B6B'
    line = '#2E2E2E' if dark else '#DEDEDE'
    logo = LOGO_DARK if dark else LOGO_LIGHT
    return f'''<html><head><style>{CSS}
body{{background:{bg}}}
.hero{{width:896px;height:320px;padding:46px 48px 30px;display:flex;flex-direction:column}}
.name{{font-size:104px;font-weight:800;letter-spacing:-1px;color:{ink};line-height:1.04}}
.foot{{margin-top:auto;border-top:1px solid {line};padding-top:15px;display:flex;justify-content:space-between;align-items:center}}
.facts{{font-size:19.5px;color:{stone};font-weight:700}}
.cluster{{display:flex;align-items:center;gap:14px}}
.rule{{width:64px;height:8px;background:#FF4713}}
.cluster img{{height:21px}}
</style></head><body><div class="hero">
<div class="name">JIAHUI MIAO</div>
<div class="foot"><div class="facts">Founder, vertciti · 3GPP 6G core network standards · New York</div>
<div class="cluster"><span class="rule"></span><img src="file://{logo}"></div></div>
</div></body></html>'''

MOTIFS = {
 'dealdesk': lambda ink, stone, line: f'''
<svg width="252" height="120" viewBox="0 0 252 120">
<g font-family="JetBrains Mono" font-size="17" fill="{stone}">
<text x="6" y="22">1 204</text><text x="86" y="22">87</text><text x="150" y="22">3 412</text>
<text x="6" y="50">09</text><text x="86" y="50">640</text><text x="150" y="50">28</text>
<text x="6" y="78">512</text><text x="86" y="78">1 096</text><text x="150" y="78">73</text></g>
<line x1="4" y1="94" x2="212" y2="94" stroke="#FF4713" stroke-width="3"/>
<line x1="4" y1="102" x2="212" y2="102" stroke="{ink}" stroke-width="1.5"/>
</svg>''',
 'echowatch': lambda ink, stone, line: f'''
<svg width="252" height="120" viewBox="0 0 252 120">
<g fill="none" stroke-width="9">
<circle cx="126" cy="60" r="16" stroke="{stone}"/>
<circle cx="126" cy="60" r="33" stroke="{ink}"/>
<circle cx="126" cy="60" r="50" stroke="{stone}"/></g>
<circle cx="159" cy="33" r="7.5" fill="#FF4713"/>
</svg>''',
 'miao-ai': lambda ink, stone, line: f'''
<svg width="252" height="120" viewBox="0 0 252 120">
<g stroke="{stone}" stroke-width="2">
<line x1="126" y1="60" x2="36" y2="24"/><line x1="126" y1="60" x2="216" y2="24"/>
<line x1="126" y1="60" x2="36" y2="98"/><line x1="126" y1="60" x2="216" y2="98"/>
<line x1="36" y1="24" x2="216" y2="24"/><line x1="36" y1="98" x2="216" y2="98"/></g>
<g fill="{ink}"><rect x="29" y="17" width="14" height="14"/><rect x="209" y="17" width="14" height="14"/>
<rect x="29" y="91" width="14" height="14"/><rect x="209" y="91" width="14" height="14"/></g>
<rect x="117" y="51" width="18" height="18" fill="#FF4713"/>
</svg>''',
 'fama': lambda ink, stone, line: f'''
<svg width="252" height="120" viewBox="0 0 252 120">
<g stroke="{ink}" stroke-width="2.5" fill="none">
<line x1="26" y1="34" x2="226" y2="34"/>
<line x1="56" y1="34" x2="42" y2="66"/><line x1="56" y1="34" x2="70" y2="66"/><line x1="34" y1="66" x2="78" y2="66"/>
<line x1="196" y1="34" x2="182" y2="66"/><line x1="196" y1="34" x2="210" y2="66"/><line x1="174" y1="66" x2="218" y2="66"/>
<line x1="126" y1="34" x2="126" y2="88"/><line x1="88" y1="102" x2="164" y2="102"/></g>
<path d="M126 44 L113 74 L139 74 Z" fill="#FF4713"/>
<path d="M104 88 L148 88 L138 102 L114 102 Z" fill="{ink}"/>
</svg>''',
}

def card(theme, c, slug):
    dsize = c.get('desc_size', 22.5)
    dark = theme == 'dark'
    bg = '#000' if dark else '#FFF'
    ink = '#FFF' if dark else '#000'
    desc = '#BFBFBF' if dark else '#3F3F3F'
    stone = '#8A8A8A' if dark else '#6B6B6B'
    line = '#2E2E2E' if dark else '#DEDEDE'
    tilebg = '#FFF' if dark else '#000'
    tilefg = '#000' if dark else '#FFF'
    dot = {'Live': 'background:#1D8348', 'In development': 'background:#FFCE00'}.get(c['status'], f'border:2px solid {stone}')
    motif = MOTIFS[slug](ink, stone, line)
    return f'''<html><head><style>{CSS}
body{{background:{bg}}}
.card{{width:896px;height:216px;padding:26px 36px;border-top:1px solid {line};display:flex;gap:28px;position:relative}}
.tile{{flex:none;width:96px;height:96px;margin-top:20px;background:{tilebg};color:{tilefg};font-size:52px;font-weight:800;display:flex;align-items:center;justify-content:center}}
.main{{flex:1;display:flex;flex-direction:column}}
.name{{font-size:33px;font-weight:800;color:{ink};letter-spacing:-.5px}}
.desc{{font-size:{dsize}px;color:{desc};margin-top:8px;line-height:1.3;max-width:430px}}
.dot{{position:absolute;top:32px;right:36px;width:15px;height:15px;{dot}}}
.motif{{position:absolute;right:30px;top:40px}}
.stack{{margin-top:auto;font-size:19.5px;color:{stone}}}
</style></head><body><div class="card">
<div class="tile">{c['tile']}</div>
<div class="main"><div class="name">{c['name']}</div><div class="desc">{c['desc']}</div><div class="stack mono">{c['stack']}</div></div>
<div class="dot"></div><div class="motif">{motif}</div>
</div></body></html>'''

CARDS = [
    ('dealdesk', {'tile': 'D', 'name': 'DealDesk', 'status': 'Live', 'desc': 'Real-estate deal underwriting &mdash; rent roll, T12, model and IC pack in one flow.', 'stack': 'Python &middot; FastAPI &middot; TypeScript'}),
    ('echowatch', {'tile': 'E', 'name': 'EchoWatch', 'status': 'Live', 'desc': 'Self-hosted media monitoring that opens with a verdict.', 'stack': 'Python &middot; FastAPI &middot; SQLite FTS5'}),
    ('miao-ai', {'tile': 'M', 'name': 'Miao AI', 'status': 'Private', 'desc': 'N=1 personal AI infrastructure &mdash; agents, memory, guardrails.', 'stack': 'Python &middot; TypeScript &middot; MCP'}),
    ('fama', {'tile': 'F', 'name': 'FAMA', 'status': 'In development', 'desc': 'Judicial-disposal real-estate data infrastructure (China), built for our own real-estate operations. In development; not yet offered externally, not a product or service offering.', 'desc_size': 19, 'stack': 'Python &middot; PostgreSQL &middot; Playwright'}),
]

jobs = []
for theme in ('light', 'dark'):
    jobs.append((f'hero-{theme}.png', hero(theme), 896, 320))
    for slug, c in CARDS:
        jobs.append((f'card-{slug}-{theme}.png', card(theme, c, slug), 896, 216))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROMIUM, args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'])
    for fname, html, w, h in jobs:
        src = os.path.join(BASE, fname.replace('.png', '.html'))
        open(src, 'w').write(html)
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
        pg.goto('file://' + src); pg.wait_for_timeout(350)
        pg.screenshot(path=os.path.join(OUT, fname)); pg.close()
        print('rendered', fname)
    b.close()
