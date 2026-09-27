"""Day By Day Cafe, St Paul — the new website's title says "Demo", and search shows it.

Evidence (checked 2026-09-26):
  - Every page of daybydaymn.com (Zingmyorder site, images uploaded 2026-08-18) carries
    <title>Day By Day Cafe - Demo477 7th Street West, Saint Paul, MN, USAAmerican Restaurant</title>
    and meta description "American Restaurant".
  - A web search for the cafe returns that exact line as the result's headline, and the
    search assistant's summary said: "The website appears to be a demonstration site
    (indicated by "Demo" in the title)".
  - The home page still says "We are abiding by all recommendations for the prevention of COVID!"
  - OpenStreetMap has phone +1 651 227 0654 and Mo-Sa 06:00-15:00; their own site says
    651-998-8804 and 7am-3pm daily.
"""
from __future__ import annotations

from common import esc, page, save_plan

SLUG = "day-by-day-cafe"
NOW_TITLE = "Day By Day Cafe - Demo477 7th Street West, Saint Paul, MN, USAAmerican Restaurant"
NEW_TITLE = "Day By Day Cafe — Scratch breakfast on West 7th, St Paul"
NEW_DESC = ("Scratch-kitchen breakfast and a big outdoor patio with a koi pond. "
            "On West 7th since 1980. Open every day, 7am to 3pm. 477 7th Street West, Saint Paul.")

CSS = """
.serp{font-family:arial,sans-serif;background:#fff;color:#202124;border:1px solid #dadce0;border-radius:10px;padding:.9rem 1rem;margin:.6rem 0}
.serp .u{font-size:13px;color:#4d5156}.serp .t{font-size:19px;color:#1a0dab;margin:.2rem 0;line-height:1.3}.serp .d{font-size:14px;color:#4d5156}
.copy{font:15px ui-monospace,Menlo,monospace;background:var(--card);border:1px dashed var(--line);padding:.6rem .7rem;border-radius:8px;word-break:break-word}
"""


def serp(title: str, desc: str) -> str:
    return f'<div class="serp"><div class="u">daybydaymn.com</div><div class="t">{esc(title)}</div><div class="d">{esc(desc)}</div></div>'


def main() -> None:
    body = f"""
<p class="meta">For Day By Day Cafe · 477 7th Street West, Saint Paul</p>
<h1>Your new website is still named "Demo."</h1>
<p class="lede">It's the name on every page, so it's the headline people see when they search for you.</p>

<h2>What a search shows today</h2>
{serp(NOW_TITLE, "American Restaurant")}
<p>We asked an AI search assistant about the cafe. It read that line and said: <q>The website appears to be a demonstration site (indicated by "Demo" in the title).</q></p>

<h2>What it should show</h2>
{serp(NEW_TITLE, NEW_DESC)}

<h2>The fix: two boxes in your website settings</h2>
<p>Your site runs on Zingmyorder. In its website settings (or ask their support to do it), paste these in:</p>
<p class="meta">Site title</p><div class="copy">{esc(NEW_TITLE)}</div>
<p class="meta">Description</p><div class="copy">{esc(NEW_DESC)}</div>
<p class="meta">Every word of the description comes from your own About page and Contact page.</p>

<h2>Two smaller things while you're in there</h2>
<ul>
<li>The home page still says <q>We are abiding by all recommendations for the prevention of COVID!</q> You can delete that line.</li>
<li>OpenStreetMap, the free map many apps read, lists your phone as <b>651-227-0654</b> and your hours as <b>6am–3pm, Monday to Saturday</b>. Your site says 651-998-8804, 7am–3pm every day. Whichever is right, fix the other one (openstreetmap.org, free account, "Edit").</li>
</ul>
<p class="meta">Checked on daybydaymn.com on September 26, 2026.</p>
"""
    strip = "Put together for Day By Day Cafe by Brick &amp; Mortar from your public website and search results. Nothing was changed."
    page(SLUG, "Day By Day Cafe — the Demo title", body, strip=strip, css=CSS)
    save_plan(SLUG, {
        "slug": SLUG, "headline": "Your new website is still named \"Demo\", and that's what search shows.",
        "gift_path": f"/{SLUG}/",
        "evidence": [f"<title> on every page: {NOW_TITLE}", "web search result headline is that line; the assistant summary called it a demonstration site",
                     "COVID line on home page", "OSM phone 651-227-0654 and 6am Mo-Sa vs site 651-998-8804, 7-3 daily"],
        "to_use_it": "Paste two lines into the Zingmyorder website settings.",
        "menu": ["review_replies_monthly", "gbp_cleanup", "ai_listings"],
    })
    print("built", SLUG)


if __name__ == "__main__":
    main()
