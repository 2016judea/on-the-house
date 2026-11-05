"""Hennepin parcels the COUNTY assesses (outside the seven self-assessing cities
and Maple Grove) where the Aug 2026 parcel file carries $0 building value but
Overture Maps (release 2026-08-19) places an operating business inside the lot.
Public owners and non-business categories are dropped: an exempt city hall on a
land-only parcel is not a finding."""
import duckdb, json, pathlib, re
DB = pathlib.Path.home() / "Desktop/workspace/bricks/data/closed_system.duckdb"
V = "county_hennepin_2026_08"
SELF = ('BLOOMINGTON','BROOKLYN PARK','EDEN PRAIRIE','EDINA','MINNEAPOLIS','MINNETONKA','ST LOUIS PARK','MAPLE GROVE','')
PUBLIC = re.compile(r"\b(CITY|VILLAGE|COUNTY|STATE OF|U S |USA|GOVT|COMMISSION|AUTH|EDA|HRA|SCHOOL|DIST|CHURCH|CH$|METH|LUTH|CATH|PARK|WATERSHED|MET COUNCIL|RAILROAD|RY CO|UNIV)\b")
SKIP = {"park","lake","central_government_office","public_service_and_government","water_supplier","department_of_motor_vehicles","church_cathedral","airport_terminal","airline","structure_and_geography","river","beach","campground","playground","religious_organization","school","elementary_school","high_school","landmark_and_historical_building","nature_reserve","trail","golf_course","cemetery","community_services_non_profits","parking","dog_park"}
c = duckdb.connect(str(DB), read_only=True)
rows = c.execute(f"""
select p.pin, p.anumber, p.street, p.city, p.useclass1, p.emv_land, p.emv_bldg, p.emv_total, p.owner_name, p.year_built,
       r.attrs->>'name', r.attrs->>'category', (r.attrs->>'confidence')::double, r.attrs->>'websites'
from parcel_snapshot p join record r on r.layer='overture_places' and r.parcel_key=p.parcel_key
where p.vintage='{V}' and upper(trim(coalesce(p.city,''))) not in {SELF}
  and coalesce(p.emv_bldg,0)=0 and coalesce(p.emv_land,0)>0
  and (r.attrs->>'confidence')::double >= 0.9
order by p.emv_land desc""").fetchall()
out = {}
for (pin, no, st, city, use, land, bldg, tot, owner, yb, name, cat, conf, web) in rows:
    if PUBLIC.search((owner or "").upper()) or cat in SKIP:
        continue
    o = out.setdefault(pin, {"pin": pin, "address": f"{no} {st}".strip(), "city": (city or "").strip().title(),
                             "class": use, "land_value": land, "building_value": bldg, "owner": (owner or "").strip(),
                             "businesses": []})
    o["businesses"].append({"name": name, "category": cat, "confidence": round(conf, 2)})
res = sorted(out.values(), key=lambda x: -x["land_value"])
pathlib.Path(__file__).with_name("zero_building.json").write_text(json.dumps(res, indent=1))
print(len(res))
for x in res: print(x["pin"], x["address"], x["city"], x["class"], int(x["land_value"]), x["owner"][:28], "|", "; ".join(f"{b['name']} ({b['category']})" for b in x["businesses"][:3]))
