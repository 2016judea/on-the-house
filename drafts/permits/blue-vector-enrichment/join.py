import json, urllib.request, urllib.parse, csv, collections
B="https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services"
def q(svc, where, fields="*", order=None):
    out=[];off=0
    while True:
        p=dict(where=where,outFields=fields,f="json",resultOffset=off,resultRecordCount=2000,returnGeometry="false")
        if order: p["orderByFields"]=order
        d=json.load(urllib.request.urlopen(urllib.request.Request(f"{B}/{svc}/FeatureServer/0/query",data=urllib.parse.urlencode(p).encode())))
        fs=[f["attributes"] for f in d.get("features",[])]; out+=fs
        if not d.get("exceededTransferLimit") or not fs: break
        off+=len(fs)
    return out
rows=list(csv.DictReader(open("/Users/aidan/Desktop/workspace/bricks/website/for/d9143508/restaurants-opening.csv")))
pn=[r["Permit #"] for r in rows]
perm=q("CCS_Permits","permitNumber IN (%s)"%",".join(f"'{x}'" for x in pn),"permitNumber,APN,Display,Latitude,Longitude,applicantName,milestone,status")
bypn={p["permitNumber"]:p for p in perm}
apns=sorted({p["APN"] for p in perm if p["APN"]})
print("permits",len(perm),"apns",len(apns))
inl=",".join(f"'{a}'" for a in apns)
food=q("Food_Inspections",f"APN IN ({inl}) AND YearOfInspection>=2025","HealthFacilityIDNumber,BusinessName,FacilityCategory,RiskLevel,InspectionType,InspectionResult,DateOfInspection,APN,FullAddress")
liq=q("On_Sale_Liquor",f"apn IN ({inl})")
other=q("CCS_Permits",f"APN IN ({inl}) AND issueDate >= date '2025-01-01'","permitNumber,APN,permitType,workType,applicantName,comments,issueDate,status,milestone")
json.dump(dict(rows=rows,bypn=bypn,food=food,liq=liq,other=other),open("join.json","w"),default=str)
print("food rows",len(food),"liq",len(liq),"other permits",len(other))
print(collections.Counter(f["InspectionType"] for f in food).most_common())
print(collections.Counter(o["permitType"] for o in other).most_common())
