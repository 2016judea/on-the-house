"""Step 2: decide what free work we can do, with NO login and NO contact.

Rules, and why each is free:
  site     their site is dead, broken on https, or nearly empty  -> we build and host a one-page site.
           Free because it lives on our hosting; pointing their domain at it needs their login (menu).
  replies  Google reviews with no owner answer                   -> ready-to-paste replies.
           Free because posting is theirs; we only write.
  listing  their phone / website / hours disagree between Google, their own site and OpenStreetMap
           -> a one-screen fix sheet.
  schema   their site has no schema.org LocalBusiness block      -> a drop-in file (and it is on our page).
  llms     their site has no /llms.txt                           -> a drop-in file.
  ai       what Claude (web search on) names for the obvious local query.

Writes work/<slug>/plan.json.
"""
from __future__ import annotations

import json
import re
import sys

from inputs import ROOT, norm

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def digits(p: str | None) -> str:
    d = re.sub(r"\D", "", p or "")
    return d[-10:]


def host(u: str | None) -> str:
    return re.sub(r"^(https?://)?(www\.)?", "", (u or "").lower()).split("/")[0]


def pick_reviews(unanswered: list[dict], n_low: int = 4, n_high: int = 2) -> list[dict]:
    """The reviews an owner most needs answered: recent, unhappy, with words in them."""
    def when(r):
        m = re.match(r"(\d\d)/(\d\d)/(\d{4})", r["review_datetime_utc"] or "")
        return f"{m[3]}-{m[1]}-{m[2]}" if m else ""
    has_text = [dict(r, date=when(r)) for r in unanswered if (r.get("review_text") or "").strip()]
    has_text.sort(key=lambda r: r["date"], reverse=True)
    low = [r for r in has_text if (r["review_rating"] or 5) <= 3 and r["date"] >= "2024-01-01"][:n_low]
    high = [r for r in has_text if (r["review_rating"] or 0) == 5 and len(r["review_text"]) > 60][:n_high]
    return low + high


def to24(t: str) -> str:
    m = re.match(r"(\d{1,2})(?::(\d\d))?\s*(AM|PM)", t.strip(), re.I)
    if not m:
        return t
    h = int(m[1]) % 12 + (12 if m[3].upper() == "PM" else 0)
    return f"{h:02d}:{m[2] or '00'}"


def google_hours(wh: dict) -> dict:
    out = {}
    for d in DAYS:
        v = (wh.get(d) or ["?"])[0]
        out[d[:2]] = "closed" if v.lower().startswith("closed") else (
            "-".join(to24(x) for x in re.split(r"[\-\u2013]", v)) if "-" in v or "\u2013" in v else v)
    return out


def osm_hours(oh: str) -> dict | None:
    """Only the simple 'Mo-Sa 06:00-15:00; Su 07:00-15:00' shape; anything fancier returns None."""
    ab = [d[:2] for d in DAYS]
    out = {d: "closed" for d in ab}
    for part in oh.split(";"):
        m = re.fullmatch(r"\s*([A-Za-z,\-]+)\s+(\d\d:\d\d-\d\d:\d\d|off|closed)\s*", part)
        if not m:
            return None
        days = []
        for rng in m[1].split(","):
            a, _, b = rng.partition("-")
            if a not in ab or (b and b not in ab):
                return None
            i, j = ab.index(a), ab.index(b or a)
            days += ab[i:j + 1]
        for d in days:
            out[d] = "closed" if m[2] in ("off", "closed") else m[2]
    return out


def listing_issues(sig: dict) -> list[dict]:
    g, s, o = sig["google"], sig["site"], sig["osm"]
    tags = (o.get("match") or {}).get("tags", {})
    out = []
    gp = digits(g["phone"])
    sp = [digits(p) for p in s["phones"]]
    if sp and gp not in sp:
        out.append({"field": "phone", "google": g["phone"], "your site": ", ".join(s["phones"])})
    op = digits(tags.get("phone") or tags.get("contact:phone"))
    if op and op != gp:
        out.append({"field": "phone", "google": g["phone"], "openstreetmap": tags.get("phone") or tags.get("contact:phone")})
    ow = tags.get("website") or tags.get("contact:website")
    if ow and host(ow) != host(g["site"]):
        out.append({"field": "website", "google": g["site"], "openstreetmap": ow})
    if s["status"] == 0 or s["status"] >= 400:
        out.append({"field": "website", "google": g["site"], "reality": "does not load (checked 2026-09-26)"})
    elif s.get("https_broken"):
        out.append({"field": "website", "google": g["site"], "reality": "the secure (https) version fails to load; only plain http works (checked 2026-09-26)"})
    if not g["working_hours"]:
        out.append({"field": "hours", "google": "no hours listed", "fix": "add your hours so Google can show 'Open now'"})
    oh = tags.get("opening_hours")
    if oh and g["working_hours"]:
        gh, osh = google_hours(g["working_hours"]), osm_hours(oh)
        diff = [d for d in gh if osh is not None and gh[d] != osh[d]]
        if diff:
            out.append({"field": "hours", "days": ", ".join(diff),
                        "google": "; ".join(f"{d} {gh[d]}" for d in diff),
                        "openstreetmap": "; ".join(f"{d} {osh[d]}" for d in diff)})
    if o.get("checked") and not o.get("found"):
        out.append({"field": "map listing", "openstreetmap": "missing", "fix": "not on OpenStreetMap, the free map many apps and AI tools read"})
    return out


def plan(sig: dict) -> dict:
    b, g, s = sig["business"], sig["google"], sig["site"]
    dead = s["status"] == 0 or s["status"] >= 400
    work = []
    if dead or s.get("https_broken") or s["text_chars"] < 100:
        work.append("site")
    reviews = pick_reviews(g["unanswered"])
    if reviews:
        work.append("replies")
    issues = listing_issues(sig)
    if issues:
        work.append("listing")
    if not s["has_localbusiness_schema"]:
        work.append("schema")
    if not s["has_llms_txt"]:
        work.append("llms")
    work.append("ai")
    headline = ("site_dead" if dead else "site_broken" if s.get("https_broken") else
                "site" if "site" in work else "replies")
    return {
        "slug": b["slug"], "name": b["name"], "sector": b["sector"], "work": work, "headline": headline,
        "reviews_to_answer": reviews, "listing_issues": issues,
        "unanswered_total": len(g["unanswered"]), "sample": g["sample"],
        "low_unanswered_since_2024": sum(1 for r in pick_reviews(g["unanswered"], 999, 0)),
    }


def main(slugs: list[str]) -> None:
    for slug in slugs:
        sig = json.load(open(ROOT / "work" / slug / "signals.json"))
        p = plan(sig)
        json.dump(p, open(ROOT / "work" / slug / "plan.json", "w"), indent=1)
        print(f'{slug:32} {p["headline"]:12} {",".join(p["work"]):40} replies={len(p["reviews_to_answer"])} issues={len(p["listing_issues"])}')


if __name__ == "__main__":
    main(sys.argv[1:])
