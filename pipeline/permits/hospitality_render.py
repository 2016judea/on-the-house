"""Render /for/<token>/ from hospitality.json (see hospitality_pull.py)."""
import json, csv, re, sys
import pathlib as _pl
# Persistent PostHog reader id + touch events for bricks /for/ pages (copy of
# bricks/scripts/outreach/reader_events.js; marker bm-visitor-id is pinned by bricks' tests).
_READER = "<script>" + (_pl.Path(__file__).resolve().parent.parent / "reader_events.js").read_text().strip() + "</script>"
# The shared PostHog block (?me=1 opt-out, no headless capture): ~/.claude/skills/site-analytics/posthog_inject.py --print.
_READER = (_pl.Path(__file__).resolve().parent.parent / "posthog.html").read_text() + _READER
exec(open("render.py").read().split("# ---------------- Vineland")[0])
T=open("template_links.html").read()
OUT=sys.argv[1]
E=[e for e in json.load(open("hospitality.json")) if not e["inst"] and e["lat"]]
ORDER=["Opening soon","Just opened","New license","Remodeling or expanding"]
f=lambda d: (d or "")[:10]
def md(d):
    import datetime as dt
    return dt.date.fromisoformat(d).strftime("%b %-d") if d else ""
TC=lambda x: re.sub(r"'S\b","'s",x.title()).replace("Llc","LLC").replace("Mpls","MPLS")
rows=[]
for e in E:
    p=e["permit"]; g=e.get("gp"); newopen=bool(p and p["kind"]=="New restaurant or bar opening")
    fresh=bool(g and (g["reviews"]<=5 or g["status"]=="CLOSED_TEMPORARILY"))
    if p and p["stage"] in("Final inspection","Under construction"):
        st="Opening soon" if (newopen or fresh) and not e["food"] else ("Just opened" if e["food"] else "Remodeling or expanding")
    elif e["food"]: st="New license" if (g and g["reviews"]>300) else "Just opened"
    elif p: st="Just opened" if newopen else "Remodeling or expanding"
    else: st="New license"
    sig=[]; dates=[]
    if p:
        sig.append(f'{p["kind"].replace("New restaurant or bar opening","New restaurant build-out").replace("New hood going in","New kitchen hood")} permit, {p["stage"].lower().replace("just opened","finished "+md(p["done"]))}')
        dates+= [p["issued"],p["done"]]
    for x in e["food"]:
        sig.append(f'First health inspection {md(x["date"])}'+(" ("+(TC(x["name"]) if x["name"].isupper() else x["name"])+")" if len(e["food"])>1 else "")); dates.append(x["date"])
    for x in {x["num"]:x for x in e["liq"]}.values():
        sig.append(f'New liquor license{" (pending)" if x["status"]=="Pending" else ""}, {md(x["date"])}'); dates.append(x["date"])
    if g and g["reviews"]<=5: sig.append(f'Google listing with {g["reviews"]} review{"s" if g["reviews"]!=1 else ""}')
    if g and g["status"]=="CLOSED_TEMPORARILY": sig.append("Google says temporarily closed")
    pref={"liquor":0,"google":1,"permit":2,"food":3}
    names=sorted(e["names"],key=lambda x:pref[x[0]])
    name=(names[0][1] if names else "")
    tc=lambda x: re.sub(r"'S\b","'s",x.title()).replace("Llc","LLC").replace("Mpls","MPLS")
    if name.isupper() or name.istitle() and "'S" in name: name=tc(name)
    s=e.get("sos"); s2=e.get("sos2")
    people=[f"{n.title() if n.isupper() else n} ({l.replace('Chief Executive Officer','CEO').lower()})" for src in (s,s2) if src for l,n in src["people"] if l in("Manager","Chief Executive Officer") and " " in n.strip()]
    holder=[n for src in (s,) if src for l,n in src["people"] if l=="Name Holder"]
    ent=(s2 or s or {}).get("entity","") if (s2 or s) else ""
    if holder: ent=holder[0]
    rk=(0 if p and p["stage"]=="Final inspection" else 1)*2+(0 if name else 1)
    rows.append(dict(stage=st,rk=rk,name=name,street=e["addr"],addr=name or e["addr"],hood=e["hood"].replace("'S ","'s "),lat=round(e["lat"],5),lon=round(e["lon"],5),
      what=" · ".join(sig),latest=max([d for d in dates if d] or [""]),
      web=(g or {}).get("web",""),phone=(g or {}).get("phone",""),reviews=(g or {}).get("reviews","") if g else "",maps=(g or {}).get("maps",""),
      owner="; ".join(dict.fromkeys(people)),entity=ent,filed=(s or {}).get("filed",""),sosurl=(s or {}).get("url",""),
      liquor="; ".join(f'{x["name"]} {x["num"]} ({x["status"]}, {x["date"]})' for x in {x["num"]:x for x in e["liq"]}.values()),
      firstinsp="; ".join(f'{TC(x["name"]) if x["name"].isupper() else x["name"]} ({x["date"]})' for x in e["food"]),
      permit=(p or {}).get("permit",""),pdesc=(p or {}).get("what",""),by=(p or {}).get("by",""),
      also="; ".join(dict.fromkeys(n for _,n in e["names"] if n!=name))))
cnt=lambda s: sum(r["stage"]==s for r in rows)
own=sum(bool(r["owner"]) for r in rows); web=sum(bool(r["web"] or r["phone"]) for r in rows)
cols=[("stage","Stage"),("name","Business"),("street","Address"),("hood","Neighborhood"),("what","What changed"),("latest","Latest signal"),("web","Website"),("phone","Phone"),("reviews","Google reviews"),("owner","Owner or manager (MN Secretary of State)"),("entity","Business entity"),("filed","Entity filed"),("liquor","New liquor license"),("firstinsp","First health inspection"),("permit","Permit #"),("pdesc","Permit description"),("by","Contractor"),("also","Other names at this address"),("sosurl","State filing link")]
ord_js=json.dumps({s:i for i,s in enumerate(ORDER)})
cfg="""{chipKey:"stage",chipOrder:%s,river:%s,home:null,
 stats:[["%d","Minneapolis food and drink businesses changing right now"],["%d","opening soon"],["%d","with an owner or manager on the state filing"]],
 legend:[["var(--hot)","Opening soon"],["var(--accent)","Just opened"],["var(--lic)","New license at a known place"],["var(--done)","Remodeling or expanding"]],
 color:r=>({"Opening soon":"var(--hot)","Just opened":"var(--accent)","New license":"var(--lic)"})[r.stage]||"var(--done)",
 tag:r=>`<span class="tag ${r.stage==="Opening soon"?"hot":""}">${r.stage}</span>`,
 meta:r=>[r.name?r.street:"",r.hood,r.owner?("Owner: "+r.owner):(r.entity?("Entity: "+r.entity):""),r.filed?("Filed "+r.filed):"",r.phone,r.latest?("Latest "+fmt(r.latest)):""],
 links:r=>{const L=[];if(r.web)L.push(`<a href="${esc(r.web)}" rel="noopener" target="_blank">Website</a>`);if(r.maps)L.push(`<a href="${esc(r.maps)}" rel="noopener" target="_blank">Google</a>`);if(r.sosurl)L.push(`<a href="${esc(r.sosurl)}" rel="noopener" target="_blank">State filing</a>`);return L.length?`<span class="m lk">${L.join("")}</span>`:""},
 sorts:{stage:r=>{const O=%s;return r.sort((a,b)=>(O[a.stage]-O[b.stage])||(a.rk-b.rk)||b.latest.localeCompare(a.latest))},newest:r=>r.sort((a,b)=>b.latest.localeCompare(a.latest)),hood:r=>r.sort((a,b)=>a.hood.localeCompare(b.hood))},
 cols:%s}"""%(json.dumps(ORDER),json.dumps(RIVER),len(rows),cnt("Opening soon"),own,ord_js,json.dumps(cols))
LIGHT='--bg:#f3f4f2;--panel:#e7e9e5;--ink:#15201c;--ink2:#33403b;--muted:#64706b;--rule:#d0d6d2;--accent:#1f5c8a;--onaccent:#f3f4f2;--hot:#c4512a;--lic:#7a4a9a;--done:#8d9692;--ghost:#c4cac6;--water:#8fadc0;--tagbg:#e2e6e3;--tagfg:#46524d;--hotbg:#f4dcd1;--hotfg:#8e3313;--display:"Fraunces",Georgia,serif;--body:"Inter Tight",system-ui,sans-serif;--h1w:600;'
DARK='--bg:#111614;--panel:#18201d;--ink:#e6ece9;--ink2:#c0cac5;--muted:#8a9690;--rule:#27322e;--accent:#79b3e0;--onaccent:#111614;--hot:#ee8c66;--lic:#c39be0;--done:#6a7571;--ghost:#2a3430;--water:#3d6176;--tagbg:#1f2925;--tagfg:#adbab4;--hotbg:#45251a;--hotfg:#f6b9a1;'
LEDE=(f"You said the question isn't who pulled a restaurant permit. It's which local hospitality businesses are changing right now. "
 f"So this joins every signal Minneapolis publishes. A build-out permit, a brand-new liquor license, a kitchen's first-ever health inspection. Then it adds the website, phone and owner from Google and the Secretary of State. "
 f"<b>{cnt('Opening soon')} are opening soon</b>, {cnt('Just opened')} just opened, and {cnt('New license')} took out a new liquor or food license, which is how a new owner or a new concept shows up.")
NOTE=("<p>Sources, all public: the City of Minneapolis building permit register (pulled Oct 4, 2026), its on-sale liquor license list (updated Sep 22) and its food inspection records (through Sep 29); Google Maps listings; and business filings at the Minnesota Secretary of State. Pulled Oct 5, 2026.</p>"
 f"<p>How each signal is read. A new liquor license is one whose number is among the newest the city has issued; license numbers run in sequence. A first health inspection means the kitchen had no inspection on record since January 2024, and only visits since July 1 are counted. A Google listing with five reviews or fewer usually means the doors just opened or are about to. The owner is the manager or chief executive on the state filing for the business name the city or Google uses. When no exact match came back, the field is blank.</p>"
 "<p>Minneapolis only. Food trucks, school and care-center kitchens are left out. Hiring and press coverage are not in here yet.</p>"
 "<p>Free, from Aidan Jude at Brick &amp; Mortar (aidan@brickandmortar.dev). Nothing to sign up for.</p>")
SORTS='<option value="stage">Closest to opening</option><option value="newest">Newest signal first</option><option value="hood">By neighborhood</option>'
CSVN="hospitality-changes.csv"
T=T.replace(".toast{",".lk{gap:4px 14px}.lk a{color:var(--accent);font-weight:600;text-decoration:none}.lk a:hover{text-decoration:underline}.toast{")
import builtins
h=T
for k,v in {"__TITLE__":"Changing Hands, Opening Doors","__CSV__":CSVN,"__FONTS__":"family=Fraunces:opsz,wght@9..144,600&family=Inter+Tight:wght@400;500;600","__LIGHT__":LIGHT,"__DARK__":DARK,
  "__EYEBROW__":"Made for Blue Vector Bookkeeping · Minneapolis public records · updated Oct 5, 2026","__H1__":f"{len(rows)} Minneapolis restaurants and bars in the middle of a change",
  "__LEDE__":LEDE,"__SORTS__":SORTS,"__NOTE__":NOTE}.items(): h=h.replace(k,v)
h=h.replace("__CFG__",cfg).replace("__ROWS__",js_json(rows))
head,body=h.split('<div class="wrap">',1)
open(f"{OUT}/index.html","w").write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex"><script defer src="/_vercel/insights/script.js"></script>{_READER}{head}</head><body><div class="wrap">{body}</body></html>')
with open(f"{OUT}/{CSVN}","w",newline="") as fh:
    w=csv.writer(fh); w.writerow([c[1] for c in cols]); [w.writerow([r.get(c[0],"") for c in cols]) for r in rows]
print("rows",len(rows),{s:cnt(s) for s in ORDER},"owner",own,"web/phone",web)
