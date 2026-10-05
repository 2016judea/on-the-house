"""Hospitality change events, Minneapolis. Pull + merge + enrich (Joel Oine / Blue Vector ask, 2026-10-05).
Signals: restaurant build-out permits (the 51 rows of /for/d9143508/), NEW on-sale liquor licenses
(license numbers are sequential; > NEWLIC = newest), first-ever health inspection since 2026-07-01.
Enrichment: Google Places Text Search (cached), MN Secretary of State (cached). Writes hospitality.json."""
import json, urllib.request, urllib.parse, datetime as dt, re, os, time, html, csv, collections
B="https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services"
NEWLIC=420000; SINCE=dt.date(2026,7,1)
def q(svc, where, fields="*"):
    out=[];off=0
    while True:
        p=dict(where=where,outFields=fields,f="json",resultOffset=off,resultRecordCount=2000,returnGeometry="false")
        d=json.load(urllib.request.urlopen(urllib.request.Request(f"{B}/{svc}/FeatureServer/0/query",data=urllib.parse.urlencode(p).encode())))
        fs=[f["attributes"] for f in d.get("features",[])]; out+=fs
        if not d.get("exceededTransferLimit") or not fs: break
        off+=len(fs)
    return out
D=lambda ms: dt.datetime.utcfromtimestamp(int(ms)/1000).date() if ms not in (None,"None","") else None
SUF={"AVENUE":"AVE","STREET":"ST","ROAD":"RD","BOULEVARD":"BLVD","PARKWAY":"PKWY","DRIVE":"DR","PLACE":"PL","LANE":"LN"}
def key(a):
    a=re.sub(r"\s*#.*$","",(a or "").upper()).replace(".","")
    a=re.sub(r",.*$","",a); t=[SUF.get(x,x) for x in a.split()]
    return " ".join(t[:4])
def title(a):
    a=re.sub(r"\s*#.*$","",a or ""); out=[]
    for w in a.split():
        out.append(w if re.fullmatch(r"(N|S|E|W|NE|SE|NW|SW)",w.upper()) and len(w)<=2 and w.isupper() else (w.upper() if w.upper() in("NE","SE","NW","SW") else w.capitalize()))
    return " ".join(out).replace("Nw","NW")
E={}
def ev(k):
    if not k: k="?"
    return E.setdefault(k,dict(key=k,addr=None,hood="",lat=None,lon=None,names=[],sig=[],permit=None,liq=[],food=[],inst=False))
# --- 1 permits (the 51 rows already sent, Oct 4 pull; re-joined to parcel coords 10/05)
J=json.load(open("join.json"))
NAMEFIX={"Bellcour":"Bellecour"}  # permit typo; Gavin Kaysen's Bellecour, Wells Fargo Center (Star Tribune, 2026)
for r in J["rows"]:
    p=J["bypn"].get(r["Permit #"],{});
    if not p.get("Latitude"): continue
    e=ev(key(p["Display"])); e["addr"]=e["addr"] or title(p["Display"]); e["hood"]=r["Neighborhood"]; e["lat"],e["lon"]=p["Latitude"],p["Longitude"]
    m=re.search(r" - ([^-]+?)\s*$",r["Permit description"]); nm=r["Name on the permit (when it gives one)"] or (m.group(1).strip() if m and not re.search(r"floor|level|^(restaurant|cafe|bar|coffee shop|bakery)$",m.group(1).strip(),re.I) else "")
    nm=NAMEFIX.get(nm,nm)
    if nm: e["names"].append(("permit",nm))
    pr=dict(stage=r["Stage"],kind=r["What the permit is"],what=r["Permit description"],by=r["Contractor"],issued=r["Permit issued"],done=r["Finished"],permit=r["Permit #"])
    rank={"Final inspection":0,"Under construction":1,"Just opened":2}
    if not e["permit"] or rank[pr["stage"]]<rank[e["permit"]["stage"]] or (pr["kind"]=="New restaurant or bar opening" and e["permit"]["kind"]!=pr["kind"]): e["permit"]=pr
# --- 2 new liquor licenses citywide
for l in {l["licenseNumber"]:l for l in q("On_Sale_Liquor","1=1")}.values():
    if int(l["licenseNumber"][3:])<=NEWLIC or not l["address"]: continue
    e=ev(key(l["address"])); e["addr"]=e["addr"] or title(l["address"]); e["hood"]=e["hood"] or (l["neighborhood"] or "").title()
    if e["lat"] is None: e["lat"],e["lon"]=l["lat"],l["long"]
    e["liq"].append(dict(name=l["licenseName"],num=l["licenseNumber"],status=l["licenseStatus"],date=str(D(l["issueDate"]) or ""),type=l["licenseType"]))
    e["names"].append(("liquor",l["licenseName"]))
# --- 3 first-ever health inspection since SINCE (no inspection 2024-01-01 .. SINCE)
food=q("Food_Inspections","YearOfInspection>=2024","HealthFacilityIDNumber,BusinessName,FacilityCategory,DateOfInspection,FullAddress,Neighborhood,Latitude,Longitude")
first={}
for f in food:
    d=D(f["DateOfInspection"]); k=f["HealthFacilityIDNumber"]
    if k not in first or d<first[k][0]: first[k]=(d,f)
for d,f in first.values():
    if d<SINCE or f["FacilityCategory"] not in("RESTAURANT","FOOD TRUCK","FOOD CART"): continue
    if f["FacilityCategory"]!="RESTAURANT": continue
    if re.search(r"child ?care|daycare|day care|school|senior|academy|church|hospital|clinic|head start",f["BusinessName"],re.I): continue   # trucks/carts have no street address that means anything
    e=ev(key(f["FullAddress"])); e["addr"]=e["addr"] or title(f["FullAddress"]); e["hood"]=e["hood"] or (f["Neighborhood"] or "").title()
    if e["lat"] is None and f["Latitude"]: e["lat"],e["lon"]=f["Latitude"],f["Longitude"]
    e["food"].append(dict(name=f["BusinessName"].strip(),date=str(d)))
    e["names"].append(("food",f["BusinessName"].strip()))
# school / institution kitchens on permit rows: drop
for f in J["food"]:
    k=key(f["FullAddress"])
    if k in E and f["FacilityCategory"]=="INSTITUTION" and not E[k]["names"] and not E[k]["liq"]: E[k]["inst"]=True
# --- 4 Google Places Text Search, cached
KEY=[l.split("=",1)[1].strip().strip('"') for l in open(os.path.expanduser("~/Desktop/bricks/.env")) if l.startswith("GOOGLE_PLACES_API_KEY")][0]
GC=json.load(open("hosp_google.json")) if os.path.exists("hosp_google.json") else {}
F="places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.businessStatus,places.userRatingCount,places.googleMapsUri,places.primaryType"
def gsearch(text):
    if text in GC: return GC[text]
    body=dict(textQuery=text,maxResultCount=5,locationBias=dict(circle=dict(center=dict(latitude=44.97,longitude=-93.26),radius=20000.0)))
    r=urllib.request.Request("https://places.googleapis.com/v1/places:searchText",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","X-Goog-Api-Key":KEY,"X-Goog-FieldMask":F})
    try: GC[text]=json.load(urllib.request.urlopen(r)).get("places",[])
    except Exception as ex: GC[text]=[]
    return GC[text]
NB=json.load(open("places_nearby.json"))
FOODTYPES=re.compile(r"restaurant|cafe|coffee|bar|bakery|brewery|food|meal|pub|pizza|deli|diner|bistro",re.I)
def norm(s): return re.sub(r"[^a-z0-9]","",re.sub(r"\b(llc|inc|co|corp|the|restaurant|cafe|café|and|&)\b","",(s or "").lower()))
E.pop("?",None)
for e in E.values():
    num=e["key"].split()[0]
    best=[n for _,n in e["names"]]
    cands=[]
    for t in ([f"{best[0]}, {e['addr']}, Minneapolis MN"] if best else [])+[f"restaurant at {e['addr']}, Minneapolis MN"]:
        cands+=gsearch(t)
    for d,v in NB.items():
        if key(d)==e["key"] and isinstance(v,list): cands+=v
    for pl in cands:
        fa=pl.get("formattedAddress","")
        if not fa.startswith(num+" ") or pl.get("businessStatus")=="CLOSED_PERMANENTLY": continue
        if not FOODTYPES.search(pl.get("primaryType","") or "") and not (best and norm(pl["displayName"]["text"])[:6]==norm(best[0])[:6]): continue
        e.setdefault("g",[])
        if pl["displayName"]["text"] not in [x["name"] for x in e["g"]]:
            e["g"].append(dict(name=pl["displayName"]["text"],web=pl.get("websiteUri",""),phone=pl.get("nationalPhoneNumber",""),status=pl.get("businessStatus",""),reviews=pl.get("userRatingCount",0),maps=pl.get("googleMapsUri","")))
json.dump(GC,open("hosp_google.json","w"))
# pick one Google place: name match first, else fewest reviews (the new one at a busy address)
for e in E.values():
    g=e.get("g",[]); names=[n for _,n in e["names"]]
    m=[x for x in g if any(norm(x["name"])[:6] and norm(x["name"])[:6]==norm(n)[:6] for n in names)]
    # at a build-out the NEW tenant is the listing with the fewest reviews; the old one is the incumbent
    newbuild=bool(e["permit"] and e["permit"]["kind"]=="New restaurant or bar opening")
    pick=sorted(g,key=lambda x:x["reviews"])
    pick=[x for x in pick if "truck" not in x["name"].lower()]
    # a city name (liquor or health license) is the authority: Google only joins when its name agrees.
    # a permit-only row has no name, so the newest listing at the address stands in, if there is one.
    lst=m if (e["liq"] or e["food"]) else (pick if newbuild else (m or pick))
    e["gp"]=lst[0] if lst else None
    m=[x for x in m if x is e["gp"]]
    if e["gp"] and not m: e["names"].append(("google",e["gp"]["name"]))
# --- 5 MN Secretary of State, cached
SC=json.load(open("hosp_sos.json")) if os.path.exists("hosp_sos.json") else {}
UA={"User-Agent":"Mozilla/5.0"}
def get(u):
    time.sleep(0.6); return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode("utf-8","replace")
def text(h):
    h=re.sub(r"<script.*?</script>|<style.*?</style>","",h,flags=re.S); return [l.strip() for l in html.unescape(re.sub(r"<[^>]+>","\n",h)).split("\n") if l.strip()]
def sos(name):
    k=norm(name)
    if not k or len(k)<4: return None
    if name in SC: return SC[name]
    res=None
    try:
        s=re.sub(r"\b(LLC|L\.L\.C\.|INC\.?|CORP\.?)\b","",name,flags=re.I).strip(" ,.")
        h=get("https://mblsportal.sos.mn.gov/Business/BusinessSearch?"+urllib.parse.urlencode(dict(BusinessName=s,IncludePriorNames="False",Status="Active",Type="BeginsWith")))
        hits=[]
        for tr in h.split("<tr")[1:]:
            m=re.search(r'href="(/Business/SearchDetails\?filingGuid=[^"]+)"',tr)
            tl=text("<x"+tr)
            if m and tl and norm(tl[0])==k: hits.append((("Assumed" in tr) , m))
        hits.sort(key=lambda x:x[0])   # entities first, assumed names after
        for _,m in hits[:3]:
            t=text(get("https://mblsportal.sos.mn.gov"+html.unescape(m.group(1))))
            def after(label):
                return t[t.index(label)+1] if label in t else ""
            bn=after("Minnesota Business Name") or after("Business Name")
            if norm(bn)!=k: continue
            people=[]
            for lab in ("Manager","Chief Executive Officer","Name Holder","Applicant"):
                for i,x in enumerate(t):
                    if x==lab and i+1<len(t): people.append((lab,t[i+1]))
            res=dict(entity=bn,type=after("Business Type"),filed=after("Filing Date"),people=people[:3],url="https://mblsportal.sos.mn.gov"+html.unescape(m.group(1)))
            break
    except Exception as ex: res=None
    SC[name]=res; json.dump(SC,open("hosp_sos.json","w"),indent=1); return res
for e in E.values():
    if e["inst"]: continue
    tried=set()
    for src,n in sorted(e["names"],key=lambda x:{"food":0,"liquor":1,"permit":2,"google":3}[x[0]]):
        if n in tried: continue
        tried.add(n); r=sos(n)
        if r:
            e["sos"]=r
            # an assumed name's holder is the owning entity: look it up once for its manager
            hold=[p for l,p in r["people"] if l=="Name Holder"]
            if hold and not [1 for l,_ in r["people"] if l in("Manager","Chief Executive Officer")]:
                r2=sos(hold[0])
                if r2: e["sos2"]=r2
            break
json.dump(list(E.values()),open("hospitality.json","w"),indent=1,default=str)
print("events",len(E),"| permit",sum(bool(e["permit"]) for e in E.values()),"liq",sum(bool(e["liq"]) for e in E.values()),"food",sum(bool(e["food"]) for e in E.values()),
      "| google",sum(bool(e.get("gp")) for e in E.values()),"sos",sum(bool(e.get("sos")) for e in E.values()),"inst",sum(e["inst"] for e in E.values()))
