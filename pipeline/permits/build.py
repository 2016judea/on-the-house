import json,re,csv,math,datetime as dt,collections
D=lambda x: dt.datetime.fromtimestamp(x/1000,dt.timezone.utc).date().isoformat() if x else ""
def miles(a,b,c,d):
    R=3958.8;p=math.radians
    h=math.sin(p(c-a)/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(p(d-b)/2)**2
    return round(2*R*math.asin(math.sqrt(h)),1)
CUT=re.compile(r"\s*(certificate of occupancy|const\.? type|building code|energy code|construction documents|special inspection|occupancy:|number of stories|2020 m[sn]bc|engineer:|architect:|sprinkler|shell permit|note:|\(maa\)|\(jjl\)|\(acw\)|-acw|\(sck\)|sck\b|contact|\(same work).*",re.I|re.S)
def what(s):
    s=(s or "").strip()
    if s.lower().startswith("source information"): return ""
    s=re.sub(r"^\(DMH[^)]*\)\s*","",s); s=CUT.sub("",s); s=re.sub(r"\s*-?\s*2020 IRC.*","",s,flags=re.I|re.S); s=re.sub(r"_+"," ",s); s=re.sub(r"\s+"," ",s).strip(" .-;,")
    if s.isupper(): s=s.capitalize()
    return s[:160]
def title(s): return " ".join((w.lower() if re.match(r"^\d+(st|nd|rd|th)$",w,re.I) else w.upper() if re.match(r"^(\d|[NSEW]{1,2}$)",w) else ("Mc"+w[2:].capitalize() if w.lower().startswith("mc") and len(w)>3 else w.capitalize())) for w in (s or "").split())
BIZ=re.compile(r"\b(INC|LLC|L\.L\.C|CORP|CORPORATION|CO|COMPANY|CONST|CONSTRUCTION|BUILD|BUILDERS|BUILDING|HOMES|HOME|REMODEL|REMODELING|DESIGN|GROUP|ROOF|ROOFING|DECK|DECKS|LANDSCAP\w*|PROPERT\w*|DEVELOP\w*|CONTRACT\w*|SERVICES|RENOVAT\w*|ARCHITECT\w*|STUDIO|ENTERPRISES|SCIENCE|POOLS?|GARAGES?|EXTERIORS|CARPENTRY|MASONRY|CONCRETE|LTD)\b",re.I)
def contractor(n):
    n=(n or "").strip()
    if not n or not BIZ.search(n): return ""
    t=title(n)
    for a,b in [(" Llc"," LLC"),(" Inc"," Inc."),(" Co "," Co. "),("Cc ","CC ")]: t=t.replace(a,b)
    return t.rstrip(",. ").replace("Inc..","Inc.")

# ---------- Vineland ----------
VL=(44.957226913373,-93.236326606297)
rows=[]
for x in json.load(open("vineland_raw.json")):
    if x["status"]=="Cancelled" or x["Latitude"] is None: continue
    c=(x["comments"] or "").lower()
    if x["permitType"]=="Wrecking": t="Teardown"
    elif x["workType"]=="New": t="New house"
    elif "pool" in c: t="Pool"
    elif "retaining" in c: t="Retaining wall"
    elif "garage" in c: t="Garage"
    elif re.search(r"2nd|second|story|dormer|shed dormer",c) and not re.search(r"foundation|basement|footing",c): t="Upper-floor addition"
    elif re.search(r"deck|porch|stoop|pergola",c): t="Deck or porch"
    elif x["workType"]=="Accessory": t="Garage" if "accessory" in c or "shed" in c else "Outbuilding"
    else: t="Ground-floor addition"
    rows.append(dict(addr=title(x["Display"]),hood=x["Neighborhoods_Desc"] or "",type=t,issued=D(x["issueDate"]),
        status="Finished" if x["status"]=="Closed" else "Work under way",what=what(x["comments"]),
        by=contractor(x["applicantName"]),permit=x["permitNumber"],lat=round(x["Latitude"],5),lon=round(x["Longitude"],5),
        mi=miles(*VL,x["Latitude"],x["Longitude"])))
rows.sort(key=lambda r:r["issued"],reverse=True)
json.dump(rows,open("vineland.json","w"))
print("vineland",len(rows),collections.Counter(r["type"] for r in rows),collections.Counter(r["status"] for r in rows))
print("date range",rows[-1]["issued"],rows[0]["issued"], "within 2mi",sum(r["mi"]<=2 for r in rows))

# ---------- AOC ----------
AO=(44.821744382169,-93.305173164597)
EX=re.compile(r"roof|solar|window|water damage|fire damage|parking|sign\b|signage|demo only|not a building permit|fire barrier|repair|reroof|siding|balcon|elevator|antenna|tower|canopy|sound control|masonry|tuckpoint|facade|stair|amphitheater",re.I)
IN=re.compile(r"tenant|build[- ]?out|\bTI\b|occupancy required:\s*yes|change of use|conver|restaurant|office|retail|clinic|salon|studio|cafe|coffee|\bbar\b|brewery|gym|fitness|school|daycare|new building|interior remodel|interior alteration|remodel of|alterations",re.I)
arows=[]
for x in json.load(open("aoc_raw.json")):
    cm=x["comments"] or ""
    if x["status"] in("Cancelled","Expired") or x["Latitude"] is None or EX.search(cm): continue
    if not (IN.search(cm) or x["workType"] in("New","Addition")): continue
    done=D(x["completeDate"])
    if x["status"]=="Closed":
        if not done or done<"2026-07-01": continue
        st="Just finished"
    else: st="Final inspection" if x["milestone"]=="Final Inspection" else "Under construction"
    c=cm.lower()
    if re.search(r"new (construction|building|mixed|\d)|construct (a |new )?\d? ?story|construct \d|build church|new \d+ story",c) or x["workType"]=="New": kind="New building"
    elif "addition" in c or x["workType"]=="Addition": kind="Addition"
    elif re.search(r"tenant|\bti\b|build[- ]?out|suite",c): kind="Tenant build-out"
    else: kind="Remodel"
    arows.append(dict(addr=title(x["Display"]),hood=x["Neighborhoods_Desc"] or "",type=kind,stage=st,issued=D(x["issueDate"]),done=done,
        what=what(cm),by=contractor(x["applicantName"]),permit=x["permitNumber"],fees=round(x["totalFees"] or 0),
        co="yes" if re.search(r"occupancy required\s*[:\-]?\s*(yes|y\b)|CERTIFICATE OF OCCUPANCY REQUIRED - AN",cm,re.I) else "",
        lat=round(x["Latitude"],5),lon=round(x["Longitude"],5),mi=miles(*AO,x["Latitude"],x["Longitude"])))
order={"Final inspection":0,"Under construction":1,"Just finished":2}
arows.sort(key=lambda r:(order[r["stage"]],-r["fees"]))
json.dump(arows,open("aoc.json","w"))
print("aoc",len(arows),collections.Counter(r["stage"] for r in arows),collections.Counter(r["type"] for r in arows))
for r in arows[:6]: print(r)
for name,rs,cols in [("vineland",rows,["issued","addr","hood","type","status","what","by","permit","mi"]),("aoc",arows,["stage","addr","hood","type","what","by","issued","done","fees","co","permit","mi"])]:
    with open(f"{name}.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction="ignore");w.writeheader();w.writerows(rs)
