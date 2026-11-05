"""Bare MN Skin Care Studio, West St Paul — a Barneys review is sitting on Jillian's Google page.

Evidence (Google review sample pulled 2026-05-18, all 30 of 30 reviews):
  - Every one of the 21 reviews since 2020-10-01 is five stars.
  - The 4.5 comes from 9 reviews older than that, back to 2013, on a Google place that
    evidently belonged to someone else first. One (1 star, 2018-12-10) is plainly about
    Barneys: "ordered a Christmas gift, delivered by FedEx only to never receive my package".
  - Removing that one review: (134 - 1) / 29 = 4.59, which Google shows as 4.6.
We only name the Barneys one for removal; the others are old but not provably someone else's.
"""
from __future__ import annotations

import json

from common import ROOT, esc, page, save_plan

SLUG = "bare-mn-skin-care-studio"


def main() -> None:
    from pathlib import Path
    places = json.load(open(Path.home() / "Desktop/workspace/bricks/data/outscraper_reviews.json"))
    p = next(x for x in places if x["name"].startswith("Bare MN"))
    rs = p["reviews_data"]

    def dt(r):
        m = r["review_datetime_utc"]
        return f"{m[6:10]}-{m[0:2]}-{m[3:5]}"

    post = [r for r in rs if dt(r) >= "2020-10-01"]
    pre = sorted([r for r in rs if dt(r) < "2020-10-01"], key=dt)
    total = sum(r["review_rating"] for r in rs)
    barneys = next(r for r in rs if "Barneys" in (r["review_text"] or ""))
    now = total / len(rs)
    after = (total - barneys["review_rating"]) / (len(rs) - 1)
    assert all(r["review_rating"] == 5 for r in post), "premise broke: a post-2020 review is not 5 stars"

    rows = "".join(
        f'<tr><td>{dt(r)}</td><td>{"★" * r["review_rating"]}</td>'
        f'<td>{esc((r["review_text"] or "(no words)")[:140])}</td></tr>' for r in pre)
    body = f"""
<p class="meta">For Jillian Ledy · Bare MN Skin Care Studio · 1720 Livingston Ave, Studio #19, West St Paul</p>
<h1>One of your Google reviews is about Barneys.</h1>
<p class="lede">It's a 1-star, from December 2018, about a Christmas gift FedEx never delivered. Get it taken down and your rating goes from 4.5 to 4.6.</p>

<div class="card">
<p class="sans"><b>The review</b> · ★ · {dt(barneys)}</p>
<blockquote>{esc(barneys["review_text"])}</blockquote>
<a class="btn" href="{esc(barneys["review_link"])}">Open it on Google</a>
</div>

<h2>How to get it removed (2 minutes)</h2>
<ol class="sans">
<li>Sign in to the Google account that manages Bare's profile.</li>
<li>Open the review with the button above.</li>
<li>Tap the three dots next to it, then <b>Report review</b>.</li>
<li>Pick <b>Off topic</b> ("doesn't talk about an experience at this place").</li>
</ol>
<p class="meta">Google reviews each report itself, so it can take a few days.</p>

<h2>The math</h2>
<div class="scroll"><table>
<tr><td>Reviews since October 2020</td><td>{len(post)}</td><td>all five stars</td></tr>
<tr><td>Reviews from before that</td><td>{len(pre)}</td><td>average {(total - 5 * len(post)) / len(pre):.1f} stars</td></tr>
<tr><td>Your rating now</td><td>{now:.2f}</td><td>Google shows {round(now + 1e-9, 1)}</td></tr>
<tr><td>Without the Barneys review</td><td>{after:.2f}</td><td>Google shows {round(after + 1e-9, 1)}</td></tr>
</table></div>

<h2>Everything older than your first client review</h2>
<p>Your page picked these up before October 2020. We only flagged the one that is plainly about another business.</p>
<div class="scroll"><table>{rows}</table></div>
<p class="meta">From Google's public review list as of May 18, 2026.</p>
"""
    strip = "Put together for Bare MN by Brick &amp; Mortar from your public Google reviews. Nothing was changed on your profile."
    page(SLUG, "Bare MN — the Barneys review", body, strip=strip)
    save_plan(SLUG, {
        "slug": SLUG, "headline": "One of your Google reviews is about Barneys. Removing it takes you from 4.5 to 4.6.",
        "gift_path": f"/{SLUG}/",
        "evidence": [f"{len(post)} of {len(post)} reviews since Oct 2020 are 5 stars",
                     f"Barneys review {dt(barneys)}, 1 star", f"Google shows {round(now + 1e-9, 1)} now; without that review it shows {round(after + 1e-9, 1)}"],
        "to_use_it": "Report the one review as off topic from her Google login.",
        "menu": ["review_replies_monthly", "online_booking", "review_engine"],
    })
    print("built", SLUG, f"{now:.3f} -> {after:.3f}")


if __name__ == "__main__":
    main()
