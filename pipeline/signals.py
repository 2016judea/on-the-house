"""Step 1: read the live public signals for each business. Costs $0.

For each business with a usable email this records, in work/<slug>/signals.json:
  - google:  the cached listing (hours, phone, site, booking/menu links) and the
             review sample, split into answered / unanswered
  - site:    their own website fetched now: status, phone numbers printed on it,
             whether it carries schema.org LocalBusiness JSON-LD or an llms.txt
  - osm:     whether OpenStreetMap has them within 150 m (Overpass, public)
  - report:  the text of the latest Dropbox Full Report

Nothing here logs into anything or contacts anyone.
"""
from __future__ import annotations

import json
import re
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from inputs import REVIEWS, ROOT, norm

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
PHONE = re.compile(r"\(?\b(\d{3})\)?[\s.\-]?(\d{3})[\s.\-](\d{4})\b")


def fetch(url: str, timeout: int = 20) -> tuple[int, str, str]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            return r.status, r.geturl(), r.read(2_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception as e:  # noqa: BLE001 — a dead site is a finding, not a crash
        return 0, url, f"ERROR {type(e).__name__}: {e}"


def phones(text: str) -> list[str]:
    return sorted({f"({a}) {b}-{c}" for a, b, c in PHONE.findall(text)})


def site_signals(url: str) -> dict:
    status, final, html = fetch(url)
    https_broken = False
    if status == 0:  # one retry, then the other scheme: a broken https is itself a finding
        time.sleep(2)
        status, final, html = fetch(url)
    if status == 0:
        alt = url.replace("https://", "http://") if url.startswith("https://") else url.replace("http://", "https://")
        s2, f2, h2 = fetch(alt)
        if s2:
            https_broken = alt.startswith("http://")
            status, final, html = s2, f2, h2
    ld = re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, re.S | re.I)
    ld_types = sorted(set(re.findall(r'"@type"\s*:\s*"([^"]+)"', " ".join(ld))))
    base = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(final))
    llms_status, _, llms = fetch(base + "/llms.txt", 10)
    text = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I))
    return {
        "url": url, "status": status, "final_url": final,
        "error": html if html.startswith("ERROR") else None,
        "title": (re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I) or [None, ""])[1].strip()[:120],
        "phones": phones(text),
        "jsonld_types": ld_types,
        "has_localbusiness_schema": any(t in ld_types for t in (
            "LocalBusiness", "Restaurant", "CafeOrCoffeeShop", "BeautySalon", "HairSalon", "NailSalon",
            "DaySpa", "Bakery", "Brewery", "FoodEstablishment", "BarOrPub", "HealthAndBeautyBusiness")),
        "has_llms_txt": llms_status == 200 and "<html" not in llms[:500].lower(),
        "text_chars": len(text.split()),
        "https_broken": https_broken,
    }


def osm_signals(lat: float, lon: float, name: str) -> dict:
    q = f'[out:json][timeout:25];nwr(around:150,{lat},{lon})["name"];out tags center;'
    for attempt in range(3):
        try:
            data = urllib.parse.urlencode({"data": q}).encode()
            req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=data, headers={"User-Agent": "on-the-house/0.1"})
            els = json.load(urllib.request.urlopen(req, timeout=40))["elements"]
            break
        except Exception as e:  # noqa: BLE001
            time.sleep(5 * (attempt + 1))
            els, err = None, str(e)
    if els is None:
        return {"checked": False, "error": err}
    key = norm(name)[:8]
    hit = [e for e in els if key and key in norm(e["tags"].get("name", ""))]
    return {"checked": True, "found": bool(hit), "match": hit[0] if hit else None, "nearby_named": len(els)}


def google_signals(p: dict) -> dict:
    rv = p.get("reviews_data") or []
    keep = ("review_id", "author_title", "review_rating", "review_text", "review_datetime_utc", "owner_answer", "review_link")
    rows = [{k: r.get(k) for k in keep} for r in rv]
    return {
        "name": p["name"], "phone": p.get("phone"), "site": p.get("site") or p.get("website"),
        "address": p.get("address"), "lat": p.get("latitude"), "lon": p.get("longitude"),
        "working_hours": p.get("working_hours"), "category": p.get("category"), "subtypes": p.get("subtypes"),
        "rating": p.get("rating"), "reviews": p.get("reviews"), "photos_count": p.get("photos_count"),
        "booking_link": p.get("booking_appointment_link"), "menu_link": p.get("menu_link"),
        "reservation_links": p.get("reservation_links"), "order_links": p.get("order_links"),
        "verified": p.get("verified"), "description": p.get("description"), "about": p.get("about"),
        "reviews_tags": p.get("reviews_tags"), "photo": p.get("photo"), "logo": p.get("logo"),
        "location_link": p.get("location_link"), "reviews_link": p.get("reviews_link"),
        "sample": len(rows),
        "answered": sum(1 for r in rows if r["owner_answer"]),
        "unanswered": [r for r in rows if not r["owner_answer"]],
        "pulled": "2026-05-18",
    }


def main(slugs: list[str]) -> None:
    biz = [b for b in json.load(open(ROOT / "data/businesses.json")) if b["email_ok"] and b["report"] and b["google_id"]]
    if slugs:
        biz = [b for b in biz if b["slug"] in slugs]
    places = {p["google_id"]: p for p in json.load(open(REVIEWS))}
    for b in biz:
        out = ROOT / "work" / b["slug"]
        out.mkdir(parents=True, exist_ok=True)
        g = google_signals(places[b["google_id"]])
        report = subprocess.run(["pdftotext", "-layout", b["report"], "-"], capture_output=True, text=True).stdout
        sig = {"business": b, "google": g, "site": site_signals(b["website"]),
               "osm": osm_signals(g["lat"], g["lon"], b["name"]), "report_text": report}
        json.dump(sig, open(out / "signals.json", "w"), indent=1, default=str)
        s = sig["site"]
        print(f'{b["slug"]:36} site={s["status"]} schema={s["has_localbusiness_schema"]} llms={s["has_llms_txt"]} '
              f'osm={sig["osm"].get("found")} unans={len(g["unanswered"])}/{g["sample"]} '
              f'gphone={g["phone"]} sitephones={s["phones"][:3]}')
        time.sleep(1)


if __name__ == "__main__":
    main(sys.argv[1:])
