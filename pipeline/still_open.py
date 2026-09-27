"""Gate before any work: is the business still trading?

The Google listing cache is from 2026-05-18. By 2026-09-26 two of the first ten
picks had closed for good (Downtowner Woodfire Grill 5/17, Third Drop Coffee 4/30)
and both still looked alive in the cache. Writing "we fixed your listing" to a
closed business is the worst email this pipeline can send, so an agent with web
search checks every one first and the pipeline skips anything not clearly open.

Writes work/<slug>/open.json.
"""
from __future__ import annotations

import json
import sys

from inputs import ROOT
from llm import ask_json

PROMPT = """Is this small business still open and operating today (September 2026)?

{name}, {address}. Phone {phone}. Website {website}.

Search the web. Look specifically for news of a closure, sale, move or rename in 2025-2026
(local news, Yelp "CLOSED", Facebook posts). Recent reviews, posts or a working booking page
count as evidence it is open.

JSON shape: {{"status": "open" | "closed" | "moved" | "unclear", "evidence": "<one sentence>",
"source_url": "<best url>", "current_website": "<their working website if you found one, else null>"}}"""


def main(slugs: list[str]) -> None:
    biz = {b["slug"]: b for b in json.load(open(ROOT / "data/businesses.json"))}
    for slug in slugs:
        b = biz[slug]
        out = ROOT / "work" / slug / "open.json"
        if out.exists():
            print(slug, json.load(open(out))["status"], "(cached)")
            continue
        res = ask_json(PROMPT.format(**b), web=True)
        res["checked"] = "2026-09-26"
        json.dump(res, open(out, "w"), indent=1)
        print(f'{slug:36} {res["status"]:8} {res["evidence"][:110]}')


if __name__ == "__main__":
    main(sys.argv[1:])
