"""Polished Nail Spa, Fargo — the website still sends people to the downtown shop that closed.

Evidence (checked 2026-09-26):
  - InForum, 2026-05-19: "Downtown Fargo Polished Nail Spa has closed", techs moved to Osgood.
  - polishednailspa.biz still shows "Downtown 701-365-8112" in the header of every page, a
    DOWNTOWN block with hours on the homepage, and downtown address/phone/hours on Locations
    and Contact Us.
  - The "About Us" menu link opens "Page not found".
  - The Osgood hours disagree with themselves: homepage says M-F 10-7, Contact Us says M-F 10-8.
"""
from __future__ import annotations

from common import esc, page, save_plan

SLUG = "polished-nail-spa"
ARTICLE = "https://www.inforum.com/business/downtown-fargo-polished-nail-spa-has-closed"

FIXES = [
    ("Top of every page (the header)",
     "Osgood 701-281-6494 · Downtown 701-365-8112",
     "701-281-6494 · 4265 45th St S, Suite 129"),
    ("Homepage, the locations section",
     "DOWNTOWN · 102 Broadway, Fargo, ND 58102 · 701.365.8112 · Hours M-F: 10 am – 8 pm, Sat: 10 am – 3 pm, Sun: Closed",
     "Delete this block. Leave OSGOOD as the only location, and add one line under it: \"Our downtown team is here now too.\""),
    ("Locations page",
     "DOWNTOWN · 102 Broadway, Fargo, ND 58102 · 701.365.8112",
     "Delete. Osgood only: 4265 45th Street South, Suite 129, Fargo, ND 58104 · 701.281.6494"),
    ("Contact Us page, first line",
     "We're conveniently located in the Shoppes at Osgood and in Downtown Fargo on Broadway.",
     "We're in the Shoppes at Osgood, 4265 45th St S, Suite 129."),
    ("Contact Us page, second address",
     "Downtown Address: 102 Broadway Fargo, ND 58104 · Phone: 701.365.8112 · Hours M-F 10 a.m. – 8 p.m., Sat 10 a.m. – 3 p.m.",
     "Delete."),
    ("\"About Us\" in the menu",
     "Opens a \"Page not found\" screen (polishednailspa.biz/?page_id=62)",
     "Point it at a real page, or take it out of the menu."),
]


def main() -> None:
    rows = "".join(
        f'<div class="card"><p class="sans"><b>{i}. {esc(where)}</b></p>'
        f'<p class="meta">Now</p><p class="bad">{esc(now)}</p>'
        f'<p class="meta">Change to</p><p class="ok">{esc(new)}</p></div>'
        for i, (where, now, new) in enumerate(FIXES, 1))
    body = f"""
<p class="meta">For Polished Nail Spa · 4265 45th St S, Suite 129, Fargo</p>
<h1>Your website still sends people downtown.</h1>
<p class="lede">The downtown shop closed this spring (<a href="{ARTICLE}">InForum, May 19</a>). But polishednailspa.biz still lists 102 Broadway, its phone and its hours, on every page. Here is every spot, with the new wording written out.</p>
<p>Hand this page to whoever edits the site (the footer says Nubson Design). It's about ten minutes of work.</p>

<h2>Six edits</h2>
{rows}

<h2>One thing only you can answer</h2>
<div class="card">
<p>Your site gives Osgood two different weekday hours:</p>
<ul><li>Homepage: Monday – Friday <b>10 am – 7 pm</b></li><li>Contact Us: Monday – Friday <b>10 am – 8 pm</b></li></ul>
<p>Whichever is right, use it in both places.</p>
</div>
<p class="meta">Checked on polishednailspa.biz on September 26, 2026.</p>
"""
    strip = "Put together for Polished Nail Spa by Brick &amp; Mortar from your public website. Nothing was changed on your site."
    page(SLUG, "Polished Nail Spa — six website edits", body, strip=strip)
    save_plan(SLUG, {
        "slug": SLUG, "headline": "Your website still sends people to the downtown shop that closed.",
        "gift_path": f"/{SLUG}/",
        "evidence": ["downtown shop closed this spring (InForum story, May 19, 2026)", "downtown phone in header of every page, plus homepage, Locations, Contact",
                     "About Us link is a 404", "the site gives Osgood two different weekday closing times (7pm on the homepage, 8pm on Contact Us); only the owner knows which is right"],
        "to_use_it": "Forward the page to whoever edits the site.",
        "menu": ["gbp_cleanup", "ai_listings", "online_booking"],
    })
    print("built", SLUG)


if __name__ == "__main__":
    main()
