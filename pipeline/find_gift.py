"""Step 2 (agent): find the ONE thing worth doing for THIS owner.

Aidan, 2026-09-26: "it has to be specific TO THAT PERSON, otherwise it feels like a
product and people immediately turn their brain off when being sold to. WE DID
SOMETHING FOR THEM." So this step does not pick from a menu of generic deliverables.
An agent reads every review we hold, the report, and the live-site facts, and names
the one problem that is theirs alone — the thing their customers keep saying — and a
fix we can build and hand over with no login and no contact with anyone.

The test the agent applies: if the gift still makes sense after swapping in another
business's name, it fails.

Writes work/<slug>/gift_candidates.json. A human-grade pick is then made into
work/<slug>/plan.json by build steps.
"""
from __future__ import annotations

import json
import sys

from inputs import ROOT
from llm import ask_json

PROMPT = """You are finding a free favor to do for one small-business owner. Not a product. A favor.

Business: {name} — {address} — {sector}. Google {rating} stars, {reviews} reviews.
Their website right now: {site_status}.
OpenStreetMap: {osm}.

Below are {n} Google reviews (star rating, date, text; "OWNER REPLIED" if they answered).
Then the research report we wrote about them in May 2026.

Your job:
1. Find the specific, recurring problems customers name about THIS place (count them; quote them).
   Also unmet requests ("I wish they had...", "couldn't find...", "hours were wrong", "no parking info").
2. For the top 3, propose a fix WE can build today and hand over, under these hard rules:
   - no login to any of their accounts, no contacting anyone, no spending money
   - the deliverable is a real thing at a URL or in a file they can use today
     (a page, a printable sign, a one-screen guide, a menu, a status page, a rebuilt site, a list)
   - it must be about THEIR problem: if it would still make sense after swapping in another
     business's name, reject it
   - generic review replies, generic schema code, generic "SEO" do NOT count
3. Say what public input the build needs (their menu page, their hours, a map, a city dataset...)
   and whether that input is actually reachable.

JSON shape:
{{"complaints": [{{"theme": "...", "count": N, "quotes": ["...", "..."], "latest": "YYYY-MM"}}],
  "gifts": [{{"title": "<what we built, in the owner's words, <=12 words>",
             "for_complaint": "...", "deliverable": "...", "inputs_needed": "...",
             "buildable_without_access": true, "why_they_stop_and_read": "..."}}],
  "best": 0}}

REVIEWS:
{reviews_block}

REPORT (May 2026):
{report}
"""


def reviews_block(g: dict, all_reviews: list[dict]) -> str:
    rows = []
    for r in all_reviews:
        t = (r.get("review_text") or "").strip().replace("\n", " ")
        if not t:
            continue
        rows.append(f'[{r.get("review_rating")}★ {(r.get("review_datetime_utc") or "")[:10]}'
                    f'{" OWNER REPLIED" if r.get("owner_answer") else ""}] {t[:600]}')
    return "\n".join(rows)


def main(slugs: list[str]) -> None:
    from inputs import REVIEWS
    places = {p["google_id"]: p for p in json.load(open(REVIEWS))}
    for slug in slugs:
        out = ROOT / "work" / slug / "gift_candidates.json"
        if out.exists():
            print(slug, "(cached)")
            continue
        sig = json.load(open(ROOT / "work" / slug / "signals.json"))
        b, g, s, o = sig["business"], sig["google"], sig["site"], sig["osm"]
        allrev = places[b["google_id"]].get("reviews_data") or []
        site_status = (f'{s["status"]} {s["final_url"]} "{s["title"]}"' if s["status"] else f'DOES NOT LOAD: {s["error"]}')
        prompt = PROMPT.format(
            name=b["name"], address=sig["google"]["address"], sector=b["sector"], rating=g["rating"],
            reviews=g["reviews"], site_status=site_status,
            osm=json.dumps((o.get("match") or {}).get("tags")) if o.get("found") else "not listed",
            n=len(allrev), reviews_block=reviews_block(g, allrev), report=sig["report_text"][:18000])
        res = ask_json(prompt, timeout=900)
        json.dump(res, open(out, "w"), indent=1)
        best = res["gifts"][res.get("best", 0)]
        print(f'{slug:32} {best["title"]}')


if __name__ == "__main__":
    main(sys.argv[1:])
