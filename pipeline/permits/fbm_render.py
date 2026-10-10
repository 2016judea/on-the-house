"""Render one /for/<token>/ page per Facebook Marketplace seller (2026-10-10).

Inputs: hospitality.json (permits + liquor + first inspections, hospitality_pull.py, Oct 5)
and fbm_food.json (new trucks, caterers, grocery/meat markets, fbm_pull.py).
Usage: python3 fbm_render.py <bricks>/website/for   (tokens read from fbm_tokens.json)
Every number in a page and in its Marketplace message is printed here; nothing is typed."""
import json, csv, re, sys, math, os, secrets, collections
import pathlib as _pl
sys.argv = [sys.argv[0], "/dev/null"] + sys.argv[1:]
_src = open("hospitality_render.py").read().split("cnt=lambda")[0]
exec(_src)                                   # -> E (hospitality events), rows (one per E), RIVER, T, _READER
HROWS = list(zip(E, rows))
FOR = sys.argv[2]
FOOD = json.load(open("fbm_food.json"))
TOK = json.load(open("fbm_tokens.json")) if os.path.exists("fbm_tokens.json") else {}

def mi(a, b):
    if not a or not b: return ""
    R = 3958.8; p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(h)), 1)

STREET = lambda a: re.sub(r" (Ne|Se|Nw|Sw)$", lambda m: " "+m.group(1).upper(), re.sub(r"(\d)(St|Nd|Rd|Th)\b", lambda m: m.group(1)+m.group(2).lower(), re.sub(r"\s*#.*$", "", a).title()))
TCASE = lambda x: re.sub(r"'S\b", "'s", x.title()).replace("Llc", "LLC").replace("Bbq", "BBQ") if x and x.isupper() else (x or "")
KIND = {"New restaurant or bar opening": "Restaurant build-out", "Remodel": "Kitchen remodel", "New hood going in": "New kitchen hood", "Expansion": "Restaurant expansion"}

# ---- permit rows (kitchen work with a city permit)
def permit_rows():
    out = []
    for e, r in HROWS:
        p = e["permit"]
        if not p: continue
        out.append(dict(kind=KIND[p["kind"]], stage=p["stage"], name=r["name"], street=e["addr"], hood=r["hood"], lat=r["lat"], lon=r["lon"],
                        what=p["what"].rstrip(" .") + ".", by=p["by"], latest=max(x for x in (p["issued"], p["done"]) if x) if (p["issued"] or p["done"]) else "",
                        issued=p["issued"], permit=p["permit"], owner=r["owner"], entity=r["entity"], sosurl=r["sosurl"], web=r["web"], phone=r["phone"], maps=r["maps"],
                        src="Minneapolis building permit"))
    return out

# ---- new food businesses from the inspection register
def food_rows(cats):
    seen = {}
    for f in FOOD["rows"]:
        if f["cat"] not in cats or not f["addr"] or not f["lat"]: continue
        if re.search(r"canteen|vending|compass group|garfield holdings|khp iv|^jaime michay$", f["name"], re.I): continue
        nm = re.sub(r"\s*-\s*(GROCERY|MEAT MARKET)$", "", f["name"]).strip()
        k = (nm.upper(), f["addr"])
        s = f["sos"] or {}
        people = [f"{TCASE(n)} ({l.replace('Chief Executive Officer', 'CEO').lower()})" for l, n in s.get("people", []) if l in ("Manager", "Chief Executive Officer") and " " in n.strip() and n != "Not Available" and not re.search(r"\bLLC\b", n)]
        if k in seen:
            seen[k]["cats"].add(f["cat"]); continue
        seen[k] = dict(cats={f["cat"]}, name=TCASE(nm), street=STREET(f["addr"]),
                       hood=f["hood"], lat=round(f["lat"], 5), lon=round(f["lon"], 5), latest=f["first"], owner="; ".join(people), entity=s.get("entity", ""), sosurl=s.get("url", ""),
                       web="", phone="", maps="", by="", permit="", issued="", src="Minneapolis health inspection register")
    out = []
    for r in seen.values():
        c = r.pop("cats")
        if c & {"FOOD TRUCK", "FOOD CART"}: r["kind"] = "New food truck"
        elif "LIMITED MOBILE" in c: r["kind"] = "New ice cream or cart vendor"
        elif "CATERER" in c: r["kind"] = "New caterer"
        elif c == {"GROCERY", "MEAT MARKET"}: r["kind"] = "New grocery with a meat counter"
        elif "MEAT MARKET" in c: r["kind"] = "New meat market"
        else: r["kind"] = "New grocery or corner store"
        if r["kind"] in ("New food truck", "New ice cream or cart vendor", "New caterer"):
            r["what"] = {"New food truck": "Food truck", "New ice cream or cart vendor": "Mobile vendor", "New caterer": "Caterer"}[r["kind"]] + f" licensed and first inspected {md(r['latest'])}, based at this kitchen."
        else:
            r["what"] = {"New grocery with a meat counter": "Grocery and meat market", "New meat market": "Meat market", "New grocery or corner store": "Grocery"}[r["kind"]] + f" licensed and first inspected {md(r['latest'])}."
        r["stage"] = ""
        out.append(r)
    # shared base kitchens: an address that 3+ of the new mobile/caterer businesses list as home
    base = collections.Counter(r["street"] for r in out if r["kind"] in ("New food truck", "New caterer", "New ice cream or cart vendor"))
    for r in out:
        r["shared"] = base[r["street"]] if base[r["street"]] >= 3 and r["kind"] in ("New food truck", "New caterer", "New ice cream or cart vendor") else 0
        if r["shared"]: r["what"] += f" {r['shared']} new mobile food businesses share this address."
    return out, base

MOBILE = {"FOOD TRUCK", "FOOD CART", "LIMITED MOBILE", "CATERER"}
MARKET = {"GROCERY", "MEAT MARKET"}

PAL = {
 "steel": ('--bg:#f2f3f4;--panel:#e6e8ea;--ink:#16191d;--ink2:#353b42;--muted:#666e77;--rule:#cfd4d9;--accent:#2d5f86;--onaccent:#f2f3f4;--hot:#c0532c;--lic:#6c5a9c;--done:#8f969d;--ghost:#c6cbd0;--water:#94afc2;--tagbg:#e0e4e8;--tagfg:#47505a;--hotbg:#f4dccf;--hotfg:#8a3414;--display:"Archivo",system-ui,sans-serif;--body:"Inter Tight",system-ui,sans-serif;--h1w:700;',
           '--bg:#121417;--panel:#1a1e22;--ink:#e7eaed;--ink2:#c3c9cf;--muted:#8b939b;--rule:#2a3036;--accent:#7fb2dc;--onaccent:#121417;--hot:#ec8c66;--lic:#b3a3e3;--done:#6c747b;--ghost:#2b3137;--water:#3f6178;--tagbg:#20262b;--tagfg:#aeb7bf;--hotbg:#45261a;--hotfg:#f4b9a0;',
           "family=Archivo:wght@700&family=Inter+Tight:wght@400;500;600"),
 "frost": ('--bg:#f1f5f6;--panel:#e3ecee;--ink:#122024;--ink2:#2f4247;--muted:#5f7378;--rule:#cbd9dc;--accent:#1d6f82;--onaccent:#f1f5f6;--hot:#b8562f;--lic:#5b6ea8;--done:#8a9a9e;--ghost:#c2d0d3;--water:#8fb3c1;--tagbg:#dce7ea;--tagfg:#3e555b;--hotbg:#f2ddd1;--hotfg:#83361a;--display:"Space Grotesk",system-ui,sans-serif;--body:"Inter Tight",system-ui,sans-serif;--h1w:600;',
           '--bg:#0f1719;--panel:#162124;--ink:#e4eef0;--ink2:#bfd0d4;--muted:#88a0a5;--rule:#253539;--accent:#6fc3d6;--onaccent:#0f1719;--hot:#e89069;--lic:#a2b1e6;--done:#68797d;--ghost:#26363a;--water:#3a6371;--tagbg:#1c2a2d;--tagfg:#a7bcc0;--hotbg:#42271b;--hotfg:#f2bba2;',
           "family=Space+Grotesk:wght@600&family=Inter+Tight:wght@400;500;600"),
 "fire":  ('--bg:#f6f2ee;--panel:#ede6df;--ink:#211913;--ink2:#433830;--muted:#76685d;--rule:#ddd2c7;--accent:#a8431f;--onaccent:#f6f2ee;--hot:#a8431f;--lic:#2f6b73;--done:#9a8e84;--ghost:#d3c8bd;--water:#a6b9c0;--tagbg:#e8dfd6;--tagfg:#5a4c41;--hotbg:#f3d8c8;--hotfg:#86310f;--display:"Fraunces",Georgia,serif;--body:"Inter Tight",system-ui,sans-serif;--h1w:600;',
           '--bg:#161210;--panel:#1f1916;--ink:#efe7e1;--ink2:#cdbfb5;--muted:#9a8b80;--rule:#30271f;--accent:#ee8a5f;--onaccent:#161210;--hot:#ee8a5f;--lic:#7fc0c8;--done:#76695f;--ghost:#33291f;--water:#3f5e68;--tagbg:#261f1a;--tagfg:#bfb0a5;--hotbg:#47261a;--hotfg:#f6bba1;',
           "family=Fraunces:opsz,wght@9..144,600&family=Inter+Tight:wght@400;500;600"),
 "brick": ('--bg:#f4f2ef;--panel:#e9e5e0;--ink:#1c1a17;--ink2:#3d3833;--muted:#6f6861;--rule:#d6d0c9;--accent:#3c6b4f;--onaccent:#f4f2ef;--hot:#b4502c;--lic:#3c6b4f;--done:#958e87;--ghost:#cdc6bf;--water:#9cb3bd;--tagbg:#e3ded8;--tagfg:#514a43;--hotbg:#f2d9cc;--hotfg:#863314;--display:"Bricolage Grotesque",system-ui,sans-serif;--body:"Inter Tight",system-ui,sans-serif;--h1w:700;',
           '--bg:#131512;--panel:#1b1e1a;--ink:#e8ebe6;--ink2:#c4cac1;--muted:#8d968a;--rule:#2a2f28;--accent:#86c39c;--onaccent:#131512;--hot:#ea8d67;--lic:#86c39c;--done:#6d7469;--ghost:#2c3229;--water:#3e5f68;--tagbg:#20251f;--tagfg:#afb8ab;--hotbg:#43261b;--hotfg:#f3baa1;',
           "family=Bricolage+Grotesque:opsz,wght@12..96,700&family=Inter+Tight:wght@400;500;600"),
}

STAGE_O = {"Final inspection": 0, "Under construction": 1, "Just opened": 2, "": 3}

def build(slug, cfg):
    R = cfg["rows"]()
    home = cfg.get("home")
    for r in R:
        r["mi"] = mi((home["lat"], home["lon"]), (r["lat"], r["lon"])) if home else ""
        r["addr"] = r["name"] or r["street"]
        r["tagtxt"] = r["kind"] + (" · " + r["stage"].lower() if r["stage"] else "")
    order = cfg["chips"]
    R = [r for r in R if r["kind"] in order]
    cnt = collections.Counter(r["kind"] for r in R)
    facts = cfg["facts"](R, cnt)
    sorts = {"first": "r=>{const O=%s,S=%s;return r.sort((a,b)=>(O[a.kind]-O[b.kind])||(S[a.stage]-S[b.stage])||b.latest.localeCompare(a.latest))}" % (json.dumps({k: i for i, k in enumerate(order)}), json.dumps(STAGE_O)),
             "newest": "r=>r.sort((a,b)=>b.latest.localeCompare(a.latest))",
             "near": "r=>r.sort((a,b)=>a.mi-b.mi)",
             "by": "r=>r.sort((a,b)=>(!a.by)-(!b.by)||a.by.localeCompare(b.by))",
             "hood": "r=>r.sort((a,b)=>a.hood.localeCompare(b.hood))"}
    sortsel = cfg["sorts"]
    labels = {"first": cfg.get("firstlabel", "Most useful first"), "newest": "Newest first", "near": f"Closest to {home['label']}" if home else "", "by": "By contractor", "hood": "By neighborhood"}
    cols = [("kind", "What it is"), ("stage", "Permit stage"), ("name", "Business"), ("street", "Address"), ("hood", "Neighborhood"), ("what", "What changed"), ("latest", "Latest date"),
            ("by", "Contractor on the permit"), ("owner", "Owner or manager (MN Secretary of State)"), ("entity", "Business entity"), ("phone", "Phone"), ("web", "Website"), ("permit", "Permit #"), ("sosurl", "State filing link"), ("src", "Source")]
    if home: cols.insert(5, ("mi", f"Miles from {home['label']}"))
    colors = ["var(--hot)", "var(--accent)", "var(--lic)", "var(--done)", "var(--ink2)", "var(--muted)"]
    cmap = {k: colors[i % len(colors)] for i, k in enumerate(order)}
    meta_first = cfg.get("meta_first", "owner")
    js = """{chipKey:"kind",chipOrder:%s,river:%s,home:%s,
 stats:%s,
 legend:%s,
 color:r=>(%s)[r.kind]||"var(--done)",
 tag:r=>`<span class="tag ${r.stage==="Final inspection"||r.stage==="Under construction"?"hot":""}">${esc(r.stage||r.kind.replace(/^New /,""))}</span>`,
 meta:r=>{const by=r.by?("Contractor: "+r.by):"",ow=r.owner?("Owner: "+r.owner):(r.entity?("Entity: "+r.entity):"");return [%s,r.name?r.street:"",r.hood,r.mi!==""?(r.mi+" mi from %s"):"",r.phone,r.latest?(fmt(r.latest)):""]},
 links:r=>{const L=[];if(r.web)L.push(`<a href="${esc(r.web)}" rel="noopener" target="_blank">Website</a>`);if(r.maps)L.push(`<a href="${esc(r.maps)}" rel="noopener" target="_blank">Google</a>`);if(r.sosurl)L.push(`<a href="${esc(r.sosurl)}" rel="noopener" target="_blank">State filing</a>`);return L.length?`<span class="m lk">${L.join("")}</span>`:""},
 sorts:{%s},
 cols:%s}""" % (json.dumps(order), json.dumps(RIVER), json.dumps(dict(lat=home["lat"], lon=home["lon"], label=home["label"], inMap=home["inMap"]) if home and home["inMap"] else (dict(label=home["offlabel"], inMap=False) if home else None)),
                json.dumps(facts["stats"]), json.dumps([[cmap[k], k] for k in order if cnt[k]]), json.dumps(cmap),
                ("by,ow" if meta_first == "by" else "ow,by"), home["label"] if home else "",
                ",".join(f"{k}:{sorts[k]}" for k in sortsel), json.dumps(cols))
    pal = PAL[cfg["pal"]]
    sorthtml = "".join(f'<option value="{k}">{labels[k]}</option>' for k in sortsel)
    csvn = cfg["csv"]
    h = T.replace(".toast{", ".lk{gap:4px 14px}.lk a{color:var(--accent);font-weight:600;text-decoration:none}.lk a:hover{text-decoration:underline}.toast{")
    for k, v in {"__TITLE__": cfg["title"], "__CSV__": csvn, "__FONTS__": pal[2], "__LIGHT__": pal[0], "__DARK__": pal[1], "__EYEBROW__": cfg["eyebrow"], "__H1__": facts["h1"],
                 "__LEDE__": facts["lede"], "__SORTS__": sorthtml, "__NOTE__": NOTE(cfg)}.items():
        h = h.replace(k, v)
    h = h.replace('aria-label="Map of Minneapolis with each permit as a dot"', 'aria-label="Map of Minneapolis with each business as a dot"')
    keep = ["kind", "stage", "name", "street", "addr", "hood", "lat", "lon", "what", "latest", "by", "owner", "entity", "sosurl", "web", "phone", "maps", "permit", "mi", "src"]
    h = h.replace("__CFG__", js).replace("__ROWS__", json.dumps([{k: r.get(k, "") for k in keep} for r in R], separators=(",", ":")))
    head, body = h.split('<div class="wrap">', 1)
    tok = TOK.setdefault(slug, secrets.token_hex(4))
    out = f"{FOR}/{tok}"; os.makedirs(out, exist_ok=True)
    open(f"{out}/index.html", "w").write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex"><script defer src="/_vercel/insights/script.js"></script>{_READER}{head}</head><body><div class="wrap">{body}</body></html>')
    with open(f"{out}/{csvn}", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow([c[1] for c in cols]); [w.writerow([r.get(c[0], "") for c in cols]) for r in sorted(R, key=lambda r: (order.index(r["kind"]), STAGE_O[r["stage"]]))]
    print(f"\n== {slug} -> /for/{tok}/  rows {len(R)} {dict(cnt)}")
    for k, v in facts["msg"].items(): print(f"   {k}: {v}")
    return tok

def NOTE(cfg):
    return ("<p>Sources, all public: City of Minneapolis building permits (pulled Oct 4, 2026), its on-sale liquor license list, its food inspection register (through "
            + md(FOOD["latest"]) + "), Google Maps listings for website and phone, and business filings at the Minnesota Secretary of State for owner names.</p>"
            "<p>A business counts as new when its first health inspection on record since January 2024 falls this year (trucks, carts and caterers) or since April 1 (groceries and meat markets). "
            "A truck or caterer's address is the licensed kitchen it works out of, not where it parks. Permit stage is the city's: under construction, final inspection, or finished.</p>"
            "<p>Minneapolis only. School, hospital and corporate cafeteria kitchens are left out. " + cfg.get("notex", "") + "</p>"
            "<p>Free, from Aidan Jude at Brick &amp; Mortar (aidan@brickandmortar.dev). Nothing to sign up for.</p>")

PR = permit_rows()
FR_ALL, BASE = food_rows(MOBILE | MARKET)
mob = lambda: [dict(r) for r in FR_ALL if r["kind"] in ("New food truck", "New caterer", "New ice cream or cart vendor")]
mkt = lambda: [dict(r) for r in FR_ALL if r["kind"].startswith("New grocery") or r["kind"] == "New meat market"]
prm = lambda: [dict(r) for r in PR]
live = lambda r: r["stage"] in ("Under construction", "Final inspection")
top_base = BASE.most_common(1)[0]

SELLERS = {
 "contier": dict(pal="steel", title="Kitchens Out to Quote", csv="minneapolis-kitchen-jobs.csv",
   eyebrow="Made for Contier · Minneapolis permits · updated Oct 10, 2026",
   home=dict(lat=44.8505, lon=-93.2884, label="your Bloomington showroom", offlabel="Your Bloomington showroom is south of this map", inMap=False),
   rows=prm, chips=["Restaurant build-out", "New kitchen hood", "Kitchen remodel", "Restaurant expansion"], sorts=["first", "near", "by", "newest"], firstlabel="Still being built first", meta_first="by",
   facts=lambda R, c: dict(
     h1=f"{len(R)} Minneapolis kitchens with a permit for equipment, hoods or a remodel",
     lede=f"Your listing offers a quote on kitchen equipment, hoods, remodeling or furnishing. These are the Minneapolis jobs where the city has already issued a permit for exactly that work. "
          f"<b>{sum(live(r) for r in R)} are still under construction or at final inspection</b>, so the equipment isn't all bought yet. Each one shows the contractor on the permit and, where the state has it, the owner.",
     stats=[[str(c['Restaurant build-out']), "restaurant build-outs"], [str(c['New kitchen hood']), "new kitchen hoods"], [str(sum(live(r) for r in R)), "still under construction"]],
     msg=dict(total=len(R), live=sum(live(r) for r in R), hoods=c['New kitchen hood'], buildouts=c['Restaurant build-out'], with_contractor=sum(bool(r['by']) for r in R)))),

 "dandb": dict(pal="steel", title="Who Needs Stainless", csv="kitchens-and-trucks.csv",
   eyebrow="Made for D&B Restaurant Supply · Minneapolis public records · updated Oct 10, 2026",
   home=dict(lat=44.8930, lon=-93.0350, label="South St Paul", offlabel="South St Paul is east of this map", inMap=False),
   rows=lambda: [r for r in prm() if live(r) or r["kind"] == "Restaurant build-out"] + [r for r in mob() if r["kind"] == "New food truck"],
   chips=["Restaurant build-out", "Kitchen remodel", "New kitchen hood", "Restaurant expansion", "New food truck"], sorts=["first", "near", "newest", "hood"], firstlabel="Still being built first",
   facts=lambda R, c: dict(
     h1=f"{len(R)} Minneapolis kitchens and food trucks that need tables now",
     lede=f"You sell NSF stainless tables for restaurants and food trucks, pick up seven days a week. These are the kitchens being built or rebuilt in Minneapolis right now, "
          f"plus <b>{c['New food truck']} food trucks the city licensed for the first time this year</b>. Owner names come from the state filing where one exists.",
     stats=[[str(sum(live(r) for r in R)), "kitchens under construction or at final inspection"], [str(c['New food truck']), "new food trucks this year"], [str(sum(bool(r['owner']) for r in R)), "with an owner's name"]],
     msg=dict(total=len(R), live=sum(live(r) for r in R), trucks=c['New food truck']))),

 "randy": dict(pal="frost", title="Walk-ins Wanted", csv="walk-in-buyers.csv",
   eyebrow="Made for Randy · Minneapolis public records · updated Oct 10, 2026",
   home=dict(lat=44.9537, lon=-93.0900, label="St Paul", offlabel="St Paul is east of this map", inMap=False),
   rows=lambda: [r for r in prm() if r["kind"] in ("Restaurant build-out", "Kitchen remodel", "Restaurant expansion")] + mkt(),
   chips=["Restaurant build-out", "Kitchen remodel", "Restaurant expansion", "New grocery with a meat counter", "New meat market", "New grocery or corner store"], sorts=["first", "near", "newest", "hood"], firstlabel="Still being built first",
   facts=lambda R, c: dict(
     h1=f"{len(R)} Minneapolis kitchens and stores that may need a walk-in",
     lede=f"You're selling used Superior walk-in coolers. A walk-in goes in while a kitchen is being built, and every new grocery or meat counter needs cold storage. "
          f"<b>{sum(live(r) for r in R)} restaurant kitchens are under construction or at final inspection</b>, and {sum(r['kind'].startswith('New grocery') or r['kind']=='New meat market' for r in R)} groceries and meat markets got their first health inspection since April.",
     stats=[[str(sum(live(r) for r in R)), "kitchens still being built"], [str(sum(r['kind'].startswith('New grocery') or r['kind']=='New meat market' for r in R)), "new groceries and meat markets"], [str(sum(bool(r['owner']) for r in R)), "with an owner's name"]],
     msg=dict(total=len(R), live=sum(live(r) for r in R), markets=sum(r['kind'].startswith('New grocery') or r['kind']=='New meat market' for r in R),
              meat=sum(r['kind'] in ('New grocery with a meat counter', 'New meat market') for r in R)))),

 "sonna": dict(pal="frost", title="Cold Room Contractors", csv="walk-in-projects.csv",
   eyebrow="Made for Sonna · Minneapolis public records · updated Oct 10, 2026",
   rows=lambda: [r for r in prm() if r["kind"] != "New kitchen hood"] + mkt(),
   chips=["Restaurant build-out", "Restaurant expansion", "Kitchen remodel", "New grocery with a meat counter", "New meat market", "New grocery or corner store"], sorts=["by", "first", "newest", "hood"], meta_first="by",
   facts=lambda R, c: dict(
     h1=f"{len(R)} Minneapolis cooler projects, and {len({r['by'] for r in R if r['by']})} contractors building them",
     lede=f"Your panels are for new construction, replacement or expansion: restaurants, groceries and convenience stores. "
          f"These are the Minneapolis projects of that kind on the public record now. <b>{sum(bool(r['by']) for r in R)} name the contractor</b>, who is usually the one ordering the walk-in. "
          f"Sort by contractor to see who has more than one job going.",
     stats=[[str(len({r['by'] for r in R if r['by']})), "contractors with a job open"], [str(sum(live(r) for r in R)), "kitchens still being built"], [str(sum(r['kind'].startswith('New grocery') or r['kind']=='New meat market' for r in R)), "new groceries and meat markets"]],
     msg=dict(total=len(R), contractors=len({r['by'] for r in R if r['by']}), named=sum(bool(r['by']) for r in R),
              repeat=[(b, n) for b, n in collections.Counter(r['by'] for r in R if r['by']).most_common(3)]))),

 "kim": dict(pal="fire", title="Where Fryers Go", csv="new-hoods-and-trucks.csv",
   eyebrow="Made for Kim · Minneapolis public records · updated Oct 10, 2026",
   rows=lambda: [r for r in prm() if r["kind"] in ("New kitchen hood", "Restaurant build-out")] + [r for r in mob() if r["kind"] == "New food truck"],
   chips=["New kitchen hood", "Restaurant build-out", "New food truck"], sorts=["first", "newest", "hood"], firstlabel="New hoods first",
   facts=lambda R, c: dict(
     h1=f"{len(R)} new Minneapolis kitchens a gas fryer could go into",
     lede=f"You sell new Dukers gas fryers with free shipping. A fryer needs a Type I hood over it, and the city permits every new one. "
          f"<b>{c['New kitchen hood']} kitchens put in a new hood</b>, {c['Restaurant build-out']} restaurants are being built from scratch, and {c['New food truck']} food trucks were licensed for the first time this year.",
     stats=[[str(c['New kitchen hood']), "new kitchen hoods"], [str(c['Restaurant build-out']), "restaurant build-outs"], [str(c['New food truck']), "new food trucks"]],
     msg=dict(total=len(R), hoods=c['New kitchen hood'], buildouts=c['Restaurant build-out'], trucks=c['New food truck']))),

 "rustam": dict(pal="brick", title="Looking for a Kitchen", csv="operators-who-need-a-kitchen.csv",
   eyebrow="Made for Rustam · Minneapolis public records · updated Oct 10, 2026",
   rows=lambda: mob() + [r for r in prm() if r["kind"] == "Restaurant build-out" and live(r)],
   chips=["New caterer", "New food truck", "New ice cream or cart vendor", "Restaurant build-out"], sorts=["first", "newest", "hood"], firstlabel="Caterers first",
   facts=lambda R, c: dict(
     h1=f"{c['New caterer']+c['New food truck']+c['New ice cream or cart vendor']} new Minneapolis caterers, trucks and carts, and the kitchen each one works out of",
     lede=f"Your listing is for restaurants, caterers, bakeries, ghost kitchens and commissary users. Every Minneapolis truck and caterer has to be licensed out of a real kitchen, and the city records which one. "
          f"<b>{c['New caterer']} caterers and {c['New food truck']} food trucks got their first license this year.</b> {top_base[1]} of them work out of one address, {top_base[0]}. That kitchen is filling up.",
     stats=[[str(c['New caterer']), "new caterers"], [str(c['New food truck']), "new food trucks"], [str(top_base[1]), f"sharing one kitchen at {top_base[0]}"]],
     msg=dict(total=len(R), caterers=c['New caterer'], trucks=c['New food truck'], carts=c['New ice cream or cart vendor'], top_base=top_base, buildouts=c['Restaurant build-out']))),

 "paul": dict(pal="brick", title="Trucks Need a Base", csv="new-trucks-and-pop-ups.csv",
   eyebrow="Made for Paul · Minneapolis public records · updated Oct 10, 2026",
   home=dict(lat=45.0010, lon=-93.2550, label="NE Minneapolis", offlabel="", inMap=True),
   rows=mob, chips=["New food truck", "New ice cream or cart vendor", "New caterer"], sorts=["near", "first", "newest"], firstlabel="Trucks first",
   facts=lambda R, c: dict(
     h1=f"{c['New food truck']} new Minneapolis food trucks, and where each one cooks",
     lede=f"You're spec'ing a commercial kitchen in NE Minneapolis and said you need food truck registrations. The city licenses every truck out of a base kitchen and writes the address down. "
          f"<b>{c['New food truck']} trucks, {c['New ice cream or cart vendor']} cart vendors and {c['New caterer']} caterers got their first license this year</b>, and {top_base[1]} of them share one kitchen at {top_base[0]}. Sorted closest to NE first.",
     stats=[[str(c['New food truck']), "new food trucks"], [str(c['New caterer']), "new caterers"], [str(top_base[1]), f"sharing one kitchen at {top_base[0]}"]],
     msg=dict(total=len(R), trucks=c['New food truck'], carts=c['New ice cream or cart vendor'], caterers=c['New caterer'], top_base=top_base,
              ne=sum(1 for r in R if r['mi'] != '' and r['mi'] <= 2.0)))),

 "tang": dict(pal="fire", title="Caterers Need Kitchens", csv="new-caterers-and-producers.csv",
   eyebrow="Made for Tang · Minneapolis public records · updated Oct 10, 2026",
   home=dict(lat=45.0390, lon=-93.1050, label="Little Canada", offlabel="Little Canada is northeast of this map", inMap=False),
   rows=lambda: [r for r in mob() if r["kind"] in ("New caterer", "New food truck")],
   chips=["New caterer", "New food truck"], sorts=["first", "near", "newest"], firstlabel="Caterers first",
   notex="Restaurants with a dining room are left out, since your space has no seating.",
   facts=lambda R, c: dict(
     h1=f"{len(R)} new caterers and food trucks that need a kitchen, not a dining room",
     lede=f"Your Little Canada kitchen is for a caterer, co-packer or food producer, Monday to Thursday, with no seating. That is who this list is. "
          f"<b>{c['New caterer']} caterers and {c['New food truck']} food trucks got their first Minneapolis license this year</b>, each tied to the kitchen it works out of. {top_base[1]} share a single address on {top_base[0].split(' ',1)[1].title()}.",
     stats=[[str(c['New caterer']), "new caterers"], [str(c['New food truck']), "new food trucks"], [str(sum(bool(r['owner']) for r in R)), "with an owner's name"]],
     msg=dict(total=len(R), caterers=c['New caterer'], trucks=c['New food truck'], top_base=top_base))),
}

for slug, cfg in SELLERS.items():
    build(slug, cfg)
json.dump(TOK, open("fbm_tokens.json", "w"), indent=1)
