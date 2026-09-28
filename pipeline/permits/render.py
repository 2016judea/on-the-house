import json,statistics,collections
T=open("template.html").read()
RIVER=[[45.052,-93.2885],[45.03,-93.2805],[45.012,-93.2745],[44.998,-93.2685],[44.988,-93.2625],[44.9815,-93.2575],[44.977,-93.2475],[44.972,-93.2385],[44.967,-93.2295],[44.962,-93.2225],[44.953,-93.2065],[44.946,-93.2005],[44.935,-93.2005],[44.917,-93.2035],[44.905,-93.1995],[44.889,-93.1935]]
def page(out,cfg,rows,subs):
    h=T
    for k,v in subs.items(): h=h.replace(k,v)
    h=h.replace("__CFG__",cfg).replace("__ROWS__",json.dumps(rows,separators=(",",":")))
    head,body=h.split('<div class="wrap">',1)
    doc=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex"><script defer src="/_vercel/insights/script.js"></script>{head}</head><body><div class="wrap">{body}</body></html>'
    open(out,"w").write(doc)
# ---------------- Vineland
v=json.load(open("vineland.json"))
DIG={"New house","Teardown","Garage","Pool","Retaining wall","Ground-floor addition"}
for r in v: r["g"]="Digging" if r["type"] in DIG else "Lighter work"
n=len(v); live=sum(r["status"]!="Finished" for r in v); near=sum(r["mi"]<=2 for r in v); dig=sum(r["g"]=="Digging" for r in v)
vcfg="""{chipKey:"type",chipOrder:["New house","Teardown","Garage","Pool","Retaining wall","Ground-floor addition","Deck or porch","Upper-floor addition","Outbuilding"],
river:%s,home:{lat:44.957227,lon:-93.236327,label:"Vineland",inMap:true},
stats:[["%d","homes with outdoor work permitted since March"],["%d","still under construction"],["%d","within 2 miles of your yard on 25th Ave"]],
legend:[["var(--bark)","Digging: new house, teardown, garage, pool, wall, addition"],["var(--moss)","Lighter: deck, porch, upper floor"]],
color:r=>r.g==="Digging"?"var(--bark)":"var(--moss)",
tag:r=>`<span class="tag ${r.status!=="Finished"?"hot":""}">${r.status==="Finished"?"Finished":"Under way"}</span>`,
meta:r=>[r.type,r.hood,"Permit "+fmt(r.issued),r.by?("Builder: "+r.by):"",r.mi+" mi from you"],
sorts:{newest:r=>r.sort((a,b)=>b.issued.localeCompare(a.issued)),near:r=>r.sort((a,b)=>a.mi-b.mi),hood:r=>r.sort((a,b)=>a.hood.localeCompare(b.hood)||b.issued.localeCompare(a.issued))},
cols:[["issued","Permit issued"],["addr","Address"],["hood","Neighborhood"],["type","Work"],["status","Status"],["what","Permit description"],["by","Builder"],["mi","Miles from Vineland"],["permit","Permit #"]]}"""%(json.dumps(RIVER),n,live,near)
LIGHT_V='--bg:#f2f4ec;--panel:#e8ecdf;--ink:#1d261c;--ink2:#374235;--muted:#66705f;--rule:#cfd6c3;--accent:#3d6b35;--onaccent:#f2f4ec;--bark:#8a5a2b;--moss:#5f8f4e;--ghost:#b9c1ad;--water:#7fa6b8;--tagbg:#e0e5d5;--tagfg:#4d5747;--hotbg:#f0dcc4;--hotfg:#7a4a1c;--display:"Alegreya",Georgia,serif;--body:"Alegreya Sans",system-ui,sans-serif;--h1w:700;'
DARK_V='--bg:#151a14;--panel:#1c231b;--ink:#e6ebdf;--ink2:#c3cbb9;--muted:#8f9985;--rule:#2f392d;--accent:#8cc27a;--onaccent:#10150f;--bark:#d59a5c;--moss:#8cc27a;--ghost:#3a4436;--water:#4b7486;--tagbg:#263024;--tagfg:#b3bda9;--hotbg:#3d2c1a;--hotfg:#f0c08a;'
page("vineland.html",vcfg,v,{"__TITLE__":"Yards Under Construction","__CSV__":"vineland-yards.csv","__FONTS__":"family=Alegreya:wght@500;700&family=Alegreya+Sans:wght@400;500;700",
 "__LIGHT__":LIGHT_V,"__DARK__":DARK_V,
 "__EYEBROW__":"Made for Vineland Tree · Minneapolis building permits · updated Sep 28, 2026",
 "__H1__":f"{n} Minneapolis yards with construction in them this year",
 "__LEDE__":f"Your fall newsletter named construction as a main cause of soil compaction around Minnesota trees. These are the Minneapolis homes that pulled a permit to dig, pour or build outside since March 1. <b>Work is still going at {live} of them</b>, so some trees can still be protected before the damage is done.",
 "__SORTS__":'<option value="newest">Newest permit first</option><option value="near">Closest to Vineland</option><option value="hood">By neighborhood</option>',
 "__NOTE__":"<p>Source: the City of Minneapolis building permit register, pulled Sep 28, 2026. It covers residential permits for new houses, additions, garages and other outbuildings, pools, retaining walls, decks and porches, plus house teardowns. Interior-only work is left out.</p><p>Minneapolis only. Saint Paul stopped publishing its permit register in mid-2025. Homeowner names are left out. The builder is shown when the permit names a company.</p><p>Free, from Aidan Jude at Brick &amp; Mortar (aidan@brickandmortar.dev). Nothing to sign up for.</p>"})
# ---------------- AOC
a=json.load(open("aoc.json"))
fin=sum(r["stage"]=="Final inspection" for r in a); uc=sum(r["stage"]=="Under construction" for r in a); jf=sum(r["stage"]=="Just finished" for r in a)
builders=collections.Counter(r["by"] for r in a if r["by"] and r["stage"]!="Just finished")
nb=len(builders)
acfg="""{chipKey:"stage",chipOrder:["Final inspection","Under construction","Just finished"],
river:%s,home:{label:"Your Bloomington office is about 9 miles south of this map",inMap:false},
stats:[["%d","at final inspection now"],["%d","under construction"],["%d","finished since July 1"]],
legend:[["var(--hot)","Final inspection"],["var(--accent)","Under construction"],["var(--done)","Finished since July 1"]],
color:r=>r.stage==="Final inspection"?"var(--hot)":r.stage==="Under construction"?"var(--accent)":"var(--done)",
tag:r=>`<span class="tag ${r.stage==="Final inspection"?"hot":""}">${r.stage}</span>`,
meta:r=>[r.type,r.hood,r.by?("GC: "+r.by):"",r.done?("Finished "+fmt(r.done)):("Permit "+fmt(r.issued)),"Permit fee $"+r.fees.toLocaleString(),r.mi+" mi from you"],
sorts:{stage:r=>r.sort((a,b)=>({"Final inspection":0,"Under construction":1,"Just finished":2}[a.stage]-{"Final inspection":0,"Under construction":1,"Just finished":2}[b.stage])||b.fees-a.fees),size:r=>r.sort((a,b)=>b.fees-a.fees),builder:r=>r.sort((a,b)=>(a.by||"~").localeCompare(b.by||"~")||b.fees-a.fees),near:r=>r.sort((a,b)=>a.mi-b.mi)},
cols:[["stage","Stage"],["addr","Address"],["hood","Neighborhood"],["type","Work"],["what","Permit description"],["by","General contractor"],["issued","Permit issued"],["done","Finished"],["fees","Permit fee ($)"],["co","Certificate of occupancy required"],["mi","Miles from AOC"],["permit","Permit #"]]}"""%(json.dumps(RIVER),fin,uc,jf)
LIGHT_A='--bg:#f7f8fa;--panel:#eef1f5;--ink:#131c26;--ink2:#34404d;--muted:#65707d;--rule:#d5dbe3;--accent:#0f6f7a;--onaccent:#f7f8fa;--hot:#c2701a;--done:#8b96a3;--ghost:#c6cdd6;--water:#8fb2c8;--tagbg:#e3e8ee;--tagfg:#44505d;--hotbg:#f6e3cc;--hotfg:#8a4b0c;--display:"Archivo",system-ui,sans-serif;--body:"Archivo",system-ui,sans-serif;--h1w:800;'
DARK_A='--bg:#0f141a;--panel:#161d25;--ink:#e7ecf2;--ink2:#c0c9d3;--muted:#8a95a2;--rule:#27313c;--accent:#4fb6c1;--onaccent:#0b1015;--hot:#f0a04e;--done:#6d7885;--ghost:#2c3642;--water:#3f6479;--tagbg:#1e2731;--tagfg:#aab4bf;--hotbg:#3a2814;--hotfg:#f5c28a;'
top=", ".join(f"{b} ({c})" for b,c in builders.most_common(4))
page("aoc.html",acfg,a,{"__TITLE__":"Spaces Near Handover","__CSV__":"aoc-spaces.csv","__FONTS__":"family=Archivo:wght@400;500;600;800",
 "__LIGHT__":LIGHT_A,"__DARK__":DARK_A,
 "__EYEBROW__":"Made for AOC Building Solutions · Minneapolis building permits · updated Sep 28, 2026",
 "__H1__":f"{len(a)} Minneapolis commercial spaces headed for a final clean",
 "__LEDE__":f"Your site offers post-construction cleanup and the turnover clean before occupancy. These are the Minneapolis tenant build-outs, remodels and new buildings at or near that point. <b>{fin} are at final inspection right now.</b> Most permits name the general contractor, and {nb} different GCs are running the open jobs. The busiest are {top}.",
 "__SORTS__":'<option value="stage">Closest to handover</option><option value="size">Biggest jobs first</option><option value="builder">By general contractor</option><option value="near">Closest to your office</option>',
 "__NOTE__":"<p>Source: the City of Minneapolis building permit register, pulled Sep 28, 2026. It covers commercial remodels, tenant improvements, additions and new buildings issued since March 1, plus any finished since July 1. Roofs, windows, solar, signs, parking and damage repairs are left out.</p><p>The permit fee is what the city charged. It rises with the value of the job, so it ranks size, but it is not the job's cost. Minneapolis does not publish project values.</p><p>Free, from Aidan Jude at Brick &amp; Mortar (aidan@brickandmortar.dev). Nothing to sign up for.</p>"})
print(n,live,near,dig,"|",len(a),fin,uc,jf,nb,top)
