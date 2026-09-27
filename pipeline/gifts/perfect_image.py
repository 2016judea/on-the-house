"""Facials with Rachel / Perfect Image, Maplewood — 506 reviews on GlossGenius, 31 on Google.

Evidence:
  - facialswithrachel.glossgenius.com/about (read 2026-09-26): "(506 Reviews)", Rachel Moen,
    owner of Facials with Rachel and Perfect Image studios.
  - Google listing "Perfect Image" (pulled 2026-05-18): 31 reviews, 4.3 stars. 19 are from
    before 2021 and 7 are about haircuts ("Ask for Jerry"), from when it was a hair shop.
  - Hours disagree. GlossGenius: Tue 3-7, Wed 10:30-7, Thu 12:30-7, Fri 9:30-6, Sat 9:30-4.
    Google: Tue-Fri 11-7, Sat 10-2. One review found the door locked.
Gift: a counter card and an after-visit text with her direct Google review link, so the
clients who already review her on GlossGenius can say the same thing where new clients look.
"""
from __future__ import annotations

from common import esc, page, save_plan

SLUG = "perfect-image"
PLACE_ID = "ChIJd0NlpfbTslIRtDHcD3ifDFc"
REVIEW = f"https://search.google.com/local/writereview?placeid={PLACE_ID}"

TEXT = ("Thank you for coming in today! If you have a minute, a Google review helps new clients find me: "
        f"{REVIEW}  — Rachel")

GG = [("Monday", "Closed"), ("Tuesday", "3 – 7 pm"), ("Wednesday", "10:30 am – 7 pm"), ("Thursday", "12:30 – 7 pm"),
      ("Friday", "9:30 am – 6 pm"), ("Saturday", "9:30 am – 4 pm"), ("Sunday", "Closed")]
GOOGLE = {"Monday": "Closed", "Tuesday": "11 am – 7 pm", "Wednesday": "11 am – 7 pm", "Thursday": "11 am – 7 pm",
          "Friday": "11 am – 7 pm", "Saturday": "10 am – 2 pm", "Sunday": "Closed"}


def qr_svg(data: str) -> str:
    import segno  # pip: segno (pure python)
    return segno.make(data, error="m").svg_inline(scale=5, dark="#1d1b18", light="#ffffff")


def main() -> None:
    qr = qr_svg(REVIEW)
    card = f"""
<div style="text-align:center;padding:.4in;border:2px solid currentColor;border-radius:16px;max-width:5in;margin:.3in auto">
<p class="sans" style="letter-spacing:.2em;font-size:12px">FACIALS WITH RACHEL · PERFECT IMAGE</p>
<h1 style="font-size:32px;margin:.1in 0">Loved your visit?</h1>
<p style="font-size:18px">Scan to leave a Google review.<br>It's how new clients find me.</p>
<div style="margin:.2in auto;width:max-content">{qr}</div>
<p style="font-size:16px">Thank you! — Rachel</p>
</div>"""
    rows = "".join(f"<tr><td>{d}</td><td>{esc(h)}</td><td class='{'bad' if GOOGLE[d] != h.replace(' – ', ' – ') and GOOGLE[d] != h else ''}'>{esc(GOOGLE[d])}</td></tr>" for d, h in GG)
    body = f"""
<p class="meta">For Rachel Moen · Facials with Rachel / Perfect Image · 2645 White Bear Ave #7, Maplewood</p>
<h1>506 people have reviewed you on GlossGenius. Google shows 31.</h1>
<p class="lede">And most of those 31 are from before 2021, when the listing was a hair shop. Seven are about haircuts. So someone searching for a facial in Maplewood sees 4.3 stars and "Ask for Jerry."</p>
<p>Your clients already like writing about you. They just do it in the wrong place. Here are two ways to point them at Google.</p>

<h2>1. A card for your counter</h2>
<p class="noprint"><a class="btn" href="card/">Print the card</a></p>
{card}

<h2>2. A text to send after each visit</h2>
<p>Paste this into GlossGenius as your after-appointment message, or text it yourself:</p>
<div class="card sans" style="word-break:break-word">{esc(TEXT)}</div>
<p class="meta">The link opens the "write a review" box on your Google listing directly.</p>

<h2>Your hours don't match</h2>
<div class="scroll"><table><tr><th></th><th>GlossGenius</th><th>Google</th></tr>{rows}</table></div>
<p>One Google review says the door was locked when they came. Google's hours are probably the old ones.</p>
<p class="meta">GlossGenius read September 26, 2026. Google listing as of May 18, 2026.</p>
"""
    strip = "Put together for Rachel by Brick &amp; Mortar from your GlossGenius page and your public Google listing. Nothing was changed."
    page(SLUG, "Facials with Rachel — Google reviews", body, strip=strip)
    page(SLUG, "Facials with Rachel — review card", card, sub="card",
         strip='Print (letter). <a href="../">Back</a>', css="@page{size:letter;margin:.4in}")
    save_plan(SLUG, {
        "slug": SLUG, "headline": "506 people have reviewed you on GlossGenius. Google shows 31, mostly old haircut reviews. We made a counter card and an after-visit text that send happy clients to your Google page.",
        "gift_path": f"/{SLUG}/", "print_path": f"/{SLUG}/card/",
        "evidence": ["GlossGenius about page: 506 reviews", "Google: 31 reviews, 4.3; 19 before 2021; 7 about haircuts",
                     "hours differ on every open day"],
        "to_use_it": "Print the card; paste the text into GlossGenius's after-visit message.",
        "menu": ["gbp_cleanup", "review_engine", "ai_listings"],
    })
    print("built", SLUG)


if __name__ == "__main__":
    main()
