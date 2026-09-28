import json,re,csv,collections,datetime as dt
exec(open("build.py").read().split("# ---------- Vineland")[0])   # reuse D, miles, what, title, contractor
r=json.load(open("raw2.json")); yb=json.load(open("yb.json"))
def yr(x):
    v=yb.get(x["APN"] or "",[None])[0]
    try: v=int(v); return v if 1800<v<2030 else None
    except: return None
def base(x,home):
    return dict(addr=title(x["Display"]),hood=x["Neighborhoods_Desc"] or "",issued=D(x["issueDate"]),done=D(x["completeDate"]),
        what=what(x["comments"]),by=contractor(x["applicantName"]),permit=x["permitNumber"],fees=round(x["totalFees"] or 0),
        built=yr(x),lat=round(x["Latitude"],5),lon=round(x["Longitude"],5),mi=miles(*home,x["Latitude"],x["Longitude"]) if home else None)
def dedupe(xs):
    seen=set();out=[]
    for x in xs:
        k=(x["Display"],(x["comments"] or "")[:80])
        if k in seen or x["status"] in("Cancelled","Expired") or x["Latitude"] is None: continue
        seen.add(k);out.append(x)
    return out
COMM=[x for x in r["commercial"] if x["occupancyType"] in("Comm","Mixed")]
NOTRES=re.compile(r"-unit \d|unit \d+\b.*kitchen|condo|apartment|dwelling|\bdu\b|residential unit",re.I)
EXCL=re.compile(r"water damage|fire damage|vehicle damage|repair|roof|solar|window|parking|sign\b|signage|fire barrier|sprinkler|stair|elevator|balcon|facade|masonry|not a building permit|hospital",re.I)
out={}
# 1 Architectural Antiques: teardowns
H=(45.001441,-93.251299); rows=[]
for x in dedupe(r["wreck"]):
    b=base(x,H); o=x["occupancyType"]
    b["type"]="House" if o=="SFD" else "Duplex or small apartment" if o in("TFD","3to4","MFD") else "Commercial building"
    b["stage"]="Permit open" if x["status"]=="Issued" else "Wrecked"
    b["era"]="Before 1940" if b["built"] and b["built"]<1940 else "1940 or later" if b["built"] else "Year unknown"
    rows.append(b)
rows.sort(key=lambda b:(b["stage"]!="Permit open",b["built"] or 9999))
out["archantiques"]=rows
# 2 Dusty Signs: storefronts opening
SF=re.compile(r"restaurant|cafe|café|coffee|\bbar\b|brewery|taproom|bakery|pizza|tavern|pub\b|retail|\bstore\b|\bshop\b|boutique|salon|\bspa\b|barber|grocery|market\b|dispensary|cannabis|mercantile|gallery|studio|gym|fitness|yoga|clinic|dental|showroom|ice cream|bookstore|florist|tattoo|nail",re.I)
KIND=[("Food and drink",r"restaurant|cafe|café|coffee|\bbar\b|brewery|taproom|bakery|pizza|tavern|pub\b|ice cream|dining|kitchen"),("Cannabis",r"dispensary|cannabis"),("Salon, spa or barber",r"salon|\bspa\b|barber|nail|tattoo"),("Fitness",r"gym|fitness|yoga|studio.*(dance|pilates)|climbing"),("Shop",r"retail|\bstore\b|\bshop\b|boutique|grocery|market\b|mercantile|showroom|gallery|florist|bookstore"),("Clinic",r"clinic|dental|medical|therapy")]
def kind(c):
    for k,p in KIND:
        if re.search(p,c,re.I): return k
    return "Other storefront"
NAME=re.compile(r"(?:tenant improvement|t/i|ti|build[- ]?out|remodel|new)[^-–:]*[-–:]\s*(?:suite \w+\s*[-–:]\s*)?([A-Z][\w'&. ]{2,40})",re.I)
def tenant(c):
    m=re.search(r"(?:suite|ste\.?)\s*\w+\s*[-–:,]\s*([A-Z][\w'&.]+(?: [A-Z&][\w'&.]*){0,4})",c or "")
    if m and not re.match(r"(?i)const|certificate|occupancy|remodel|tenant",m.group(1)): return m.group(1).strip(" .")
    m=re.search(r"T/I\s*-\s*([A-Z][\w'&.]+(?: [A-Z&][\w'&.]*){0,4})",c or "")
    if m: return title(m.group(1)).strip(" .")
    m=re.search(r"(?:Facility|Improvement|build ?out)\s*-\s*([A-Z][\w'&.]+(?: [A-Z&][\w'&.]*){0,4})",c or "")
    if m and not re.match(r"(?i)suite|const|certificate|occupancy",m.group(1)): return m.group(1).strip(" .")
    return ""
rows=[]
for x in dedupe(COMM):
    c=x["comments"] or ""
    if x["workType"] not in("Remodel","New","Addition") or not SF.search(c) or EXCL.search(c) or NOTRES.search(c): continue
    if re.search(r"bleacher|manufactur|cultivation|processing|basement|level \d|police|classroom|school|hospital|banquet|corporate|t/i - \d",c,re.I): continue
    if x["status"]=="Closed" and D(x["completeDate"])<"2026-05-01": continue
    b=base(x,None); b["type"]=kind(c); b["name"]=""
    b["stage"]="Just opened" if x["status"]=="Closed" else "Final inspection" if x["milestone"]=="Final Inspection" else "Under construction"
    rows.append(b)
o={"Final inspection":0,"Under construction":1,"Just opened":2}; rows.sort(key=lambda b:(o[b["stage"]],b["issued"]),reverse=False)
out["dustysigns"]=rows
# 3 ASF: retail build-outs
H=(45.030171,-93.260088); RET=re.compile(r"retail|\bstore\b|\bshop\b|boutique|pharmacy|grocery|market\b|mercantile|showroom|dispensary|cannabis|convenience|gallery|florist|bookstore|thrift",re.I)
rows=[]
for x in dedupe(COMM):
    c=x["comments"] or ""
    if x["workType"] not in("Remodel","New","Addition") or not RET.search(c) or EXCL.search(c) or NOTRES.search(c) or re.search(r"repair shop|bed repair|manufactur|cultivation|coffee shop|restaurant",c,re.I): continue
    if x["status"]=="Closed" and D(x["completeDate"])<"2026-06-01": continue
    b=base(x,H); cl=c.lower()
    b["type"]="Cannabis" if re.search("dispensar|cannabis",cl) else "Grocery or convenience" if re.search("grocery|convenience|market",cl) else "Gallery or showroom" if re.search("gallery|showroom",cl) else "Shop"
    b["name"]=""
    b["stage"]="Just opened" if x["status"]=="Closed" else "Final inspection" if x["milestone"]=="Final Inspection" else "Under construction"
    rows.append(b)
rows.sort(key=lambda b:(o[b["stage"]],-b["fees"]))
out["asf"]=rows
# 4 Palen: kitchens
H=(44.988803,-93.28559); FOOD=re.compile(r"restaurant|commercial kitchen|cafe|café|coffee|\bbar\b|brewery|taproom|bakery|pizza|grill|\bhood\b|commissary|deli\b|dining|cafeteria|food|tavern|pub\b|taqueria|distillery|ice cream|kitchen",re.I)
rows=[]
for x in dedupe(COMM+r["mech"]):
    c=x["comments"] or ""
    if not FOOD.search(c) or NOTRES.search(c) or re.search(r"fire damage|water damage|kitchen fire|nail salon|drinking establishment\. remodel kitchen and 3/4",c,re.I): continue
    if x["permitType"]=="Commercial" and x["workType"] not in("Remodel","New","Addition"): continue
    if x["permitType"]=="Mechanical" and (not re.search(r"hood|commercial kitchen|restaurant|food",c,re.I) or re.search(r"no kitchen hoods|under 250 cfm|furnace",c,re.I)): continue
    if re.search(r"plunge pool|banquet|classroom",c,re.I): continue
    if x["status"]=="Closed" and D(x["completeDate"])<"2026-06-01": continue
    cl=c.lower()
    if x["permitType"]=="Mechanical": t="Hood or kitchen ventilation"
    elif re.search(r"change of use.{0,4}restaurant|restaurant change of use|in ?to restaurant|to restaurant|restaurant tenant build ?out|new restaurant|new coffee|new cafe|new bakery|new brewery|new taproom|convert.*(restaurant|cafe|coffee)|for (a )?new|new .*kitchen",cl): t="New kitchen opening"
    elif re.search(r"addition|expan",cl): t="Expansion"
    else: t="Kitchen remodel"
    if re.search(r"convert existing (vacant )?restaurant|former restaurant|vacant restaurant",cl): t="Restaurant space changing use"
    b=base(x,H); b["type"]=t; b["name"]=""
    b["stage"]="Finished" if x["status"]=="Closed" else "Final inspection" if x["milestone"]=="Final Inspection" else "Under construction"
    rows.append(b)
o2={"Final inspection":0,"Under construction":1,"Finished":2}; rows.sort(key=lambda b:(o2[b["stage"]],-b["fees"]))
out["palen"]=rows
# 5 3 Bears: yards torn up by finished work
H=(44.933027,-93.225926); rows=[]
for x in dedupe(r["res"]+[w for w in r["wreck"] if w["occupancyType"] in("SFD","TFD")]):
    c=(x["comments"] or "").lower()
    fin=x["status"]=="Closed" or x["milestone"]=="Final Inspection"
    if not fin: continue
    if x["permitType"]=="Res" and re.search(r"2nd|second|story|dormer",c) and not re.search("foundation|basement|footing",c): continue
    t="Teardown" if x["permitType"]=="Wrecking" else "New house" if x["workType"]=="New" else "Retaining wall" if "retaining" in c else "Pool" if "pool" in c else "Garage" if ("garage" in c or x["workType"]=="Accessory") else "Deck or porch" if re.search("deck|porch|stoop",c) else "Addition"
    if t in("Deck or porch",): continue
    b=base(x,H); b["type"]=t
    b["stage"]="Final inspection" if x["milestone"]=="Final Inspection" and x["status"]!="Closed" else "Finished"
    b["done"]=b["done"] or ""
    rows.append(b)
rows.sort(key=lambda b:(b["done"] or b["issued"]),reverse=True)
out["3bears"]=rows
for k,v in out.items():
    print(k,len(v),collections.Counter(b["type"] for b in v).most_common(),collections.Counter(b["stage"] for b in v))
json.dump(out,open("five.json","w"))
