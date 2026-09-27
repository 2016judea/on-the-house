"""Dunn Bros Coffee on Grand, St Paul — the original store, where the chain's app doesn't work.

Evidence (Google reviews pulled 2026-05-18; site read 2026-09-26):
  - 3 reviews (2015, 2022, 2024) were caught out by the Dunn Bros app/rewards not working
    here: "I learned this the hard way!", "don't plan on using it here".
  - 11 four- and five-star reviews praise it BECAUSE it's the original: "The original and still the best."
  - dunnbrosgrand.com: "The original Dunn Brothers Coffee! Established in 1987."
    "We ship beans all over the US!"
  - Sunday hours disagree: their site says 8am-2pm, Google listed 7am-4pm (May 2026).
The gift: a counter card that turns the surprise into the reason people come, in their words.
"""
from __future__ import annotations

from common import page, save_plan

SLUG = "dunn-brothers-coffee-company"

CARD = """
<div style="text-align:center;padding:.5in .3in;border:3px solid currentColor;border-radius:18px;max-width:6.5in;margin:.3in auto">
<p class="sans" style="letter-spacing:.25em;font-size:13px">1569 GRAND AVE · ST PAUL</p>
<h1 style="font-size:46px;margin:.15in 0">The original Dunn Bros.</h1>
<p style="font-size:22px">Here since 1987. Roasted fresh daily.</p>
<hr style="margin:.3in 1in;border:0;border-top:1px solid #999">
<p style="font-size:19px">We're the first one, and we're our own shop.<br>
So the Dunn Bros app, rewards and chain promotions<br>don't work here. Our menu is our own too.</p>
<p style="font-size:17px;margin-top:.25in">We ship beans all over the US · 651-698-0618</p>
</div>"""


def main() -> None:
    body = f"""
<p class="meta">For Dunn Bros Coffee on Grand · 1569 Grand Ave, St Paul</p>
<h1>Three reviews say the app caught them out. Eleven more love you for being the original.</h1>
<p class="lede">Same fact, two reactions. The difference is whether they knew before they got to the register. So we made a counter card that tells them first, in your own words.</p>
<blockquote>Pro Tip: this is the first Dunn brothers location, because of this, they don't allow you to use the app, redeem rewards, discounts or promotions. I learned this the hard way!</blockquote>
<blockquote>The original and still the best.</blockquote>
<p class="noprint"><a class="btn" href="card/">Print the counter card</a></p>
{CARD}
<h2>One more thing</h2>
<p>Your website says Sunday is <b>8am–2pm</b>. Google listed <b>7am–4pm</b> in May. One of them sends people to a locked door.</p>
<p class="meta">Reviews from Google, as of May 18, 2026. Website read September 26, 2026.</p>
"""
    strip = "Put together for Dunn Bros on Grand by Brick &amp; Mortar from your reviews and your own website."
    page(SLUG, "Dunn Bros on Grand — the original", body, strip=strip)
    page(SLUG, "Dunn Bros on Grand — counter card", CARD, sub="card",
         strip='Print (letter) and fold, or frame it by the register. <a href="../">Back</a>',
         css="@page{size:letter;margin:.4in}")
    save_plan(SLUG, {
        "slug": SLUG, "headline": "Three reviews say the Dunn Bros app caught them out at your register. We made a counter card that tells them first.",
        "gift_path": f"/{SLUG}/", "print_path": f"/{SLUG}/card/",
        "evidence": ["3 reviews 2015/2022/2024 on the app/rewards", "11 four- and five-star reviews praise it as the original",
                     "Sunday 8-2 on site vs 7-4 on Google (May)"],
        "to_use_it": "Print the card for the register.",
        "menu": ["gbp_cleanup", "review_replies_monthly", "online_ordering"],
    })
    print("built", SLUG)


if __name__ == "__main__":
    main()
