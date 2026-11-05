# Gifts back to vendors who pitched us (10/06): their likely Twin Cities buyers, from the Overture business layer.
import json,re,subprocess,concurrent.futures as cf
d=json.load(open('/Users/aidan/Desktop/workspace/bricks/website/api/_data/twincities_businesses.json'))
I={k:i for i,k in enumerate(d['cols'])}
R=[dict(zip(d['cols'],r)) for r in d['rows']]
SURV={"Modern Survey","Ascendancy Research","SMS Research Advisors","Cook Research & Consulting","Consumer Surveys","Deft Research","Focus Market Research","Insightformation","Comprehensive Research Group","REAL Insight","Leede Research-MN","Watson Research","ANA Research / Anderson, Niebuhr & Associates, Inc.","Mcneff Research Consultants","Rainbow Research Inc","Applied Policy Research Inc","Minnesota Justice Research Center"}
EVAL={"Rainbow Research Inc","Applied Policy Research Inc","Minnesota Justice Research Center"}
def area(c):
    c=(c or "").strip().lower()
    return "Minneapolis" if c=="minneapolis" else "Saint Paul" if c in("st paul","saint paul","st. paul") else "Suburbs"
def alive(u):
    if not u: return False
    if not u.startswith("http"): u="http://"+u
    r=subprocess.run(["curl","-sL","-o","/dev/null","-m","12","-A","Mozilla/5.0","-w","%{http_code}",u],capture_output=True,text=True)
    return r.stdout.strip()[:1] in "23"
def row(b,kind):
    return {"addr":b["name"],"what":f'{b["address"] or ""}, {b["city"] or ""}'.strip(", "),"web":b["website"] or "","phone":b["phone"] or "","city":b["city"] or "","area":area(b["city"]),"kind":kind,"lat":b["lat"],"lon":b["lon"],"cat":b["category"]}
surv=[row(b,"Evaluation and policy research" if b["name"] in EVAL else "Market research") for b in R if b["name"] in SURV]
sw=[row(b,"Software developer") for b in R if b["category"]=="software_development" and not b["brand"] and b["website"]]
it=[row(b,"IT company") for b in R if b["category"]=="information_technology_company" and not b["brand"] and b["website"]]
allr=surv+sw+it
with cf.ThreadPoolExecutor(32) as ex:
    for r,ok in zip(allr,ex.map(lambda r:alive(r["web"]),allr)): r["live"]=ok
out={"survhey":[r for r in surv if r["live"]],"treforge":[r for r in sw+it if r["live"]],"bestlatech":[r for r in sw if r["live"]]}
for k,v in out.items(): print(k,len(v),"of",{"survhey":len(surv),"treforge":len(sw+it),"bestlatech":len(sw)}[k])
json.dump(out,open("vendors.json","w"))
