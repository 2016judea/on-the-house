import json, urllib.request, urllib.parse
U="https://services.arcgis.com/afSMGVsC7QlRK1kZ/arcgis/rest/services/CCS_Permits/FeatureServer/0/query"
F="Display,APN,Latitude,Longitude,Neighborhoods_Desc,applicantName,permitNumber,permitType,occupancyType,workType,status,milestone,comments,issueDate,completeDate,dwellingUnitsNew,totalFees"
def q(where):
    out=[];off=0
    while True:
        p=urllib.parse.urlencode(dict(where=where,outFields=F,f="json",resultOffset=off,resultRecordCount=2000,orderByFields="issueDate DESC"))
        d=json.load(urllib.request.urlopen(U+"?"+p))
        fs=[f["attributes"] for f in d["features"]]; out+=fs
        if not d.get("exceededTransferLimit") or not fs: break
        off+=len(fs)
    return out
res=q("issueDate >= date '2026-03-01' AND ((permitType='Res' AND workType IN ('Addition','Accessory','New')) OR (permitType='Wrecking' AND occupancyType IN ('SFD','TFD','3to4')))")
com=q("permitType='Commercial' AND occupancyType IN ('Comm','Mixed') AND workType IN ('Remodel','Addition','New') AND (issueDate >= date '2026-03-01' OR completeDate >= date '2026-06-01')")
json.dump(res,open("vineland_raw.json","w")); json.dump(com,open("aoc_raw.json","w"))
print(len(res),len(com))
