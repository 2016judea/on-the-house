"""Midtown Global Market, Minneapolis — "most of the vendors were closed." A who's-open-now page.

Evidence:
  - 13 of the 500 most recent Google reviews (pulled 2026-05-18, matched by a strict phrase
    regex, so a floor not a ceiling) say they arrived to find the vendors closed:
    "half the vendors were closed", "most of the stands had closed", "Many stalls are closed".
  - The market's own Merchants page (read 2026-09-26) lists 35 merchants. 25 print usable
    hours; 10 print none (or no days), so a visitor can't tell who will be open.
The page computes open/closed live in Minneapolis time from the hours each merchant printed
on the market's own page. Nothing is guessed: a merchant without printed hours says so.
"""
from __future__ import annotations

import json

from common import ROOT, esc, page, save_plan

SLUG = "midtown-global-market"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
# Printed hours that name no days, or say "one per month": show the text, don't compute.
NOT_COMPUTABLE = {"Sanchez Jewelry": "11am-7pm (days not listed)"}

JS = """
<script>
const M = __DATA__;
const days=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
function now(){const p=new Intl.DateTimeFormat('en-US',{timeZone:'America/Chicago',weekday:'short',hour:'2-digit',minute:'2-digit',hour12:false}).formatToParts(new Date());
 const g=t=>p.find(x=>x.type===t).value; return {day:g('weekday'),min:(+g('hour')%24)*60+(+g('minute'))};}
const toMin=s=>{const [h,m]=s.split(':').map(Number);return h*60+m};
const fmt=s=>{let [h,m]=s.split(':').map(Number);const ap=h>=12?'pm':'am';h=h%12||12;return h+(m?':'+String(m).padStart(2,'0'):'')+ap};
function render(){
 const {day,min}=now(); const open=[],later=[],closed=[],unknown=[];
 for(const m of M){ if(!m.hours){unknown.push(m);continue}
  const h=m.hours[day]; if(!h){closed.push(m);continue}
  const a=toMin(h[0]),b=toMin(h[1]);
  if(min>=a&&min<b) open.push([m,'until '+fmt(h[1])]); else if(min<a) later.push([m,'opens '+fmt(h[0])]); else closed.push(m);}
 const order=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]; const i0=order.indexOf(day);
 const next=m=>{for(let k=1;k<=7;k++){const d=order[(i0+k)%7];const h=m.hours[d];if(h)return 'opens '+(k===1?'tomorrow':d)+' '+fmt(h[0])}return ''};
 const li=(m,t)=>`<div class="v"><div class="row"><b>${m.name}</b><span>${t||''}</span></div><div class="meta">${m.what||''}</div></div>`;
 document.getElementById('clock').textContent=new Intl.DateTimeFormat('en-US',{timeZone:'America/Chicago',weekday:'long',hour:'numeric',minute:'2-digit'}).format(new Date());
 document.getElementById('n').textContent=open.length;
 document.getElementById('open').innerHTML=open.map(([m,t])=>li(m,t)).join('')||'<p class="meta">Nobody right now.</p>';
 document.getElementById('later').innerHTML=later.map(([m,t])=>li(m,t)).join('')||'<p class="meta">—</p>';
 document.getElementById('closed').innerHTML=closed.map(m=>li(m,next(m))).join('')||'<p class="meta">—</p>';
 document.getElementById('unknown').innerHTML=unknown.map(m=>li(m,m.printed||'no hours posted')).join('');
}
render(); setInterval(render,60000);
</script>"""

CSS = """
.v{padding:.45rem 0;border-bottom:1px solid var(--line)}
.row{display:flex;justify-content:space-between;gap:1rem;font-family:ui-sans-serif,system-ui,sans-serif}
.row span{white-space:nowrap;color:var(--mute);font-size:14px}
.big{font:700 3rem/1 ui-sans-serif,system-ui,sans-serif;color:var(--ok)}
"""


def main() -> None:
    ms = json.load(open(ROOT / "work" / SLUG / "merchants.json"))["merchants"]
    data = []
    for m in ms:
        hours = None if m["name"] in NOT_COMPUTABLE else m["hours"]
        data.append({"name": m["name"], "what": m["what"], "hours": hours,
                     "printed": NOT_COMPUTABLE.get(m["name"])})
    posted = sum(1 for d in data if d["hours"])
    week = "".join(
        f"<tr><td>{esc(d['name'])}</td>" + "".join(
            f"<td>{'–'.join(x[:5] for x in d['hours'][k]) if d['hours'][k] else 'closed'}</td>" for k in DAYS) + "</tr>"
        for d in data if d["hours"])
    body = f"""
<p class="meta">Midtown Global Market · 920 E Lake St, Minneapolis</p>
<h1>Who's open right now</h1>
<p class="sans" id="clock"></p>
<p><span class="big" id="n">–</span> <span class="sans">merchants open</span></p>
<div id="open"></div>
<h2>Opening later today</h2><div id="later"></div>
<h2>Closed now</h2><div id="closed"></div>
<h2>No hours posted</h2>
<p class="meta">These merchants don't list hours on the market's Merchants page yet.</p>
<div id="unknown"></div>
<h2>The whole week</h2>
<div class="scroll"><table><tr><th></th>{''.join(f'<th>{d}</th>' for d in DAYS)}</tr>{week}</table></div>
<p class="meta">Built from the hours each merchant prints on midtownglobalmarket.org/merchants, read September 26, 2026. Updates itself every minute.</p>
"""
    strip = "Built for Midtown Global Market by Brick &amp; Mortar from your own Merchants page. Nothing on your site was changed."
    page(SLUG, "Midtown Global Market — open now", body, strip=strip, css=CSS,
         extra_head="")
    out = ROOT / "site" / SLUG / "index.html"
    out.write_text(out.read_text().replace("</body>", JS.replace("__DATA__", json.dumps(data)) + "</body>"))
    save_plan(SLUG, {
        "slug": SLUG, "headline": "Visitors keep finding the vendors closed. We built a page that shows who's open right now.",
        "gift_path": f"/{SLUG}/",
        "evidence": ["13 of 500 recent Google reviews say they found vendors closed (strict phrase match)",
                     f"{len(data)} merchants on the Merchants page; {posted} print usable hours, {len(data) - posted} don't"],
        "to_use_it": "Link it from the website and a QR sign at each entrance.",
        "menu": ["gbp_cleanup", "ai_listings", "review_replies_monthly"],
    })
    print("built", SLUG, len(data), posted)


if __name__ == "__main__":
    main()
