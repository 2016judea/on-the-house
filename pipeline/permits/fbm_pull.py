"""New mobile food, caterers and grocery/meat markets in Minneapolis, for the 2026-10-10
Facebook Marketplace gifts (kitchen landlords, cooler and equipment sellers).

A facility counts as NEW when its first inspection on record since 2024-01-01 falls on or after
SINCE (trucks, carts, limited mobile, caterers: 2026-01-01; grocery + meat market: 2026-04-01).
The inspection address of a truck or caterer is the licensed base kitchen it operates from.
Owner/manager from MN Secretary of State, cached in hosp_sos.json (shared with hospitality_pull.py).
Writes fbm_food.json."""
import json, urllib.request, urllib.parse, datetime as dt, re, os, time, html
B = "https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services"
MOBILE = ("FOOD TRUCK", "FOOD CART", "LIMITED MOBILE", "CATERER")
MARKET = ("GROCERY", "MEAT MARKET")
SINCE = {**{c: dt.date(2026, 1, 1) for c in MOBILE}, **{c: dt.date(2026, 4, 1) for c in MARKET}}
SKIP = re.compile(r"public schools|school|canteen at ups|event network|college|university|church", re.I)


def q(where, fields):
    out, off = [], 0
    while True:
        p = dict(where=where, outFields=fields, f="json", resultOffset=off, resultRecordCount=2000, returnGeometry="false")
        d = json.load(urllib.request.urlopen(urllib.request.Request(f"{B}/Food_Inspections/FeatureServer/0/query", data=urllib.parse.urlencode(p).encode())))
        fs = [f["attributes"] for f in d.get("features", [])]; out += fs
        if not d.get("exceededTransferLimit") or not fs: break
        off += len(fs)
    return out


D = lambda ms: dt.datetime.utcfromtimestamp(int(ms) / 1000).date()
F = q("YearOfInspection>=2024", "HealthFacilityIDNumber,BusinessName,FacilityCategory,DateOfInspection,FullAddress,Neighborhood,Latitude,Longitude")
first = {}
for f in F:
    d = D(f["DateOfInspection"]); k = f["HealthFacilityIDNumber"]
    if k not in first or d < first[k][0]: first[k] = (d, f)
latest = max(D(f["DateOfInspection"]) for f in F)

def norm(s): return re.sub(r"[^a-z0-9]", "", re.sub(r"\b(llc|inc|co|corp|the|restaurant|cafe|café|and|&)\b", "", (s or "").lower()))
SC = json.load(open("hosp_sos.json")) if os.path.exists("hosp_sos.json") else {}
UA = {"User-Agent": "Mozilla/5.0"}
def get(u):
    time.sleep(0.6); return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "replace")
def text(h):
    h = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S); return [l.strip() for l in html.unescape(re.sub(r"<[^>]+>", "\n", h)).split("\n") if l.strip()]
def sos(name):
    k = norm(name)
    if not k or len(k) < 4: return None
    if name in SC: return SC[name]
    res = None
    try:
        s = re.sub(r"\b(LLC|L\.L\.C\.|INC\.?|CORP\.?)\b", "", name, flags=re.I).strip(" ,.")
        h = get("https://mblsportal.sos.mn.gov/Business/BusinessSearch?" + urllib.parse.urlencode(dict(BusinessName=s, IncludePriorNames="False", Status="Active", Type="BeginsWith")))
        hits = []
        for tr in h.split("<tr")[1:]:
            m = re.search(r'href="(/Business/SearchDetails\?filingGuid=[^"]+)"', tr)
            tl = text("<x" + tr)
            if m and tl and norm(tl[0]) == k: hits.append((("Assumed" in tr), m))
        hits.sort(key=lambda x: x[0])
        for _, m in hits[:3]:
            t = text(get("https://mblsportal.sos.mn.gov" + html.unescape(m.group(1))))
            after = lambda label: t[t.index(label) + 1] if label in t else ""
            bn = after("Minnesota Business Name") or after("Business Name")
            if norm(bn) != k: continue
            people = []
            for lab in ("Manager", "Chief Executive Officer", "Name Holder", "Applicant"):
                for i, x in enumerate(t):
                    if x == lab and i + 1 < len(t): people.append((lab, t[i + 1]))
            res = dict(entity=bn, type=after("Business Type"), filed=after("Filing Date"), people=people[:3], url="https://mblsportal.sos.mn.gov" + html.unescape(m.group(1)))
            break
    except Exception:
        res = None
    SC[name] = res; json.dump(SC, open("hosp_sos.json", "w"), indent=1); return res

out = []
for d, f in first.values():
    c = f["FacilityCategory"]
    if c not in SINCE or d < SINCE[c] or SKIP.search(f["BusinessName"] or ""): continue
    name = f["BusinessName"].strip()
    s = sos(name)
    out.append(dict(name=name, cat=c, first=str(d), addr=f["FullAddress"], hood=(f["Neighborhood"] or "").title(),
                    lat=f["Latitude"], lon=f["Longitude"], sos=s))
json.dump(dict(latest=str(latest), rows=out), open("fbm_food.json", "w"), indent=1)
import collections
print("latest inspection", latest, "| rows", len(out), collections.Counter(r["cat"] for r in out), "| sos", sum(bool(r["sos"]) for r in out))
