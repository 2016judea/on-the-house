"""Open federal notices (SAM.gov active file, keyless bulk CSV pulled 2026-09-26) that
ask someone to SUPPLY a power or distribution transformer, due after today."""
import csv, json, re, sys, pathlib
csv.field_size_limit(sys.maxsize)
HERE = pathlib.Path(__file__).parent
TODAY = "2026-09-27"
XF = re.compile(r"\b(pad[- ]?mount(ed)?|pole[- ]?mount(ed)?|substation|power|distribution|dry[- ]type|oil[- ]filled|step[- ]?(up|down)|\d{2,5}\s*kVA|\d{1,3}(\.\d)?\s*MVA)\b[^.]{0,60}\btransformers?\b|\btransformers?\b[^.]{0,40}\b(\d{2,5}\s*kVA|\d{1,3}(\.\d)?\s*MVA)", re.I)
NOT = re.compile(r"current transformer|potential transformer|instrument transformer|CCVT|control power transformer|transformer oil testing only", re.I)
rows = []
for r in csv.DictReader(open(HERE / "cache/active.csv", encoding="utf-8", errors="replace", newline="")):
    due = (r["ResponseDeadLine"] or "")[:10]
    if due < TODAY or r["Type"] in ("Award Notice", "Justification", "Sale of Surplus Property"):
        continue
    t = r["Title"] + " \n " + (r["Description"] or "")
    m = XF.search(t)
    if not m or (NOT.search(r["Title"])):
        continue
    kva = re.findall(r"(\d[\d,]{1,6})\s*kVA", t, re.I)[:4]
    mva = re.findall(r"(\d{1,3}(?:\.\d+)?)\s*MVA", t, re.I)[:4]
    rows.append({"id": r["NoticeId"], "sol": r["Sol#"], "title": r["Title"], "type": r["Type"], "posted": r["PostedDate"][:10],
                 "due": due, "agency": r["Department/Ind.Agency"], "subtier": r["Sub-Tier"], "office": r["Office"],
                 "pop": ", ".join(x for x in (r["PopCity"], r["PopState"]) if x), "setaside": r["SetASide"],
                 "naics": r["NaicsCode"], "psc": r["ClassificationCode"], "contact": r["PrimaryContactFullname"],
                 "email": r["PrimaryContactEmail"], "link": r["Link"], "kva": kva, "mva": mva,
                 "hit": t[max(0, m.start() - 250): m.end() + 350].replace("\n", " ")})
rows.sort(key=lambda x: x["due"])
(HERE / "open_bids.json").write_text(json.dumps(rows, indent=1))
print(len(rows))
for x in rows: print(x["due"], x["type"][:12], "|", x["subtier"][:26], "|", x["title"][:75], "|", x["pop"], "|", x["kva"], x["mva"], "|", x["setaside"][:20])
