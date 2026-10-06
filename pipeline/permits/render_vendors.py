import json,csv,os
exec(open("render.py").read().split("# ---------------- Vineland")[0])
O=json.load(open("vendors.json"))
NOTE="<p>Source: Overture Maps places (release 2026-08-19, CDLA-Permissive-2.0), joined to county parcels across the seven-county Twin Cities metro by Brick &amp; Mortar. %s We loaded every website on Oct 6, 2026 and kept only the ones that answered.</p><p>A listing says a business exists at that address. It does not say how big the team is or whether they are buying, so read their site before you write.</p><p>Free, from Aidan Jude at Brick &amp; Mortar (aidan@brickandmortar.dev). Nothing to sign up for. The rest of the data is at brickandmortar.dev.</p>"
COLS=[("addr","Business"),("kind","Kind"),("what","Address"),("area","Area"),("web","Website"),("phone","Phone")]
def run(slug,key,csvname,title,eyebrow,h1,lede,fonts,light,dark,chips,stats,note):
    rows=O[key]
    cfg="""{chipKey:"kind",chipOrder:%s,river:%s,home:null,stats:%s,
 legend:%s,
 color:r=>r.kind===%s?"var(--accent)":"var(--hot)",
 tag:r=>`<span class="tag">${r.area}</span>`,
 meta:r=>[r.kind,r.web.replace(/^https?:\\/\\/(www\\.)?/i,"").replace(/\\/$/,""),r.phone],
 sorts:{name:r=>r.sort((a,b)=>a.addr.localeCompare(b.addr)),area:r=>r.sort((a,b)=>a.area.localeCompare(b.area)||a.addr.localeCompare(b.addr))},
 cols:%s}"""%(json.dumps(chips),json.dumps(RIVER),json.dumps(stats),json.dumps([["var(--accent)",chips[0]]]+([["var(--hot)",chips[1]]] if len(chips)>1 else [])),json.dumps(chips[0]),json.dumps(COLS))
    os.makedirs(f"out/{slug}",exist_ok=True)
    page(f"out/{slug}/index.html",cfg,rows,{"__TITLE__":title,"__CSV__":csvname,"__FONTS__":fonts,"__LIGHT__":light,"__DARK__":dark,"__EYEBROW__":eyebrow,"__H1__":h1,"__LEDE__":lede,"__SORTS__":'<option value="name">A to Z</option><option value="area">By area</option>',"__NOTE__":note})
    with open(f"out/{slug}/{csvname}","w",newline="") as f:
        w=csv.writer(f);w.writerow([c[1] for c in COLS]);[w.writerow([r[c[0]] for c in COLS]) for r in rows]
cnt=lambda rows,k,v:sum(r[k]==v for r in rows)
LIGHT='--bg:#f4f3ef;--panel:#e9e7e1;--ink:#1b1a17;--ink2:#3b3934;--muted:#6a675f;--rule:#d5d2ca;--accent:#2f5d50;--onaccent:#f4f3ef;--hot:#b4662a;--done:#8f8c84;--ghost:#c9c6bd;--water:#93aebb;--tagbg:#e4e1d9;--tagfg:#4b4842;--hotbg:#f1dfcd;--hotfg:#7e4416;--display:"Fraunces",Georgia,serif;--body:"Inter Tight",system-ui,sans-serif;--h1w:600;'
DARK='--bg:#151513;--panel:#1d1d1a;--ink:#ebe9e3;--ink2:#c7c4bc;--muted:#928f86;--rule:#302f2b;--accent:#7cc2ae;--onaccent:#151513;--hot:#e39a5e;--done:#6c6a63;--ghost:#33322e;--water:#3e6170;--tagbg:#262622;--tagfg:#b5b2a9;--hotbg:#432b17;--hotfg:#f2c49a;'
FONTS="family=Fraunces:opsz,wght@9..144,600&family=Inter+Tight:wght@400;500;600"
s=O["survhey"]; m=cnt(s,"kind","Market research")
run("survhey","survhey","research-teams.csv","Small Research Teams, Twin Cities","Made for Survhey · Twin Cities business listings · Oct 6, 2026",
 f"{len(s)} small research shops in the Twin Cities",
 f"You build questionnaires for small research teams. These are the independent research firms we can find in the Minneapolis–Saint Paul metro: <b>{m} market research shops</b> and {len(s)-m} evaluation and policy research groups, the kind that field surveys for clients and have to defend the numbers.",
 FONTS,LIGHT,DARK,["Market research","Evaluation and policy research"],[[str(len(s)),"research shops"],[str(m),"market research"],[str(len(s)-m),"evaluation and policy"]],
 NOTE%"Picked by hand from listings whose name and website say they do research for clients; medical and lab research is left out.")
t=O["treforge"]; sw=cnt(t,"kind","Software developer")
run("treforge","treforge","software-teams.csv","Lean Software Teams, Twin Cities","Made for Treforge · Twin Cities business listings · Oct 6, 2026",
 f"{len(t)} independent software and IT shops in the Twin Cities",
 f"You build MVPs and wire AI into business tools for software teams that can't hire fast enough. These are the independent software developers and IT companies listed in the Minneapolis–Saint Paul metro: <b>{sw} software developers</b> and {len(t)-sw} IT companies. No chains or franchises.",
 FONTS,LIGHT,DARK,["Software developer","IT company"],[[str(len(t)),"independent shops"],[str(sw),"software developers"],[str(cnt(t,'area','Minneapolis')),"in Minneapolis proper"]],
 NOTE%"Every listing filed as a software developer or IT company with no parent brand.")
b=O["bestlatech"]
run("bestlatech","bestlatech","product-teams.csv","Small Product Teams, Twin Cities","Made for BestlaTech · Twin Cities business listings · Oct 6, 2026",
 f"{len(b)} independent software developers in the Twin Cities",
 f"You put engineers on small US product teams. These are the independent software developers listed in the Minneapolis–Saint Paul metro, <b>{cnt(b,'area','Minneapolis')} in Minneapolis</b>, {cnt(b,'area','Saint Paul')} in Saint Paul and {cnt(b,'area','Suburbs')} in the suburbs. No chains or franchises.",
 FONTS,LIGHT,DARK,["Software developer"],[[str(len(b)),"software developers"],[str(cnt(b,'area','Minneapolis')),"in Minneapolis"],[str(cnt(b,'area','Suburbs')),"in the suburbs"]],
 NOTE%"Every listing filed as a software developer with no parent brand.")
for k in O: print(k,len(O[k]),{a:cnt(O[k],'area',a) for a in ['Minneapolis','Saint Paul','Suburbs']},{x:cnt(O[k],'kind',x) for x in set(r['kind'] for r in O[k])})
