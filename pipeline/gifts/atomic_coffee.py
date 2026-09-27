"""Atomic Coffee, Fargo — the back room, and every office within a five-minute walk of it.

Evidence:
  - atomiccoffeefm.com/book-the-meeting-room: "Can accommodate up to 26 people. Only $25 to
    reserve the room for 2-4 hours." Booking is by phone only.
  - Their May 2026 report: a business already paid to meet in the room; nobody followed up.
  - OpenStreetMap (Overpass, 2026-09-26): named offices, firms, banks and nonprofits within
    450 m of 222 Broadway N. Walking minutes = straight line x 1.3 / 80 m per minute.
Deliverable: the list (nearest first) and a one-page flyer in Atomic's own words, to print
and drop off or hand across the counter.
"""
from __future__ import annotations

import json
import math

from common import ROOT, esc, load, page, save_plan

SLUG = "atomic-coffee"
KIND = {"company": "company", "financial": "financial", "labor": "staffing", "architect": "architects",
        "lawyer": "law firm", "insurance": "insurance", "association": "nonprofit", "ngo": "nonprofit",
        "laboratory": "lab", "bank": "bank", "office": "offices", "newspaper": "newspaper",
        "courthouse": "courthouse", "library": "library", "townhall": "city hall", "yes": "offices"}


def main() -> None:
    sig = load(SLUG, "signals.json")
    lat0, lon0 = sig["google"]["lat"], sig["google"]["lon"]
    els = json.load(open(ROOT / "work" / SLUG / "osm_offices.json"))
    rows = []
    for e in els:
        t = e["tags"]
        if not t.get("name"):
            continue
        la = e.get("lat") or e.get("center", {}).get("lat")
        lo = e.get("lon") or e.get("center", {}).get("lon")
        d = math.hypot((la - lat0) * 111_320, (lo - lon0) * 111_320 * math.cos(math.radians(lat0)))
        addr = " ".join(x for x in [t.get("addr:housenumber"), t.get("addr:street")] if x)
        kind = KIND.get(t.get("office") or t.get("amenity") or t.get("building"), "")
        rows.append((round(d * 1.3 / 80), t["name"], kind, addr))
    rows.sort()
    table = "".join(f"<tr><td>{m} min</td><td><b>{esc(n)}</b><br><span class='meta'>{esc(k)}{' · ' + esc(a) if a else ''}</span></td></tr>"
                    for m, n, k, a in rows)
    body = f"""
<p class="meta">For Atomic Coffee · 222 Broadway N, Fargo</p>
<h1>{len(rows)} workplaces are a short walk from your back room.</h1>
<p class="lede">Your room seats 26 for $25. Law firms, banks, insurers and nonprofits all hold meetings, and all of these are within {max(r[0] for r in rows)} minutes on foot. Here's the list, nearest first, and a flyer to hand them.</p>
<p class="noprint"><a class="btn" href="flyer/">Print the flyer</a></p>
<div class="scroll"><table>{table}</table></div>
<p class="meta">From OpenStreetMap, September 26, 2026. Walking times are estimates.</p>
"""
    flyer = """
<div style="text-align:center;padding-top:.6in">
<p class="sans" style="letter-spacing:.2em;font-size:13px">ATOMIC COFFEE · 222 BROADWAY N</p>
<h1 style="font-size:44px;margin:.2in 0">Need a room for your next meeting?</h1>
<p style="font-size:22px">Up to 26 people. $25 for 2–4 hours.</p>
<p style="font-size:18px">Tables and chairs set up however your meeting needs.<br>Steps away from all the coffee and food your heart desires.</p>
<p style="font-size:16px">Staff meetings · small parties · clubs · study groups</p>
<p style="font-size:30px;margin-top:.4in"><b>Call (701) 478-6160</b></p>
<p class="meta">Mon–Fri 6:30am–9pm · Sat 7am–9pm · Sun 8am–9pm</p>
</div>"""
    strip = "Put together for Atomic Coffee by Brick &amp; Mortar from OpenStreetMap and your own meeting-room page."
    page(SLUG, "Atomic Coffee — offices near your back room", body, strip=strip)
    page(SLUG, "Atomic Coffee — meeting room flyer", flyer, sub="flyer",
         strip='Print (letter). Words from your own meeting-room page. <a href="../">Back</a>',
         css="@page{size:letter;margin:.5in}")
    save_plan(SLUG, {
        "slug": SLUG, "headline": f"{len(rows)} workplaces are within a short walk of your back room. Here's the list and a flyer.",
        "gift_path": f"/{SLUG}/", "print_path": f"/{SLUG}/flyer/",
        "evidence": ["room: 26 people, $25 for 2-4 hours, phone booking (their site)",
                     f"{len(rows)} named offices within 450 m on OpenStreetMap"],
        "to_use_it": "Print the flyer; drop it at the nearest ten.",
        "menu": ["online_booking", "online_ordering", "review_replies_monthly"],
    })
    print("built", SLUG, len(rows))


if __name__ == "__main__":
    main()
