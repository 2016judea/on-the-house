"""Step 0: who we could do free work for.

Joins three read-only sources into data/businesses.json:
  - the report corpus in Dropbox (highest v<N> per business)
  - bricks/data/mail_list_with_emails.csv (the only place an email lives)
  - bricks/data/outscraper_reviews.json (the Google listing + review sample, pulled 2026-05-18)

An email is only kept if it looks like a mailbox the owner reads: not a scraped
image filename, not a placeholder, and either on the business's own domain or a
free-mail address. A web agency's or franchisor's address is dropped — writing to
the person who built their site is not writing to them.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
BRICKS = Path.home() / "Desktop/bricks"
REPORTS = Path.home() / "Dropbox/AI Consulting/prospects/B&M"
MAIL_LIST = BRICKS / "data/mail_list_with_emails.csv"
REVIEWS = BRICKS / "data/outscraper_reviews.json"

FREE_MAIL = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "aol.com", "msn.com"}
PLACEHOLDER = re.compile(r"(your@|name@|@email\.com|@example\.|\.(png|jpe?g|gif|webp|svg)$|@2x)", re.I)
# Hand-checked 2026-09-26: an address that belongs to someone other than the business.
NOT_THE_OWNER = {
    "corey@nicollet.icebergweb.dev": "their web developer",
    "sebastian@aldusleaf.org": "their web developer",
    "corporate@solasalons.com": "the Sola franchisor, not Anna",
}


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("'", "")).strip("-")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def domain(url: str) -> str:
    host = urlparse(url if "://" in url else "http://" + url).netloc.lower()
    return host.removeprefix("www.")


def email_ok(email: str, website: str) -> tuple[bool, str]:
    e = email.strip().lower()
    if not e or "@" not in e:
        return False, "no email"
    if PLACEHOLDER.search(e):
        return False, "scraped placeholder"
    if e in NOT_THE_OWNER:
        return False, NOT_THE_OWNER[e]
    d = e.split("@", 1)[1]
    if d in FREE_MAIL:
        return True, "free-mail"
    site = domain(website)
    if site and (d == site or site.endswith("." + d) or d.endswith("." + site)):
        return True, "own domain"
    return True, "other domain (check)"


def latest_report(folder: Path) -> Path | None:
    vs = sorted((p for p in folder.glob("v*") if p.name[1:].isdigit()), key=lambda p: int(p.name[1:]))
    for v in reversed(vs):
        for pdf in v.glob("*Full Report.pdf"):
            if pdf.stat().st_size > 0:  # Dropbox placeholders report 0 bytes
                return pdf
    return None


def main() -> None:
    reports = {norm(p.name): p for p in REPORTS.iterdir() if p.is_dir() and p.name not in {"B2B", "Corporate Sales"}}
    places = {}
    for p in json.load(open(REVIEWS)):
        places.setdefault(norm(p["name"]), []).append(p)

    out, seen = [], set()
    for row in csv.DictReader(open(MAIL_LIST)):
        name = row["Business Name"].strip()
        ok, why = email_ok(row["Email"], row["Website"])
        folder = reports.get(norm(name))
        report = latest_report(folder) if folder else None
        # Two GENT rows share one email; the review count picks the right Google listing.
        cands = places.get(norm(name), [])
        place = min(cands, key=lambda p: abs((p.get("reviews") or 0) - int(row["Reviews"] or 0))) if cands else None
        key = (norm(name), row["Email"].strip().lower())
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "slug": slugify(name),
            "name": name,
            "address": f'{row["Street Address"]}, {row["City"]}, {row["State"]} {row["ZIP"]}',
            "phone": row["Phone"],
            "sector": row["Sector"],
            "rating": float(row["Rating"] or 0),
            "reviews": int(row["Reviews"] or 0),
            "website": row["Website"],
            "email": row["Email"].strip(),
            "email_ok": ok,
            "email_why": why,
            "report": str(report) if report else None,
            "google_id": place["google_id"] if place else None,
        })
    (ROOT / "data").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "data/businesses.json", "w"), indent=1)
    usable = [b for b in out if b["email_ok"] and b["report"] and b["google_id"]]
    print(f"{len(out)} rows, {sum(b['email_ok'] for b in out)} usable emails, "
          f"{sum(bool(b['report']) for b in out)} with a Dropbox report, {len(usable)} with all three")
    for b in usable:
        print(f"  {b['slug']:40} {b['email']:34} {b['email_why']}")


if __name__ == "__main__":
    sys.exit(main())
