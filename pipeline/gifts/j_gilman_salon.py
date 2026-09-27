"""J. Gilman Salon, Wichita — their website is down; rebuild it from its own last saved copy.

Evidence (checked 2026-09-26):
  - www.jgilmansalon.com is a CNAME to djwnq9j0xxm30.cloudfront.net, which no longer
    resolves on 8.8.8.8 or 1.1.1.1. The apex 301s to www. So the site is gone for everyone,
    and Google still sends people to it.
  - The Wayback Machine holds the site as of 2026-02-07 (home, about, team, services, 20
    service pages). All copy below is theirs, from that capture.
  - Their online booking page (EnvisionGo) still answers 200. Nothing links to it now.
"""
from __future__ import annotations

import json
import re

from common import ROOT, esc, load, page, save_plan

SLUG = "j-gilman-salon"
BOOK = "https://na02.envisiongo.com/a/jgilmansalon/OnlineBooking.aspx"
NAV = ("Home Services Meet The Owner About About Us Contact Careers Shop Kasilo Hair Products "
       "At-Home Beauty and Gifts Expert Stylists Book Now Shop Online")


def clean(s: str) -> str:
    s = s.replace(NAV, "").strip()
    s = s.replace("&#x27;", "'").replace("&quot;", '"').replace("’", "'")
    return re.sub(r"\s*©.*", "", s)


def main() -> None:
    t = {k: clean(v) for k, v in json.load(open(ROOT / "work" / SLUG / "wayback/text.json")).items()}
    sig = load(SLUG, "signals.json")
    hours = sig["google"]["working_hours"]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def desc(key: str) -> str:
        """The page's own first paragraph after its Book Now button, cut before the sub-service list."""
        m = re.search(r"Book Now (.*?)(?: Related Services| Book Now| Other Stylists|$)", t[key])
        text = m.group(1).strip() if m else ""
        sents = re.findall(r"[^.!?]+[.!?]", text)
        keep = []
        for x in sents:
            if keep and re.match(r"\s*(Women's|Men's|Child's|Hair Extensions|All Over|Balayage|Weave|Brows|Lashes|Facials|Waxing|Perm|Optismooth|4-Ever|Wedding|Dematting|Shampoo|Toner|Additional)\b", x):
                break
            keep.append(x.strip())
        return " ".join(keep)

    def tagline(key: str) -> str:
        """The one-line blurb under a service's name, e.g. 'Refresh your look with ...'."""
        head = t[key].split(" Book Now ")[0]
        m = re.search(r"((?:[A-Z][^.]*?)\.)$", head)
        return m.group(1).strip() if m else ""

    def price(key: str) -> str:
        m = re.search(r"(\$\d+[^A-Z]*?)(?= [A-Z])", t[key].split(" Book Now ")[0])
        return m.group(1).strip() if m else ""

    groups = [
        ("Haircut & Style", "services_haircut-style", ["womens-haircut", "mens-haircut", "childs-haircut", "hair-extensions"]),
        ("Color", "services_color", ["all-over-color", "balayage-color-correction", "weave-highlights"]),
        ("Spa", "services_spa", ["brows", "lashes", "facials", "waxing"]),
        ("Texture", "services_texture-services", ["perm", "optismooth-straightening-treatment", "4-ever-smooth-keratin-treatment"]),
        ("Extras", "services_additional-services", ["wedding", "toner", "shampoo-style", "additional-bowls", "dematting"]),
    ]
    svc = []
    for title, key, subs in groups:
        items = []
        for s in subs:
            k = f"{key}_{s}"
            name = re.sub(r"^Services .*? ", "", t[k].split(" Book Now ")[0])
            nm = t[k].split(" Book Now ")[0]
            label = {"womens-haircut": "Women's Haircut", "mens-haircut": "Men's Haircut", "childs-haircut": "Child's Haircut",
                     "hair-extensions": "Hair Extensions (consultation required)", "all-over-color": "All Over Color",
                     "balayage-color-correction": "Balayage / Color Correction", "weave-highlights": 'Weave "Highlights"',
                     "brows": "Brows", "lashes": "Lashes", "facials": "Facials", "waxing": "Waxing", "perm": "Perm",
                     "optismooth-straightening-treatment": "Optismooth Straightening", "4-ever-smooth-keratin-treatment": "4-Ever Smooth Keratin",
                     "wedding": "Wedding", "toner": "Toner", "shampoo-style": "Shampoo & Style", "additional-bowls": "Additional Bowls",
                     "dematting": "Dematting"}[s]
            p = price(k)
            if s == "dematting":
                p = "hourly, at your haircut rate"
            tl = re.sub(r"^.*?(?=(Transform|Find|J\. Gilman|Enhance|Refresh|Add|Discover|Achieve|Elevate|Reveal|Get|Enjoy|Let|Restore))", "", tagline(k))
            items.append(f'<tr><td>{esc(label)}</td><td class="meta">{esc(p)}</td></tr>')
        svc.append(f'<h3>{esc(title)}</h3><p class="meta">{esc(desc(key).replace("J. Gilman", "J·Gilman").split(". ")[0].replace("J·Gilman", "J. Gilman").rstrip(".") + ".")}</p><div class="scroll"><table>{"".join(items)}</table></div>')

    hrs = "".join(f"<tr><td>{d}</td><td>{esc(', '.join(hours.get(d, ['?'])))}</td></tr>" for d in days)
    justin = t["team_justin"].split("the_dirtbike_hairstylist ", 1)[1].split(" Book Now")[0]
    daisy = t["team_daisy"].split("looks_with.dais ", 1)[1].split(" Book Now")[0]
    body = f"""
<p class="meta">916 East Douglas Avenue · Wichita, KS 67202 · <a href="tel:+13162605203">(316) 260-5203</a></p>
<h1>J. Gilman Salon</h1>
<p class="lede">{esc(t['home'].split('Welcome to J. Gilman Salon ')[1].split(' Discover the J. Gilman')[0])}</p>
<a class="btn" href="{BOOK}">Book now</a>

<h2>Services</h2>
<p>{esc(t['services'].split('Services ',1)[1].split(' Spa Experience')[0].replace(' Stop in or call to schedule an appointment today!',''))}</p>
{''.join(svc)}

<h2>Our stylists</h2>
<div class="card"><h3>Justin — owner</h3><p>{esc(justin)}</p></div>
<div class="card"><h3>Daisy</h3><p>{esc(daisy)}</p></div>

<h2>Hours</h2>
<div class="scroll"><table>{hrs}</table></div>
<p class="meta">Hours as Google listed them in May 2026.</p>

<h2>Find us</h2>
<p>916 East Douglas Avenue, Wichita, KS 67202 — Old Town.<br>
<a href="https://www.openstreetmap.org/search?query=916%20E%20Douglas%20Ave%2C%20Wichita%2C%20KS">Map</a> ·
<a href="tel:+13162605203">(316) 260-5203</a> ·
Instagram <a href="https://www.instagram.com/j.gilman_salon/">@j.gilman_salon</a></p>
<a class="btn" href="{BOOK}">Book now</a>
"""
    strip = ("Rebuilt for J. Gilman Salon by Brick &amp; Mortar from the salon's own website, as last saved on Feb 7, 2026. "
             "jgilmansalon.com stopped loading; this copy is here until it's back.")
    page(SLUG, "J. Gilman Salon — Wichita", body, strip=strip)
    save_plan(SLUG, {
        "slug": SLUG, "headline": "Your website is down. We rebuilt it from your own last saved copy.",
        "gift_path": f"/{SLUG}/",
        "evidence": [
            "www.jgilmansalon.com points at a CloudFront address (djwnq9j0xxm30.cloudfront.net) that no longer exists; it fails on Google and Cloudflare DNS (checked 2026-09-26)",
            "Google still links to it",
            "Rebuilt from the Wayback Machine capture of 2026-02-07: same words, same services, same prices, Justin and Daisy",
            f"Your EnvisionGo booking page still works ({BOOK}); every Book button points at it",
        ],
        "to_use_it": "Share the link today. To put it back on jgilmansalon.com, whoever holds the domain points www at it (5 minutes).",
        "menu": ["domain_hookup", "gbp_cleanup", "review_replies_monthly"],
    })
    print("built", SLUG)


if __name__ == "__main__":
    main()
