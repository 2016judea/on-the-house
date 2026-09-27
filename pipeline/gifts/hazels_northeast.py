"""Hazel's Northeast, Minneapolis — the same two health-inspection items, three visits running.

Evidence: Minneapolis food inspection open data (bricks/data/cache/licences/mpls_food,
records through 2026-08-07), licence holder GOOD CHEER HOSPITALITY LLC, 2859 Johnson St NE.
  - 2024-07-10 routine (86): cold station 2 at 42-45F; no illness log; 7-day date marks; no test strips
  - 2024-08-06 follow-up (96): cold station 2 at 47-50F
  - 2025-07-09 routine (92): topless cold station at 45-47F; no illness log; 4 minor items
  Both routines fell in July. No 2026 routine is in the data yet.
The gift is the paperwork the inspector asked for, made for their line, ready to print.
"""
from __future__ import annotations

import json

from common import ROOT, esc, page, save_plan

SLUG = "hazels-northeast"

SHEET_CSS = """
@page{size:letter;margin:.5in}
.sheet{break-after:page}
.sheet table{font-size:12px}
.sheet td,.sheet th{border:1px solid #999;height:26px}
.sheet h2{margin-top:0}
"""


def log_sheet() -> str:
    rows = "".join("<tr>" + "<td></td>" * 7 + "</tr>" for _ in range(16))
    return f"""<div class="sheet"><h2>Cold line temperature log — Hazel's Northeast</h2>
<p class="meta">Probe the food, not the air: one item from the front and one from the back of the cold station. 41°F or colder. Twice a shift.</p>
<table><tr><th>Date</th><th>Time</th><th>Item (front)</th><th>°F</th><th>Item (back)</th><th>°F</th><th>If over 41°F: what we did · initials</th></tr>{rows}</table>
<p class="meta">Over 41°F: turn the dial down, don't overfill the pans, recheck in 30 minutes. Food over 41°F for more than 4 hours gets thrown out.</p></div>"""


def illness_sheet() -> str:
    rows = "".join("<tr>" + "<td></td>" * 6 + "</tr>" for _ in range(14))
    return f"""<div class="sheet"><h2>Employee illness log — Hazel's Northeast</h2>
<p class="meta">Keep this where the inspector can see it. Staff tell the person in charge if they have any of these: vomiting, diarrhea, jaundice (yellow skin or eyes), sore throat with fever, or an infected cut or burn on the hands or arms.</p>
<table><tr><th>Date</th><th>Employee</th><th>Symptom</th><th>Reported to</th><th>Action (sent home / restricted / cleared)</th><th>Return date</th></tr>{rows}</table>
<p class="meta">Vomiting or diarrhea: stay out until 24 hours after symptoms stop.</p></div>"""


def main() -> None:
    insp = json.load(open(ROOT / "work" / SLUG / "inspections.json"))
    visits = {}
    for r in insp:
        visits.setdefault((r["date"], r["InspectionType"], r["InspectionScore"]), []).append(r)
    vrows = ""
    for (d, typ, score), rs in sorted(visits.items()):
        items = [r for r in rs if r["InspectorComments"]]
        cold = any("41" in (r["InspectorComments"] or "") for r in items)
        ill = any("illness" in (r["InspectorComments"] or "").lower() for r in items)
        vrows += (f"<tr><td>{d}</td><td>{esc(typ)}</td><td>{score}</td>"
                  f"<td class='{'bad' if cold else ''}'>{'warm' if cold else 'ok'}</td>"
                  f"<td class='{'bad' if ill else ''}'>{'missing' if ill else ('not checked' if typ == 'Follow-Up' else 'ok')}</td></tr>")
    last = [r for r in insp if r["date"] == "2025-07-09" and r["ViolationPriority"] == "Priority3"]
    minor = "".join(f"<li>{esc(r['InspectorComments'].split('.')[0].replace('Observed ', '').capitalize())}.</li>" for r in last)
    quotes = [r["InspectorComments"].split(" Maintain")[0] for r in insp if "41" in (r["InspectorComments"] or "")]
    body = f"""
<p class="meta">For Hazel's Northeast · 2859 Johnson St NE · from Minneapolis's public inspection records</p>
<h1>Your cold line has read warm at three inspections in a row.</h1>
<p class="lede">Cold food above 41°F in July 2024, August 2024 and July 2025. The employee illness log was missing at both routine visits too. We made you a temperature log for the line and the illness log, ready to print.</p><p>Your routine visits were in July both years. The city's data has no 2026 visit yet.</p>
<p class="noprint"><a class="btn" href="print/">Print the two sheets</a></p>

<h2>What the reports say</h2>
<div class="scroll"><table><tr><th>Date</th><th>Visit</th><th>Score</th><th>Cold line</th><th>Illness log</th></tr>{vrows}</table></div>
{''.join(f'<blockquote>{esc(q.rstrip("."))}.</blockquote>' for q in quotes)}

<h2>The small stuff from July 2025</h2>
<ul>{minor}</ul>
<p class="meta">Source: City of Minneapolis food inspection data, licence holder Good Cheer Hospitality LLC. Records through August 7, 2026.</p>
"""
    strip = "Put together for Hazel's Northeast by Brick &amp; Mortar from the city's public inspection records."
    page(SLUG, "Hazel's Northeast — inspection sheets", body, strip=strip)
    page(SLUG, "Hazel's — sheets to print", log_sheet() + illness_sheet(), sub="print",
         strip='Print (letter). <a href="../">Back</a>', css=SHEET_CSS)
    save_plan(SLUG, {
        "slug": SLUG, "headline": "Your cold line has read warm at three inspections in a row. We made the log sheets for it.",
        "gift_path": f"/{SLUG}/", "print_path": f"/{SLUG}/print/",
        "evidence": ["Minneapolis inspections 2024-07-10, 2024-08-06, 2025-07-09: cold food 42-50F each time",
                     "no illness log at both routine visits", "both routines in July; none yet in 2026 data (through 2026-08-07)"],
        "to_use_it": "Print both sheets, tape the log by the cold station.",
        "menu": ["review_replies_monthly", "gbp_cleanup", "online_ordering"],
    })
    print("built", SLUG)


if __name__ == "__main__":
    main()
