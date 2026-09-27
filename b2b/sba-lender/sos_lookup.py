"""Look up each live SBA borrower of one lender on the MN Secretary of State's
PUBLIC business search (mblsportal.sos.mn.gov), one entity at a time.

This is the public per-entity lookup anyone can run, NOT the SOS bulk file
(which bricks holds under a researcher certification and may never export).
Every page fetched is cached under cache/sos/ so a re-run costs nothing.

usage: python3 sos_lookup.py "Falcon National Bank"
"""
import hashlib, html, json, re, sys, time, urllib.parse, pathlib, subprocess

HERE = pathlib.Path(__file__).parent
CACHE = HERE / "cache" / "sos"; CACHE.mkdir(parents=True, exist_ok=True)
LOANS = pathlib.Path.home() / "Desktop/bricks/website/api/_data/twincities_sba_loans.json"
BASE = "https://mblsportal.sos.mn.gov"
LIVE = ("EXEMPT", "COMMIT")  # SBA FOIA: EXEMPT = outstanding, COMMIT = approved, undisbursed

SUFFIX = re.compile(r"\b(l\.?\s?l\.?\s?c|inc|incorporated|corp|corporation|co|company|ltd|p\.?a|pllc|plc|llp)\b\.?", re.I)


def norm(s):
    s = SUFFIX.sub(" ", s.lower().replace("’", "'"))
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def get(url):
    f = CACHE / (hashlib.sha1(url.encode()).hexdigest() + ".html")
    if f.exists():
        return f.read_text()
    time.sleep(1.5)
    out = subprocess.run(["curl", "-s", "-L", "-m", "30", "-A", "Mozilla/5.0 (Macintosh)", url],
                         capture_output=True, text=True).stdout
    if "Search Results" in out or "Filing History" in out or "No results" in out or "Business Name" in out:
        f.write_text(out)
    return out


def text(h):
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)))


def search(name):
    q = " ".join(re.sub(r"[^A-Za-z0-9&' ]+", " ", name).split()[:3])
    url = f"{BASE}/Business/BusinessSearch?" + urllib.parse.urlencode(
        {"BusinessName": q, "IncludePriorNames": "False", "Status": "", "Type": "BeginsWith"})
    h = get(url)
    hits = []
    for m in re.finditer(r'<strong>\s*(.*?)\s*</strong>.*?href="(/Business/SearchDetails\?filingGuid=[^"]+)"', h, re.S):
        hits.append((html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip(), m.group(2)))
    if not hits:  # fall back to a looser parse of the result block
        names = re.findall(r'<h4[^>]*>\s*(.*?)\s*</h4>', h, re.S)
        links = re.findall(r'href="(/Business/SearchDetails\?filingGuid=[^"]+)"', h)
        hits = list(zip([html.unescape(re.sub(r"<[^>]+>", "", n)).strip() for n in names], links))
    want = norm(name)
    exact = [x for x in hits if norm(x[0]).replace(" ", "") == want.replace(" ", "")]
    return url, exact, hits


def detail(path):
    url = BASE + html.unescape(path)
    t = text(get(url))
    g = lambda k, nxt: (re.search(re.escape(k) + r"\s+(.*?)\s+(?:" + nxt + ")", t) or [None, None])[1]
    status = g("Status", "Renewal Due Date|Registered Office|Registered Agent|Principal|Filing History")
    renewal = g("Renewal Due Date", "Registered|Principal|Manager|Filing History")
    filed = g("Filing Date", "Status|Expiration")
    seg = t[t.find("Filing History Select"):]
    fil, _, ren = seg.partition("Renewal History Filing Date")
    ren = ren.split("Close dialog")[0]
    ev = lambda s: [{"date": d, "event": e.strip()} for d, e in
                    re.findall(r"(\d{1,2}/\d{1,2}/\d{4})\s+([A-Z][A-Za-z ,'&/]+?)\s+-\s", s)]
    hist, renewals = ev(fil), ev(ren)
    return {"url": url, "status": status, "renewal_due": renewal, "filed": filed,
            "history": hist, "renewals": renewals}


def main(lender):
    loans = json.load(open(LOANS))["loans"]
    live = [l for l in loans if l["lender"] == lender and l["status"] in LIVE]
    out = {}
    for name in sorted({l["business"] for l in live}, key=norm):
        key = norm(name)
        if key in out:
            continue
        url, exact, hits = search(name)
        rec = {"borrower": name, "search_url": url, "candidates": [h[0] for h in hits[:8]]}
        if len(exact) >= 1:
            rec["match"] = exact[0][0]
            rec["ambiguous"] = len(exact) > 1
            rec.update(detail(exact[0][1]))
        out[key] = rec
        print(f"{name[:45]:45} -> {rec.get('match','NO EXACT MATCH')[:40]:40} {rec.get('status')}", flush=True)
    slug = re.sub(r"[^a-z0-9]+", "-", lender.lower()).strip("-")
    (HERE / f"sos_{slug}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
