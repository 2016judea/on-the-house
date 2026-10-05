import json, urllib.request, urllib.parse, collections, datetime as dt
B="https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services"
def q(svc, where, fields="*"):
    out=[];off=0
    while True:
        p=dict(where=where,outFields=fields,f="json",resultOffset=off,resultRecordCount=2000,returnGeometry="false")
        d=json.load(urllib.request.urlopen(urllib.request.Request(f"{B}/{svc}/FeatureServer/0/query",data=urllib.parse.urlencode(p).encode())))
        fs=[f["attributes"] for f in d.get("features",[])]; out+=fs
        if not d.get("exceededTransferLimit") or not fs: break
        off+=len(fs)
    return out
D=lambda ms: dt.datetime.utcfromtimestamp(ms/1000).date() if ms else None
liq=q("On_Sale_Liquor","1=1")
print("liquor status",collections.Counter(l["licenseStatus"] for l in liq))
print("liquor type",collections.Counter(l["licenseType"] for l in liq).most_common(8))
print("endorsements sample",collections.Counter(l["endorsements"] for l in liq).most_common(6))
iss=[l for l in liq if l["issueDate"] and D(l["issueDate"])>=dt.date(2026,7,1)]
print("issued since 7/1:",len(iss))
print("issue-date month histogram",sorted(collections.Counter(D(l["issueDate"]).strftime('%Y-%m') for l in liq if l['issueDate']).items())[-14:])
for l in liq:
    if l["licenseStatus"]!="Approved": print("  ",l["licenseStatus"],l["licenseName"],l["address"],D(l["issueDate"]),l["licenseNumber"])
json.dump(liq,open("liq_all.json","w"))
food=q("Food_Inspections","YearOfInspection>=2024","HealthFacilityIDNumber,BusinessName,FacilityCategory,DateOfInspection,FullAddress,APN,InspectionType")
first={}
for f in food:
    k=f["HealthFacilityIDNumber"]; d=D(f["DateOfInspection"])
    if k not in first or d<first[k][0]: first[k]=(d,f["BusinessName"],f["FullAddress"],f["FacilityCategory"])
new=[v for v in first.values() if v[0]>=dt.date(2026,7,1) and v[3] in ("RESTAURANT","FOOD TRUCK","GROCERY","FOOD CART")]
print("facilities first inspected since 7/1 (no inspection in 2024-6/2026):",len(new), collections.Counter(v[3] for v in new))
for v in sorted(new)[-15:]: print("  ",v)
print("latest inspection date in data", max(D(f["DateOfInspection"]) for f in food))
json.dump({k:[str(v[0]),*v[1:]] for k,v in first.items()},open("food_first.json","w"))
