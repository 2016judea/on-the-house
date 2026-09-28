import json, urllib.request, urllib.parse
U="https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/CCS_Permits/FeatureServer/0/query"
F="Display,APN,Latitude,Longitude,Neighborhoods_Desc,applicantName,permitNumber,permitType,occupancyType,workType,status,milestone,comments,issueDate,completeDate,totalFees"
def q(where):
    out=[];off=0
    while True:
        p=urllib.parse.urlencode(dict(where=where,outFields=F,f="json",resultOffset=off,resultRecordCount=2000,orderByFields="issueDate DESC"))
        d=json.load(urllib.request.urlopen(U+"?"+p))
        fs=[f["attributes"] for f in d["features"]]; out+=fs
        if not d.get("exceededTransferLimit") or not fs: break
        off+=len(fs)
    return out
sets={
 "commercial":"permitType='Commercial' AND issueDate >= date '2026-01-01'",
 "mech":"permitType='Mechanical' AND occupancyType IN ('Comm','Mixed') AND issueDate >= date '2026-01-01' AND (UPPER(comments) LIKE '%HOOD%' OR UPPER(comments) LIKE '%KITCHEN%' OR UPPER(comments) LIKE '%RESTAURANT%')",
 "wreck":"permitType='Wrecking' AND issueDate >= date '2025-09-01'",
 "res":"permitType='Res' AND workType IN ('New','Addition','Accessory') AND issueDate >= date '2025-10-01'",
}
allr={k:q(w) for k,w in sets.items()}
for k,v in allr.items(): print(k,len(v))
json.dump(allr,open("raw2.json","w"))
# year built from Hennepin
pids=sorted({x["APN"] for v in allr.values() for x in v if x["APN"]})
HU="https://gis.hennepin.us/arcgis/rest/services/HennepinData/LAND_PROPERTY/MapServer/1/query"
yb={}
for i in range(0,len(pids),150):
    ch=pids[i:i+150]
    p=urllib.parse.urlencode(dict(where="PID IN (%s)"%",".join("'%s'"%x for x in ch),outFields="PID,BUILD_YR,PR_TYP_NM1",returnGeometry="false",f="json"))
    d=json.load(urllib.request.urlopen(urllib.request.Request(HU,data=p.encode())))
    for f in d.get("features",[]): a=f["attributes"]; yb[a["PID"]]=(a["BUILD_YR"],a["PR_TYP_NM1"])
print("pids",len(pids),"matched",len(yb))
json.dump(yb,open("yb.json","w"))
