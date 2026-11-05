"""Page for Anthony M Bauer, CMA, Analytics and Assessment Division Manager,
Hennepin County Assessor — built only on the parcels HIS office values (the
county roll minus the seven cities that self-assess commercial property, and
minus Maple Grove, which self-assessed in 2025 — his 9/11 letter, ref D065206).

Two lists, every number computed here:
 1. The roll contradicting itself: a private, non-residential parcel whose own
    record carries a 2024+ build year and $0 building value. Overture Maps
    (2026-08-19) names the business inside the lot where it has one.
 2. Sales-ratio outliers: arm's-length commercial / industrial / apartment
    sales since Jan 2025 whose ratio (value on the Aug 2026 file / price) sits
    outside 0.60-1.50.
"""
import duckdb, html, json, pathlib, re, statistics as st, sys, datetime as dt
tc = lambda s: re.sub(r"(\d)(St|Nd|Rd|Th)\b", lambda m: m.group(1) + m.group(2).lower(), (s or "").title())

HERE = pathlib.Path(__file__).parent
BR = pathlib.Path.home() / "Desktop/workspace/bricks"
sys.path.insert(0, str(BR / "scripts"))
from commercial_ratio_study import family

SELF = ('BLOOMINGTON', 'BROOKLYN PARK', 'EDEN PRAIRIE', 'EDINA', 'MINNEAPOLIS', 'MINNETONKA', 'ST LOUIS PARK', 'MAPLE GROVE', '')
V = "county_hennepin_2026_08"
PUBLIC = re.compile(r"\b(CITY|VILLAGE|COUNTY|STATE OF|GOVT|COMMISSION|AUTH|EDA|HRA|SCHOOL|DIST|CHURCH|CHUR|LUTH|METH|CATH|PARK BOARD|WATERSHED|MET COUNCIL|METROPOLITAN COUNCIL|VIL|UNIV|HOUSING)\b")
NONRES = ('COMMERCIAL-PREFERRED', 'COMMERCIAL-NON PREFERRED', 'INDUSTRIAL-PREFERRED', 'INDUSTRIAL-NON PREFERRED',
          'LAND-COMMERCIAL', 'LAND - INDUSTRIAL', 'LAND-INDUSTRIAL', 'VACANT LAND-APARTMENT', 'APARTMENT')
LO, HI = 0.60, 1.50

c = duckdb.connect(str(BR / "data/closed_system.duckdb"), read_only=True)
roll = {r[0]: (r[0], r[1], (r[2] or "").title(), *r[3:]) for r in c.execute(f"""
  select pin, trim(anumber||' '||street), trim(city), useclass1, emv_land, emv_bldg, emv_total, year_built, trim(owner_name), total_tax, sale_date, sale_value
  from parcel_snapshot where vintage='{V}' and upper(trim(coalesce(city,''))) not in {SELF}""").fetchall()}

def places(pin):
    return [(n, a) for n, a, conf in c.execute(
        "select attrs->>'name', attrs->>'addr', (attrs->>'confidence')::double from record where layer='overture_places' and parcel_key=? order by 3 desc",
        ['hennepin:' + pin]).fetchall() if conf and conf >= 0.8]

# 1 -- the roll contradicting itself
contra = []
for pin, (p, addr, city, use, land, bldg, tot, yb, owner, tax, sd, sv) in roll.items():
    if use in NONRES and (yb or 0) >= 2024 and not (bldg or 0) and not PUBLIC.search((owner or "").upper()):
        num = addr.split(" ")[0]
        biz = [n for n, a in places(pin) if (a or "").split(" ")[0] == num and not n.endswith(", MN")]
        contra.append({"pin": pin, "address": tc(addr), "city": city, "class": use, "year_built": yb,
                       "land": land, "building": bldg or 0, "owner": owner, "businesses": biz[:3],
                       "last_sale": sd.isoformat() if sd else None, "last_price": sv or None})
contra.sort(key=lambda x: (-len(x["businesses"]), -(x["last_price"] or 0), -x["land"]))
tiny = [ {"pin": pin, "address": tc(r[1]), "city": r[2], "class": r[3], "total": r[6], "year_built": r[7], "owner": r[8],
          "last_price": r[11], "last_sale": r[10].isoformat() if r[10] else None, "businesses": [n for n, a in places(pin)][:2]}
        for pin, r in roll.items() if r[3] in NONRES and 0 < (r[6] or 0) < 1000 and (r[7] or 0) > 1800
        and not PUBLIC.search((r[8] or "").upper()) and (r[11] or 0) > 100000]

# 2 -- ratio outliers
sales = json.load(open(BR / "website/api/_data/exports/sales.json"))["rows"]
clean = []
for s in sales:
    pin = s.get("parcel_id")
    if "Hennepin" not in (s.get("county") or "") or pin not in roll: continue
    if not (s.get("assessed") and s.get("price")) or s["price"] < 50_000: continue
    if s.get("arms_length") is not True or s.get("usable_comp") is not True: continue
    if s.get("multi_parcel_deed") or s.get("shares_price_and_month"): continue
    if s["sale_month"] < "2025-01" or family(s.get("use")) not in ("commercial", "industrial", "apartment"): continue
    clean.append({**s, "ratio": s["assessed"] / s["price"], "city": roll[pin][2], "fam": family(s["use"])})
rat = [x["ratio"] for x in clean]
med = st.median(rat)
cod = 100 * sum(abs(r - med) for r in rat) / len(rat) / med
out = sorted([x for x in clean if not LO <= x["ratio"] <= HI], key=lambda x: x["ratio"])
under = [x for x in out if x["ratio"] < LO]; over = [x for x in out if x["ratio"] > HI]

F = {"built_on": "2026-09-26", "roll_file": "Hennepin parcel file pulled 2026-08-14", "sales_file_retrieved": "2026-08-18",
     "county_assessed_parcels": len(roll), "contradictions": contra, "under_1000": tiny,
     "ratio": {"n": len(clean), "median": round(med, 3), "cod": round(cod, 1), "band": [LO, HI],
               "under": len(under), "over": len(over)},
     "outliers": [{k: x[k] for k in ("parcel_id", "address", "city", "use", "sale_month", "price", "assessed", "ratio")} for x in out]}
(HERE / "findings.json").write_text(json.dumps(F, indent=1, default=str))

e = html.escape
m = lambda v: f"${v:,.0f}"
with_biz = [x for x in contra if x["businesses"]]

def crow(x):
    biz = f"<div class='biz'>Operating there: {e(', '.join(x['businesses']))}</div>" if x["businesses"] else ""
    sale = f" · sold {x['last_sale'][:7]} for {m(x['last_price'])}" if x["last_price"] else ""
    return f"""<li><div class="who">{e(x['address'])}, {e(x['city'])} <span class="pin">PID {x['pin']}</span></div>
<div class="meta">{e(x['class'])} · built {x['year_built']} · land {m(x['land'])} · <b>building $0</b>{sale}</div>{biz}
<div class="meta">Owner of record: {e(x['owner'])}</div></li>"""

def orow(x):
    return f"""<tr><td>{e(x['address'])}<br><span class="pin">PID {x['parcel_id']} · {e(x['use'])}</span></td>
<td>{x['sale_month']}</td><td>{m(x['price'])}</td><td>{m(x['assessed'])}</td><td><b>{x['ratio']:.2f}</b></td></tr>"""

page = f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>For Anthony Bauer, Hennepin County Assessor</title>
<meta name="robots" content="noindex">
<style>
:root{{--ink:#1b1b1b;--soft:#5b5b5b;--line:#e4e1da;--bg:#fbfaf7;--mark:#8a2b0f}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 Georgia,"Times New Roman",serif}}
main{{max-width:680px;margin:0 auto;padding:40px 20px 64px}}
.to{{font:13px/1.4 system-ui,sans-serif;color:var(--soft)}}
h1{{font-size:clamp(24px,5.8vw,33px);line-height:1.2;margin:14px 0}}
h2{{font-size:20px;margin:40px 0 8px}}
p{{margin:0 0 14px}}
ol{{list-style:none;padding:0;margin:20px 0}}
li{{border-top:1px solid var(--line);padding:14px 0}}
.who{{font-weight:700}} .pin{{font:12px system-ui,sans-serif;color:var(--soft);font-weight:400}}
.meta{{font:14px/1.45 system-ui,sans-serif;color:var(--soft);margin-top:3px}} .meta b{{color:var(--mark)}}
.biz{{font-size:15px;margin-top:4px}}
.scroll{{overflow-x:auto}}
table{{border-collapse:collapse;font:14px/1.4 system-ui,sans-serif;width:100%;min-width:520px}}
td,th{{border-top:1px solid var(--line);padding:8px 6px;text-align:left;vertical-align:top}} th{{color:var(--soft);font-weight:600}}
.small{{font:14px/1.55 system-ui,sans-serif;color:var(--soft)}}
footer{{margin-top:40px;border-top:1px solid var(--line);padding-top:18px}}
</style>
<main>
<div class="to">For Anthony M Bauer, CMA · Hennepin County Assessor · re: D065206 · Sept 26, 2026</div>
<h1>{len(contra)} parcels on your roll say they were built in 2024 or 2025 and carry $0 of building.</h1>
<p>Your September 11 letter said the office runs no mass appraisal model on commercial property and commissioned no studies. So we ran two checks on the {len(roll):,} parcels your office values itself &mdash; the county file, less Bloomington, Brooklyn Park, Eden Prairie, Edina, Minneapolis, Minnetonka, St. Louis Park and Maple Grove.</p>
<p>The first is the roll against itself: private commercial, industrial and apartment parcels whose own record carries a 2024 or 2025 build year and a building value of zero. On {len(with_biz)} of them a business is operating today at that address.</p>
<ol>{''.join(crow(x) for x in contra)}</ol>
{('<h2>And ' + str(len(tiny)) + ' commercial parcel' + ('s' if len(tiny)>1 else '') + ' valued under $1,000</h2><ol>' + ''.join(f"<li><div class='who'>{e(t['address'])}, {e(t['city'])} <span class='pin'>PID {t['pin']}</span></div><div class='meta'>{e(t['class'])} · built {t['year_built']} · <b>total value {m(t['total'])}</b> · sold {t['last_sale'][:7] if t['last_sale'] else ''} for {m(t['last_price'])}</div>" + (f"<div class='biz'>Operating there: {e(', '.join(t['businesses']))}</div>" if t['businesses'] else '') + "</li>" for t in tiny) + '</ol>') if tiny else ''}

<h2>{len(out)} commercial sales since January 2025 that sit far from their value</h2>
<p>Second, a ratio study on the same parcels: every arm's-length, county-usable, single-parcel commercial, industrial and apartment sale since January 2025 &mdash; {len(clean)} of them. Median ratio {med:.2f}, COD {cod:.1f} against IAAO's 20. These {len(out)} fall outside {LO:.2f}&ndash;{HI:.2f}: {len(under)} valued well under what they sold for, {len(over)} well over.</p>
<div class="scroll"><table><tr><th>Parcel</th><th>Sold</th><th>Price</th><th>Value on file</th><th>Ratio</th></tr>{''.join(orow(x) for x in out)}</table></div>

<h2>How this was done</h2>
<p class="small">Parcels, values, classes, build years and owners: Hennepin's own parcel file, pulled August 14, 2026. Sales: the county's sale of record (retrieved August 18, 2026) with its own arm's-length and usable-comp flags; deeds covering several parcels, or sharing a price and month with another, are dropped. &ldquo;Value on file&rdquo; is the market value on that August file, so a sale after January 2 is compared with a value set before it. Businesses: Overture Maps Foundation places, release 2026-08-19, kept only where the listing's street number matches the parcel's. Public and church owners are left out. Nothing here came from your office beyond what it publishes.</p>

<footer class="small">
<p>This one is free, on us. If there's other work you'd like done, just let us know.</p>
<p>A few things we could do next, if useful: the same two checks run every month against the new parcel file ($200 a month) &middot; an independent annual ratio study on commercial and apartment sales, by class and city, written up to IAAO's standard ($2,500) &middot; the same roll check for the eight cities that assess themselves, sent to each of them ($500).</p>
<p>Aidan Jude &middot; aidan@brickandmortar.dev</p>
</footer>
</main>
"""
(HERE / "index.html").write_text(page)
print(json.dumps({k: v for k, v in F.items() if k not in ("contradictions", "outliers", "under_1000")}, indent=1))
for x in contra: print("C", x["address"], x["city"], x["class"], x["year_built"], int(x["land"]), x["owner"][:25], x["last_price"], x["businesses"])
for t in tiny: print("T", t)
for x in out: print("O", x["address"], x["sale_month"], x["price"], x["assessed"], round(x["ratio"], 2))
