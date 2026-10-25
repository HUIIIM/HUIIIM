import json, os
from playwright.sync_api import sync_playwright

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(BASE)
LOGO_LIGHT = '/home/hatch/workspace/.scratch/ws35/assets/site/logo.svg'
LOGO_DARK = '/home/hatch/workspace/.scratch/ws35/assets/site/logo-reverse.svg'

CSS = '''
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Nunito Sans",sans-serif}
.mono{font-family:"JetBrains Mono",monospace}
'''

def hero(theme):
    dark = theme == 'dark'
    bg = '#000000' if dark else '#FFFFFF'
    ink = '#FFFFFF' if dark else '#000000'
    sub = '#BFBFBF' if dark else '#3F3F3F'
    stone = '#8A8A8A' if dark else '#6B6B6B'
    line = '#2E2E2E' if dark else '#DEDEDE'
    logo = LOGO_DARK if dark else LOGO_LIGHT
    return f'''<html><head><style>{CSS}
body{{background:{bg}}}
.hero{{width:896px;height:320px;padding:40px 48px 28px;position:relative;display:flex;flex-direction:column}}
.lockup{{height:44px}}
.lockup img{{height:44px}}
.name{{font-size:78px;font-weight:800;letter-spacing:-1.5px;color:{ink};line-height:1.02;margin-top:24px}}
.pillars{{display:flex;gap:18px;align-items:center;margin-top:13px;font-size:24px;color:{sub};font-weight:700}}
.pillars .sep{{width:26px;height:2px;background:{line}}}
.motif{{position:absolute;right:48px;top:150px;font-size:25px;color:{ink};letter-spacing:.5px}}
.motif .arr{{color:#FF4713;font-weight:700}}
.foot{{margin-top:auto;border-top:1px solid {line};padding-top:13px;display:flex;justify-content:space-between;font-size:21px}}
.foot .dom{{color:#FF4713;font-weight:800}}
.foot .city{{color:{stone};font-weight:700}}
</style></head><body><div class="hero">
<div class="lockup"><img src="file://{logo}"></div>
<div class="name">Jiahui Miao</div>
<div class="pillars"><span>Founder, vertciti</span><span class="sep"></span><span>3GPP &middot; 6G core network standards</span></div>
<div class="motif mono">{{ source }} <span class="arr">&rarr;</span> {{ target }}</div>
<div class="foot"><span class="dom">vertciti.com</span><span class="city">New York</span></div>
</div></body></html>'''

def card(theme, c):
    dark = theme == 'dark'
    bg = '#000000' if dark else '#FFFFFF'
    ink = '#FFFFFF' if dark else '#000000'
    desc = '#BFBFBF' if dark else '#3F3F3F'
    stone = '#8A8A8A' if dark else '#6B6B6B'
    line = '#2E2E2E' if dark else '#DEDEDE'
    tilebg = '#FFFFFF' if dark else '#000000'
    tilefg = '#000000' if dark else '#FFFFFF'
    if c['status'] == 'Live':
        pill = 'background:#1D8348;color:#FFFFFF'
    elif c['status'] == 'In development':
        pill = 'background:#FFCE00;color:#000000'
    else:
        pill = f'background:transparent;color:{stone};border:1.5px solid {line}'
    return f'''<html><head><style>{CSS}
body{{background:{bg}}}
.card{{width:896px;height:188px;padding:26px 36px;position:relative;border-top:1px solid {line};display:flex;gap:28px}}
.tile{{flex:none;width:96px;height:96px;margin-top:20px;background:{tilebg};color:{tilefg};font-size:52px;font-weight:800;display:flex;align-items:center;justify-content:center}}
.main{{flex:1;display:flex;flex-direction:column}}
.row1{{display:flex;justify-content:space-between;align-items:flex-start}}
.name{{font-size:33px;font-weight:800;color:{ink};letter-spacing:-.5px}}
.pill{{font-size:19px;font-weight:800;padding:7px 16px;{pill}}}
.desc{{font-size:22.5px;color:{desc};margin-top:7px;line-height:1.3;font-weight:400}}
.row3{{margin-top:auto;display:flex;justify-content:space-between;align-items:center}}
.stack{{font-size:19.5px;color:{stone}}}
.arr{{color:#FF4713;font-size:26px;font-weight:800}}
</style></head><body><div class="card">
<div class="tile">{c['tile']}</div>
<div class="main"><div class="row1"><div class="name">{c['name']}</div><div class="pill">{c['status']}</div></div>
<div class="desc">{c['desc']}</div>
<div class="row3"><div class="stack mono">{c['stack']}</div><div class="arr">&rarr;</div></div>
</div></body></html>'''

def strip(theme):
    dark = theme == 'dark'
    bg = '#000000' if dark else '#FFFFFF'
    ink = '#FFFFFF' if dark else '#000000'
    txt = '#BFBFBF' if dark else '#3F3F3F'
    stone = '#8A8A8A' if dark else '#6B6B6B'
    line = '#2E2E2E' if dark else '#DEDEDE'
    badge = 'background:#FFFFFF;color:#000000' if dark else 'background:#000000;color:#FFFFFF'
    return f'''<html><head><style>{CSS}
body{{background:{bg}}}
.strip{{width:896px;height:118px;padding:26px 36px;border-top:1px solid {line};display:flex;align-items:center;gap:26px}}
.k{{font-size:19px;color:{stone};letter-spacing:2.5px;font-weight:700}}
.t{{font-size:23.5px;color:{txt};flex:1;line-height:1.35}}
.badge{{font-size:20px;font-weight:800;padding:9px 18px;{badge}}}
</style></head><body><div class="strip">
<div class="k mono">GRADED<br>DAILY</div>
<div class="t">Every repository is graded daily by our own assessor. Red grades are published too.</div>
<div class="badge">BAR A++</div>
</div></body></html>'''

CARDS = [
    {'tile': 'D', 'name': 'DealDesk', 'status': 'Live', 'desc': 'Real-estate deal underwriting &mdash; rent roll, T12, model and IC pack in one flow.', 'stack': 'Python &middot; FastAPI &middot; TypeScript'},
    {'tile': 'E', 'name': 'EchoWatch', 'status': 'Live', 'desc': 'Self-hosted media monitoring that opens with a verdict. Live demo; source private.', 'stack': 'Python &middot; FastAPI &middot; SQLite FTS5'},
    {'tile': 'M', 'name': 'Miao AI', 'status': 'Private', 'desc': 'N=1 personal AI infrastructure &mdash; agents, memory, guardrails; runs its founder&rsquo;s life.', 'stack': 'Python &middot; TypeScript &middot; MCP'},
    {'tile': 'F', 'name': 'FAMA', 'status': 'In development', 'desc': 'Judicial-disposal real-estate data infrastructure (China). In development; not yet offered.', 'stack': 'Python &middot; PostgreSQL &middot; Playwright'},
]

jobs = []
for theme in ('light', 'dark'):
    jobs.append((f'hero-{theme}.png', hero(theme), 896, 320))
    jobs.append((f'graded-{theme}.png', strip(theme), 896, 118))
    for i, c in enumerate(CARDS):
        slug = ['dealdesk', 'echowatch', 'miao-ai', 'fama'][i]
        jobs.append((f'card-{slug}-{theme}.png', card(theme, c), 896, 188))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/meta-chromium/chrome', args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'])
    for fname, html, w, h in jobs:
        src = os.path.join(BASE, fname.replace('.png', '.html'))
        open(src, 'w').write(html)
        pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
        pg.goto('file://' + src)
        pg.wait_for_timeout(350)
        pg.screenshot(path=os.path.join(OUT, fname))
        pg.close()
        print('rendered', fname)
    b.close()
