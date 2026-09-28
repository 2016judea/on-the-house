import json,collections,csv
exec(open("render.py").read().split("# ---------------- Vineland")[0])
O=json.load(open("five.json"))
NOTE_SRC="<p>Source: the City of Minneapolis building permit register, pulled Sep 28, 2026. %s</p><p>Minneapolis only. Saint Paul stopped publishing its permit register in mid-2025. The contractor is shown when the permit names a company.</p><p>Free, from Aidan Jude at Brick &amp; Mortar (aidan@brickandmortar.dev). Nothing to sign up for.</p>"
def dark(d): return d
def run(slug,rows,csvname,cols,title,eyebrow,h1,lede,fonts,light,darkt,cfgjs,sorts,note):
    cfg=cfgjs.replace("__RIVER__",json.dumps(RIVER))
    page(f"{slug}.html",cfg,rows,{"__TITLE__":title,"__CSV__":csvname,"__FONTS__":fonts,"__LIGHT__":light,"__DARK__":darkt,"__EYEBROW__":eyebrow,"__H1__":h1,"__LEDE__":lede,"__SORTS__":sorts,"__NOTE__":note})
    with open(csvname,"w",newline="") as f:
        w=csv.writer(f);w.writerow([c[1] for c in cols]);[w.writerow([r.get(c[0],"") if r.get(c[0]) is not None else "" for c in cols]) for r in rows]
STAGESORT='r=>r.sort((a,b)=>(ORD[a.stage]-ORD[b.stage])||b.fees-a.fees)'
# ---- 1 Architectural Antiques
a=O["archantiques"]; op=[r for r in a if r["stage"]=="Permit open"]; old=[r for r in op if r["built"] and r["built"]<1940]
wc=len({r["by"] for r in op if r["by"]})
cols=[("stage","Status"),("addr","Address"),("hood","Neighborhood"),("type","Building"),("built","Year built"),("by","Wrecking contractor"),("issued","Permit issued"),("what","Permit description"),("mi","Miles from Architectural Antiques"),("permit","Permit #")]
run("archantiques",a,"teardowns.csv",cols,"Before the Excavator",
 "Made for Architectural Antiques · Minneapolis wrecking permits · updated Sep 28, 2026",
 f"{len(op)} Minneapolis buildings with a wrecking permit open right now",
 f"Every building that comes down takes its doors, hardware, mantels and light fixtures with it. These are the Minneapolis buildings that got a wrecking permit in the last twelve months. <b>At {len(op)} the permit is still open, and {len(old)} of those were built before 1940.</b> Most permits name the wrecking contractor, the person who decides what leaves the building before it comes down.",
 "family=Spectral:wght@500;700&family=Karla:wght@400;500;700",
 '--bg:#eef0ec;--panel:#e3e6e0;--ink:#1f1d1b;--ink2:#3f3b37;--muted:#6d6862;--rule:#cfd2ca;--accent:#6b2e2a;--onaccent:#f5f2ee;--old:#6b2e2a;--mid:#9a7b3c;--ghost:#bfc3ba;--water:#8aa6b4;--tagbg:#e2e4dd;--tagfg:#4a4640;--hotbg:#ecd6d2;--hotfg:#6b2e2a;--display:"Spectral",Georgia,serif;--body:"Karla",system-ui,sans-serif;--h1w:700;',
 '--bg:#171514;--panel:#201d1b;--ink:#ece6df;--ink2:#cbc3ba;--muted:#958c83;--rule:#35302c;--accent:#d98b7f;--onaccent:#171514;--old:#d98b7f;--mid:#c9a860;--ghost:#3d3834;--water:#44697a;--tagbg:#2a2522;--tagfg:#bdb3a8;--hotbg:#43241f;--hotfg:#f0b3a8;',
 """{chipKey:"type",chipOrder:["House","Duplex or small apartment","Commercial building"],river:__RIVER__,home:{lat:45.001441,lon:-93.251299,label:"You",inMap:true},
 stats:[["%d","wrecking permits still open"],["%d","of those built before 1940"],["%d","wrecking contractors on the open permits"]],
 legend:[["var(--old)","Built before 1940"],["var(--mid)","1940 or later"]],
 color:r=>r.built&&r.built<1940?"var(--old)":"var(--mid)",
 tag:r=>`<span class="tag ${r.stage==="Permit open"?"hot":""}">${r.stage}</span>`,
 meta:r=>[r.type,r.built?("Built "+r.built):"",r.hood,r.by?("Wrecker: "+r.by):"","Permit "+fmt(r.issued),r.mi+" mi from you"],
 sorts:{open:r=>r.sort((a,b)=>(a.stage!=="Permit open")-(b.stage!=="Permit open")||(a.built||9999)-(b.built||9999)),newest:r=>r.sort((a,b)=>b.issued.localeCompare(a.issued)),near:r=>r.sort((a,b)=>a.mi-b.mi),wrecker:r=>r.sort((a,b)=>(a.by||"~").localeCompare(b.by||"~"))},
 cols:%s}"""%(len(op),len(old),wc,json.dumps(cols)),
 '<option value="open">Open permits, oldest building first</option><option value="newest">Newest permit first</option><option value="near">Closest to you</option><option value="wrecker">By wrecking contractor</option>',
 NOTE_SRC%"It covers every wrecking permit issued since Sep 1, 2025. Year built comes from Hennepin County's parcel records. An open permit means the demolition is approved, not that the building is still standing, so drive by before you call.")
# ---- stage-based pages share a shape
def stagepage(slug,key,csvname,title,eyebrow,h1,lede,fonts,light,darkt,order,chips,home,notewhat,extra_stats,namecol=False):
    rows=O[key]
    cols=[("stage","Stage"),("addr","Address"),("hood","Neighborhood"),("type","Kind")]+([("name","Business name (when the permit gives one)")] if namecol else [])+[("what","Permit description"),("by","Contractor"),("issued","Permit issued"),("done","Finished"),("fees","Permit fee ($)")]+([("mi","Miles from you")] if home else [])+[("permit","Permit #")]
    ordjs=json.dumps({s:i for i,s in enumerate(order)})
    homejs=json.dumps({"lat":home[0],"lon":home[1],"label":"You","inMap":True}) if home else "null"
    cfg="""{chipKey:"type",chipOrder:%s,river:__RIVER__,home:%s,
 stats:%s,
 legend:[["var(--hot)","%s"],["var(--accent)","%s"],["var(--done)","%s"]],
 color:r=>r.stage===%s?"var(--hot)":r.stage===%s?"var(--accent)":"var(--done)",
 tag:r=>`<span class="tag ${r.stage===%s?"hot":""}">${r.stage}</span>`,
 meta:r=>[r.type,r.name?("Name on permit: "+r.name):"",r.hood,r.by?("Contractor: "+r.by):"",r.done?("Finished "+fmt(r.done)):("Permit "+fmt(r.issued)),r.mi!=null?(r.mi+" mi from you"):""],
 sorts:{stage:r=>{const O=%s;return r.sort((a,b)=>(O[a.stage]-O[b.stage])||b.fees-a.fees)},newest:r=>r.sort((a,b)=>b.issued.localeCompare(a.issued)),size:r=>r.sort((a,b)=>b.fees-a.fees)%s},
 cols:%s}"""%(json.dumps(chips),homejs,json.dumps(extra_stats),order[0],order[1],order[2],json.dumps(order[0]),json.dumps(order[1]),json.dumps(order[0]),ordjs,(",near:r=>r.sort((a,b)=>a.mi-b.mi)" if home else ""),json.dumps(cols))
    sorts='<option value="stage">Closest to opening</option><option value="newest">Newest permit first</option><option value="size">Biggest jobs first</option>'+('<option value="near">Closest to you</option>' if home else "")
    run(slug,rows,csvname,cols,title,eyebrow,h1,lede,fonts,light,darkt,cfg,sorts,NOTE_SRC%(notewhat+" The permit fee is what the city charged. It rises with the value of the job, so it ranks size, but it is not the job's cost."))
    return rows
cnt=lambda rows,s:sum(r["stage"]==s for r in rows)
# ---- 2 Dusty Signs
d=O["dustysigns"]; order=["Final inspection","Under construction","Just opened"]
stagepage("dustysigns","dustysigns","storefronts.csv","New Glass on the Block","Made for Dusty Signs · Minneapolis building permits · updated Sep 28, 2026",
 f"{len(d)} Minneapolis storefronts being built out this year",
 f"Every new storefront needs its name on the glass. These are the Minneapolis restaurants, cafes, shops, dispensaries, studios and clinics that pulled a permit to build out a street-level business this year. <b>{cnt(d,'Final inspection')} are at final inspection now</b>, the last step before the doors open. Another {cnt(d,'Under construction')} are still under construction.",
 "family=Yeseva+One&family=Work+Sans:wght@400;500;600",
 '--bg:#f3f4f7;--panel:#e8eaf0;--ink:#161a2b;--ink2:#353a4f;--muted:#666b7e;--rule:#d3d6df;--accent:#2d3a6b;--onaccent:#f3f4f7;--hot:#b8862b;--done:#8b90a1;--ghost:#c5c8d2;--water:#90a9c2;--tagbg:#e2e4ec;--tagfg:#474c60;--hotbg:#f2e4c6;--hotfg:#7a5510;--display:"Yeseva One",Georgia,serif;--body:"Work Sans",system-ui,sans-serif;--h1w:400;',
 '--bg:#11131d;--panel:#191c29;--ink:#e9eaf1;--ink2:#c3c6d4;--muted:#8d91a4;--rule:#2a2e40;--accent:#8fa2e6;--onaccent:#11131d;--hot:#e0b25a;--done:#6b7085;--ghost:#2d3143;--water:#3c5874;--tagbg:#212536;--tagfg:#b0b4c6;--hotbg:#3b2e14;--hotfg:#f0cd88;',
 order,["Food and drink","Shop","Cannabis","Salon, spa or barber","Fitness","Clinic","Other storefront"],None,
 "It covers commercial build-outs, remodels and new buildings issued since Jan 1, 2026 whose permit names a street-level use such as a restaurant, shop, salon or dispensary, plus any finished since May 1.",
 [[str(len(d)),"storefronts with a build-out permit"],[str(cnt(d,"Final inspection")),"at final inspection now"],[str(cnt(d,"Just opened")),"finished since May 1"]])
# ---- 3 ASF
s=O["asf"]; canna=sum(r["type"]=="Cannabis" for r in s)
stagepage("asf","asf","store-buildouts.csv","Dispensaries Being Fitted","Made for ASF Store Fixtures · Minneapolis building permits · updated Sep 28, 2026",
 f"{canna} Minneapolis cannabis stores being fitted out",
 f"Minnesota's dispensaries are opening one storefront at a time, and every one needs locking showcases, counters, shelving and a safe. These are the Minneapolis cannabis stores and other shops that pulled a permit to build out retail space this year. <b>{cnt(s,'Final inspection')} are at final inspection now</b> and {cnt(s,'Under construction')} are still under construction. Most name the builder doing the work.",
 "family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600",
 '--bg:#f5f5f3;--panel:#eaeae6;--ink:#1a1a18;--ink2:#3a3a36;--muted:#6b6b64;--rule:#d6d6d0;--accent:#2f4f6f;--onaccent:#f5f5f3;--hot:#c23a2b;--done:#8f8f88;--ghost:#c8c8c1;--water:#94aec2;--tagbg:#e6e6e0;--tagfg:#4a4a44;--hotbg:#f3d6d1;--hotfg:#8e2418;--display:"Barlow Condensed","Arial Narrow",sans-serif;--body:"Barlow",system-ui,sans-serif;--h1w:700;',
 '--bg:#141413;--panel:#1c1c1a;--ink:#ecece8;--ink2:#c8c8c2;--muted:#94948c;--rule:#30302c;--accent:#86a9cc;--onaccent:#141413;--hot:#ef7666;--done:#6e6e67;--ghost:#33332f;--water:#3e5f75;--tagbg:#242422;--tagfg:#b6b6ae;--hotbg:#45201a;--hotfg:#f7b0a6;',
 order,["Cannabis","Shop","Grocery or convenience"],(45.030171,-93.260088),
 "It covers commercial build-outs and remodels for retail use issued since Jan 1, 2026, plus any finished since June 1. Cannabis growing and manufacturing sites are left out.",
 [[str(canna),"cannabis stores with a build-out permit"],[str(cnt(s,"Final inspection")),"at final inspection now"],[str(len(s)),"retail build-outs in all"]])
# ---- 4 Palen
p=O["palen"]; order=["Final inspection","Under construction","Finished"]; newk=sum(r["type"]=="New kitchen opening" for r in p)
stagepage("palen","palen","kitchens.csv","Kitchens in Progress","Made for Jos. F. Palen Co. · Minneapolis building permits · updated Sep 28, 2026",
 f"{len(p)} Minneapolis restaurant kitchens being built or torn out",
 f"A new kitchen needs ranges, reach-ins and prep tables. A remodeled one sends working equipment out the back door. These are the Minneapolis restaurant, cafe and bakery build-outs, kitchen remodels and hood installs permitted this year. <b>{newk} are brand-new kitchens</b>, and {cnt(p,'Final inspection')} jobs are at final inspection now.",
 "family=Oswald:wght@500;600&family=Source+Sans+3:wght@400;600",
 '--bg:#f2f4f4;--panel:#e6eaea;--ink:#172020;--ink2:#344141;--muted:#637070;--rule:#d0d7d7;--accent:#1f6f5c;--onaccent:#f2f4f4;--hot:#b5471f;--done:#8c9696;--ghost:#c3caca;--water:#8fb0bf;--tagbg:#e1e6e6;--tagfg:#465252;--hotbg:#f1d9cd;--hotfg:#8a3212;--display:"Oswald","Arial Narrow",sans-serif;--body:"Source Sans 3",system-ui,sans-serif;--h1w:600;',
 '--bg:#101616;--panel:#172020;--ink:#e6eeee;--ink2:#c0cccc;--muted:#8a9999;--rule:#283535;--accent:#63c2a8;--onaccent:#101616;--hot:#ec8a62;--done:#687676;--ghost:#2a3636;--water:#3b6070;--tagbg:#1e2929;--tagfg:#aebcbc;--hotbg:#40241a;--hotfg:#f4b69c;',
 order,["New kitchen opening","Kitchen remodel","Hood or kitchen ventilation","Expansion"],(44.988803,-93.28559),
 "It covers commercial permits issued since Jan 1, 2026 that mention a restaurant, cafe, bakery, bar or commercial kitchen, and mechanical permits for kitchen hoods, plus any finished since June 1. Kitchens inside apartments and condos are left out.",
 [[str(len(p)),"kitchen jobs permitted this year"],[str(newk),"brand-new kitchens"],[str(cnt(p,"Final inspection")),"at final inspection now"]])
# ---- 5 3 Bears
b=O["3bears"]; near=sum(r["mi"]<=2 for r in b)
cols=[("stage","Stage"),("addr","Address"),("hood","Neighborhood"),("type","Work"),("done","Finished"),("issued","Permit issued"),("what","Permit description"),("by","Builder"),("mi","Miles from 3 Bears"),("permit","Permit #")]
run("3bears",b,"finished-yards.csv",cols,"Yards After the Build",
 "Made for 3 Bears Landscaping · Minneapolis building permits · updated Sep 28, 2026",
 f"{len(b)} Minneapolis yards where the construction just wrapped up",
 f"When a garage, addition, retaining wall or new house is finished, the yard around it is often torn up. These are the Minneapolis homes where that work finished or reached final inspection over the past year. <b>{near} are within two miles of you on Dight Ave.</b>",
 "family=Bitter:wght@600;700&family=Nunito+Sans:wght@400;600;700",
 '--bg:#f1f4ee;--panel:#e5eadf;--ink:#1b2416;--ink2:#374331;--muted:#65705e;--rule:#cfd8c6;--accent:#4a7c2a;--onaccent:#f1f4ee;--new:#a0522d;--wall:#4a7c2a;--ghost:#bec7b4;--water:#88a9b9;--tagbg:#e0e6d8;--tagfg:#4b5644;--hotbg:#dce9cf;--hotfg:#355c1c;--display:"Bitter",Georgia,serif;--body:"Nunito Sans",system-ui,sans-serif;--h1w:700;',
 '--bg:#131811;--panel:#1a2118;--ink:#e5ecdf;--ink2:#c1cbb8;--muted:#8d9884;--rule:#2c3627;--accent:#95c96d;--onaccent:#131811;--new:#df9468;--wall:#95c96d;--ghost:#313b2c;--water:#3e6475;--tagbg:#222a1f;--tagfg:#b0bba6;--hotbg:#27381c;--hotfg:#bfe39f;',
 """{chipKey:"type",chipOrder:["New house","Teardown","Addition","Garage","Retaining wall","Pool"],river:__RIVER__,home:{lat:44.933027,lon:-93.225926,label:"You",inMap:true},
 stats:[["%d","yards where work just finished"],["%d","within 2 miles of you"],["%d","new houses and teardowns"]],
 legend:[["var(--new)","New house, teardown or addition"],["var(--wall)","Garage, wall or pool"]],
 color:r=>["New house","Teardown","Addition"].includes(r.type)?"var(--new)":"var(--wall)",
 tag:r=>`<span class="tag ${r.stage==="Final inspection"?"hot":""}">${r.stage}</span>`,
 meta:r=>[r.type,r.hood,r.done?("Finished "+fmt(r.done)):("Permit "+fmt(r.issued)),r.by?("Builder: "+r.by):"",r.mi+" mi from you"],
 sorts:{recent:r=>r.sort((a,b)=>(b.done||b.issued).localeCompare(a.done||a.issued)),near:r=>r.sort((a,b)=>a.mi-b.mi),hood:r=>r.sort((a,b)=>a.hood.localeCompare(b.hood))},
 cols:%s}"""%(len(b),near,sum(r["type"] in("New house","Teardown") for r in b),json.dumps(cols)),
 '<option value="recent">Most recently finished</option><option value="near">Closest to you</option><option value="hood">By neighborhood</option>',
 NOTE_SRC%"It covers residential permits for new houses, additions, garages, retaining walls and pools, plus house teardowns, issued since Oct 1, 2025 and now closed or at final inspection. Decks, porches and upper-floor additions are left out because they rarely disturb the yard.")
for k,v in O.items(): print(k,len(v))
print("arch open",len(op),"old",len(old),"wreckers",wc,"| dusty",cnt(d,"Final inspection"),cnt(d,"Under construction"),"| asf",canna,cnt(s,"Final inspection"),cnt(s,"Under construction"),"| palen new",newk,cnt(p,"Final inspection"),"| bears near",near)
