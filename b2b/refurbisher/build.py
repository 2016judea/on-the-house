"""Page for T&R Electric (Colman, SD): buyers who are waiting on a transformer right
now, and Minnesota plants that are closing. Rows are chosen by id below; every field
on the page is read from the source file, never typed.

sources:
  open_bids.json / sam_hits.json  SAM.gov public opportunity files (keyless bulk CSVs,
                                  pulled 2026-09-26) via open_bids.py and sam_scan.py
  records.jsonl                   ~/Desktop/the-google-of-obsolete-infrastructure-parts
                                  (council and board agenda items, sole-source)
  twincities_layoff_notices.json  bricks, MN DEED WARN notices (site addresses read off
                                  each notice PDF where the layer had none; see WARN_SITE)
"""
import html, json, pathlib, datetime as dt

HERE = pathlib.Path(__file__).parent
OB = {x["id"]: x for x in json.load(open(HERE / "open_bids.json"))}
SH = {x["id"]: x for x in json.load(open(HERE / "sam_hits.json"))}
IDX = {}
for l in open(pathlib.Path.home() / "Desktop/the-google-of-obsolete-infrastructure-parts/data/records.jsonl"):
    r = json.loads(l); IDX[r["id"]] = r
WARN = json.load(open(pathlib.Path.home() / "Desktop/bricks/website/api/_data/twincities_layoff_notices.json"))["rows"]

OPEN = ["fbfe9a5988f74472bfe1b60bdf813908", "5c1f340589964e4fbdbd52627389ea26"]         # due this week
NEXT = ["1e0e535d26ff42f6b0ea2359cecfeaf7", "84be6fa7cb0f42419dcfa75c4a76abc4", "aff7868ee48c4dd2a925b3b554bc15c4"]
AGENDA = ["civicclerk-independencemo-11398-0"]
WAIT = "7645156c61f9444ab2a05e35c744a217"                                                # WAPA: ordered 2023, delivery 2027
# The layer carries no site for these two; the address is the one printed in the notice PDF itself.
WARN_SITE = {"Pearson's Candy Company": "2140 7th St W, St Paul, MN 55116",
             "MTD Acquisition's Inc.": "1 SW 7th Street, Chisholm, and 3219 19th Avenue E, Hibbing"}
WARN_KEEP = ["Pearson's Candy Company", "Acuity Brands Lighting, Inc.", "MTD Acquisition's Inc.", "Building Materials Manufacturing, LLC (GAF)"]

e = html.escape
fmt = lambda s: dt.date.fromisoformat(s[:10]).strftime("%b %-d, %Y") if s else ""

def sam(x, note):
    return f"""<li><div class="who">{e(x['title'])}</div>
<div class="meta">{e(x['subtier'].title())} · {e(x.get('office',''))}{' · ' + e(x['pop']) if x.get('pop') else ''}</div>
<div class="gap">{note}</div>
<div class="meta">{e(x.get('type',''))}{' · ' + e(x['setaside']) if x.get('setaside') else ''} · contact {e(x.get('contact') or '')} {e(x.get('email') or x.get('contact_email') or '')}</div>
<a href="{e(x['link'])}">The notice on SAM.gov</a></li>"""

rows_open = []
a = OB[OPEN[0]]; rows_open.append(sam(a, f"<b>Solicitation for one 1000 kVA transformer. Quotes due {fmt(a['due'])}.</b>"))
b = OB[OPEN[1]]; rows_open.append(sam(b, f"<b>Construction job that includes one 250 kVA pad-mount, 22.9 kV to 480Y/277V. Bids due {fmt(b['due'])}.</b> The contractor who wins it needs the unit."))
rows_next = []
g = SH[NEXT[0]]; rows_next.append(sam(g, "Three new station-service transformers to furnish and install, two of them 3.75/4.687 MVA step-down. Sources sought closed " + fmt(g['deadline']) + "; the solicitation comes next."))
f = SH[NEXT[1]]; rows_next.append(sam(f, "An IDIQ for 161 kV transformers. The RFI closed " + fmt(f['deadline']) + "; the contract comes next."))
r = SH[NEXT[2]]; rows_next.append(sam(r, "A redundant 69 kV power system. The Army asked bidders how they will source &ldquo;critical, long-lead high-voltage equipment (e.g., main power transformers, 69-kV circuit breakers).&rdquo;"))
i = IDX[AGENDA[0]]
agenda = f"""<li><div class="who">{e(i['agency'])}, {e(i['state'])} &mdash; ${i['price_usd']:,.0f} of {e(i['part'])}</div>
<div class="meta">Council action {fmt(i['date'])} · bought from {e(i['sole_source_vendor'])}</div>
<div class="gap">Their reason, verbatim: <i>&ldquo;{e(i['reason'])}&rdquo;</i></div>
<a href="{e(i['legistar_url'])}">The council item</a></li>"""
w = SH[WAIT]
wait_line = "WAPA ordered the new KV1A transformer in 2023 and expects delivery in 2027"
assert wait_line in w["excerpt"], "the WAPA sentence must be in the notice text"
sellers = []
for name in WARN_KEEP:
    x = max((r for r in WARN if r["employer"] == name), key=lambda r: r["notice_date"])
    site = WARN_SITE.get(name) or ", ".join(v for v in (x.get("site_address"), x.get("site_city")) if v)
    eff = f" · effective {fmt(x['effective_date'])}" if x.get("effective_date") else ""
    extra = f" · {x['footprint_sqft']:,} sq ft footprint, assessed ${x['assessed']:,}" if x.get("footprint_sqft") and x.get("assessed") else ""
    sellers.append(f"""<li><div class="who">{e(name.replace(" (GAF)", "").replace("MTD Acquisition's Inc.", "MTD Acquisition (Walter Surface Technologies)"))}</div>
<div class="meta">{e(site)}</div><div class="gap">Permanent closure, WARN notice {fmt(x['notice_date'])}{eff}{extra}</div>
<a href="{e(x['notice_url'])}">The notice</a></li>""")

page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>For T&amp;R Electric</title>
<meta name="robots" content="noindex">
<style>
:root{{--ink:#1b1b1b;--soft:#5b5b5b;--line:#e4e1da;--bg:#fbfaf7;--mark:#8a2b0f}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 Georgia,"Times New Roman",serif}}
main{{max-width:640px;margin:0 auto;padding:40px 20px 64px}}
.to{{font:13px/1.4 system-ui,sans-serif;color:var(--soft)}}
h1{{font-size:clamp(25px,6vw,34px);line-height:1.2;margin:14px 0}}
h2{{font-size:20px;margin:38px 0 6px}}
p{{margin:0 0 14px}}
ol{{list-style:none;padding:0;margin:14px 0}}
li{{border-top:1px solid var(--line);padding:14px 0}}
.who{{font-weight:700}} .meta{{font:14px/1.45 system-ui,sans-serif;color:var(--soft);margin-top:3px}}
.gap{{margin:5px 0}} .gap b{{color:var(--mark)}}
a{{color:var(--ink);font:14px system-ui,sans-serif}}
.small{{font:14px/1.55 system-ui,sans-serif;color:var(--soft)}}
footer{{margin-top:40px;border-top:1px solid var(--line);padding-top:18px}}
</style>
<main>
<div class="to">For T&amp;R Electric · Surplus and sales · {fmt('2026-09-26')}</div>
<h1>A Missouri city spent ${i['price_usd']:,.0f} on transformers from the one supplier it could find on time.</h1>
<p>In June, Independence Power &amp; Light bought pole-mount and pad-mount transformers sole-source, because it could not find a second American supplier who would meet its schedule. Your site says T&amp;R supplies &ldquo;municipalities, REA's, investor-owned utilities&rdquo; and competes on &ldquo;inventory, quick delivery.&rdquo; A municipal utility that could not find quick delivery is exactly who you sell to.</p>
<p>So we went looking for the others. Below: two federal buyers with quotes due this week, three more whose contracts come next, and four Minnesota plants that filed to close this year &mdash; each with the record it came from.</p>
<ol>{agenda}</ol>
<h2>Due this week</h2>
<ol>{''.join(rows_open)}</ol>
<h2>Coming next</h2>
<ol>{''.join(rows_next)}</ol>
<p class="small">For the wait on new: {e(w['subtier'].title())} wrote, in its Weld Substation notice, &ldquo;{wait_line}.&rdquo;</p>
<h2>For Investment Recovery: Minnesota plants closing</h2>
<p class="small">These are the sellers. A closing plant usually still has its service gear standing; the notice does not say what is inside, and the plant manager does.</p>
<ol>{''.join(sellers)}</ol>
<h2>How this was done</h2>
<p class="small">Federal notices: SAM.gov's public opportunity files, the active file and the FY2026 archive, read {fmt('2026-09-26')}, searched for transformer supply, repair and rebuild work. T&amp;R's own words: the Internet Archive's copy of t-r.com from December 3, 2023, since the live site turns away scripts. Council items: our index of public-agency sole-source purchases, built from agenda packets. Closures: Minnesota DEED's WARN notices; where the list names no site, the address is the one printed on the notice. Nothing here is paid data.</p>
<footer class="small">
<p>This one is free, on us. If there's other work you'd like done, just let us know.</p>
<p>A few things we could do next, if useful: this same list every Monday, federal and council buyers plus Minnesota and South Dakota closures ($150 a month) &middot; the same search run across every state you ship to ($400 a month) &middot; a one-time pull of every public agency that bought a transformer sole-source since 2024, with what it paid and why ($500).</p>
<p>Aidan Jude &middot; aidan@brickandmortar.dev</p>
</footer>
</main>
"""
(HERE / "index.html").write_text(page)
print("buyers open", len(OPEN), "next", len(NEXT), "sellers", len(sellers))
