"""Build the page for Roshanthi Cantin (Falcon National Bank): which of Falcon's
live SBA borrowers fell out of good standing with the MN Secretary of State
while the loan was outstanding. Every number on the page is computed here.

inputs:  bricks SBA layer (SBA 7(a)/504 FOIA, as of 2026-06-30)
         sos_falcon-national-bank.json (from sos_lookup.py, public SOS search)
output:  index.html, findings.json
"""
import datetime as dt, html, json, pathlib, re

HERE = pathlib.Path(__file__).parent
LENDER = "Falcon National Bank"
LOANS = pathlib.Path.home() / "Desktop/bricks/website/api/_data/twincities_sba_loans.json"
from sos_lookup import norm

layer = json.load(open(LOANS))
loans = [l for l in layer["loans"] if l["lender"] == LENDER and l["status"] in ("EXEMPT", "COMMIT")]
sos = json.load(open(HERE / "sos_falcon-national-bank.json"))
ALIAS = {"plymouth jimsliquor": "plymouth jims liquor", "dae fitness 1 profit sharing plan": "dae fitness 1"}

def d(s):
    m, dd, y = s.split("/"); return dt.date(int(y), int(m), int(dd))

by = {}
for l in loans:
    k = ALIAS.get(norm(l["business"]), norm(l["business"]))
    by.setdefault(k, []).append(l)

lapses, unmatched, checked = [], [], 0
for k, ls in by.items():
    r = sos.get(k)
    if not r or "match" not in r:
        unmatched.append((ls[0], r)); continue
    checked += 1
    first = min(dt.date.fromisoformat(l["approval_date"]) for l in ls)
    h = r["history"]
    for i, e in enumerate(h):
        if not e["event"].startswith("Administrative"):
            continue
        start = d(e["date"])
        if start < first:
            continue
        back = next((d(x["date"]) for x in h[i + 1:] if "Reinstatement" in x["event"]), None)
        lapses.append({
            "borrower": r["match"], "loans": len(ls), "approved": sum(l["approved"] for l in ls),
            "first_approved": first.isoformat(), "city": ls[0]["city"].title(), "trade": ls[0]["trade"],
            "event": e["event"], "lapsed": start.isoformat(), "reinstated": back.isoformat() if back else None,
            "days": (back - start).days if back else None, "sos_url": r["url"],
            "status_now": r["status"], "renewal_due": r["renewal_due"],
            "days_after_approval": (start - first).days,
        })

lapses.sort(key=lambda x: -(x["days"] or 99999))
borrowers_lapsed = sorted({x["borrower"] for x in lapses})
dollars_lapsed = sum({x["borrower"]: x["approved"] for x in lapses}.values())
total_names = len(by)
longest = lapses[0]
soonest = min(lapses, key=lambda x: x["days_after_approval"])

findings = {
    "lender": LENDER, "sba_as_of": layer["as_of"], "checked_on": "2026-09-26",
    "live_loans": len(loans), "borrowers": total_names, "found_on_register": checked,
    "not_found": [u[0]["business"] for u in unmatched],
    "borrowers_lapsed": len(borrowers_lapsed), "approved_dollars_lapsed": dollars_lapsed,
    "lapses": lapses,
}
(HERE / "findings.json").write_text(json.dumps(findings, indent=1))

e = html.escape
money = lambda v: f"${v/1e6:.2f}M" if v >= 1e6 else f"${v/1e3:,.0f}k"
fmt = lambda s: dt.date.fromisoformat(s).strftime("%b %-d, %Y")

rows = "".join(f"""
<li><div class="who">{e(x['borrower'])}</div>
<div class="meta">{e(x['city'])} · {x['loans']} loan{'s' if x['loans']>1 else ''}, {money(x['approved'])} approved {fmt(x['first_approved'])}</div>
<div class="gap"><b>{e(x['event'].replace('Administrative ','Administratively ').replace('Termination','terminated').replace('Dissolution','dissolved'))} {fmt(x['lapsed'])}</b>
{'&rarr; reinstated ' + fmt(x['reinstated']) + f" &middot; <b>{x['days']} days</b> out of good standing" if x['reinstated'] else '&rarr; <b>not reinstated</b>'}</div>
<div class="meta">Next renewal due {e(x['renewal_due'] or 'n/a')}</div>
<a href="{e(x['sos_url'])}">Their filing history at the Secretary of State</a></li>""" for x in lapses)

nf = "".join(f"<li><b>{e(u[0]['business'])}</b> · {e(u[0]['city'].title())} · {money(u[0]['approved'])} approved {fmt(u[0]['approval_date'])}</li>"
             for u in unmatched if "Profit Sharing" not in u[0]["business"])

page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>For Roshanthi Cantin, Falcon National Bank</title>
<meta name="robots" content="noindex">
<style>
:root{{--ink:#1b1b1b;--soft:#5b5b5b;--line:#e4e1da;--bg:#fbfaf7;--mark:#8a2b0f}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 Georgia,"Times New Roman",serif}}
main{{max-width:640px;margin:0 auto;padding:40px 20px 64px}}
.to{{font:13px/1.4 system-ui,sans-serif;color:var(--soft);letter-spacing:.02em}}
h1{{font-size:clamp(25px,6vw,34px);line-height:1.2;margin:14px 0 14px;font-weight:700}}
p{{margin:0 0 14px}}
ol{{list-style:none;padding:0;margin:26px 0}}
li{{border-top:1px solid var(--line);padding:16px 0}}
.who{{font-weight:700}}
.meta{{font:14px/1.45 system-ui,sans-serif;color:var(--soft);margin:2px 0 6px}}
.gap{{margin-bottom:6px}} .gap b{{color:var(--mark)}}
a{{color:var(--ink);font:14px system-ui,sans-serif}}
h2{{font-size:19px;margin:36px 0 8px}}
ul{{padding-left:18px;font-size:15px}}
.small{{font:14px/1.55 system-ui,sans-serif;color:var(--soft)}}
footer{{margin-top:40px;border-top:1px solid var(--line);padding-top:18px}}
</style>
<main>
<div class="to">For Roshanthi Cantin · Falcon National Bank · {fmt(findings['checked_on'])}</div>
<h1>{len(borrowers_lapsed)} of your SBA borrowers lost good standing with the state while they owed Falcon.</h1>
<p>We took every Twin Cities loan the SBA's public file lists under Falcon National Bank and still open &mdash; {len(loans)} loans to {total_names} borrowers &mdash; and looked each borrower up on the Minnesota Secretary of State's register, one at a time.</p>
<p>Every one we found is in good standing today. But {len(borrowers_lapsed)} were administratively dissolved or terminated at some point <i>after</i> Falcon approved their loan, for missing the annual renewal. {e(longest['borrower'])} was out for {longest['days']} days. {e(soonest['borrower'])} lapsed {soonest['days_after_approval']} days after its approval.</p>
<p>{sum(1 for x in {y['borrower']: y for y in lapses}.values() if (x['renewal_due'] or '').endswith('2026'))} of them are due to renew again by December 31 this year. A borrower who missed it once is the one worth a reminder in December.</p>
<ol>{rows}</ol>

<h2>{len([u for u in unmatched if 'Profit Sharing' not in u[0]['business']])} names we could not find on the register</h2>
<p class="small">The SBA file spells the borrower the way the loan was booked. These spellings match no Minnesota entity exactly. Most will be a spelling or an out-of-state entity. One is worth knowing about: the only <i>SJS Enterprises, LLC</i> on the register is now <i>SJS Rentals LLC</i>, which was terminated from 2013 until June 2025 and is registered on Washburn Ave N, not Penn Ave &mdash; so it may not be your borrower at all.</p>
<ul>{nf}</ul>

<h2>How this was done</h2>
<p class="small">Loans: SBA 7(a) and 504 FOIA release, as of {fmt(layer['as_of'])}, cut to the seven metro counties; &ldquo;open&rdquo; means SBA lists it as outstanding or approved-not-yet-disbursed. The SBA publishes the borrower's address, not the project site. Standing: the Secretary of State's public business search, read {fmt(findings['checked_on'])}; a lapse counts only if it started on or after the borrower's first Falcon approval. Nothing here came from Falcon or from any borrower.</p>

<footer class="small">
<p>This one is free, on us. If there's other work you'd like done, just let us know.</p>
<p>A few things we could do next, if useful: run the same check on Falcon's whole SBA book outside the metro ($250) &middot; re-check every borrower each January after the renewal deadline and send you only the ones that slipped ($150 a year) &middot; add UCC and state tax-lien filings against each borrower ($400).</p>
<p>Aidan Jude &middot; aidan@brickandmortar.dev</p>
</footer>
</main>
"""
(HERE / "index.html").write_text(page)
print(json.dumps({k: v for k, v in findings.items() if k != "lapses"}, indent=1))
for x in lapses: print(x["borrower"], x["lapsed"], x["reinstated"], x["days"], x["days_after_approval"])
