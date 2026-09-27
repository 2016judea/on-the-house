"""Scan SAM.gov's public opportunity files (active + FY2026 archive, keyless bulk CSVs)
for power transformers in Jordan Transformer's range: 69 kV to 230 kV high side,
5 to 100 MVA, or explicit transformer rebuild / rewind / remanufacture work."""
import csv, json, re, sys, pathlib
csv.field_size_limit(sys.maxsize)
HERE = pathlib.Path(__file__).parent
KV = re.compile(r"\b(69|115|138|161|230)\s*-?\s*kV\b", re.I)
MVA = re.compile(r"\b(\d{1,3}(?:\.\d)?)\s*(?:/\s*\d{1,3}(?:\.\d)?\s*)*MVA\b", re.I)
XF = re.compile(r"transformer", re.I)
WORK = re.compile(r"rewind|rebuild|re-build|remanufactur|refurbish|recondition|repair|overhaul|replace", re.I)
NOT = re.compile(r"current transformer|potential transformer|voltage transformer|CCVT|instrument transformer|control transformer", re.I)
out = []
for name in ("active.csv", "fy2026.csv"):
    with open(HERE / "cache" / name, encoding="utf-8", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            t = (r.get("Title") or "") + " \n " + (r.get("Description") or "")
            if not XF.search(t) or not (KV.search(t) or MVA.search(t)):
                continue
            mva = [float(m.group(1)) for m in MVA.finditer(t)]
            kv = sorted({int(m.group(1)) for m in KV.finditer(t)})
            if mva and not any(5 <= v <= 100 for v in mva) and not kv:
                continue
            i = XF.search(t).start()
            out.append({"file": name, "id": r["NoticeId"], "title": r["Title"], "agency": r["Department/Ind.Agency"],
                        "office": r["Office"], "subtier": r["Sub-Tier"], "posted": r["PostedDate"][:10], "type": r["Type"],
                        "deadline": (r["ResponseDeadLine"] or "")[:10], "pop": ", ".join(x for x in (r["PopCity"], r["PopState"]) if x),
                        "naics": r["NaicsCode"], "psc": r["ClassificationCode"], "award": r["Award$"], "awardee": r["Awardee"],
                        "contact": r["PrimaryContactFullname"], "contact_email": r["PrimaryContactEmail"], "link": r["Link"],
                        "kv": kv, "mva": mva[:6], "work": bool(WORK.search(t)), "instrument_only": bool(NOT.search(t)) and not mva,
                        "excerpt": t[max(0, i - 300): i + 500].replace("\n", " ")})
seen = {}
for o in out:  # one notice id can be in both files; keep the newest posting
    seen[o["id"]] = o
res = sorted(seen.values(), key=lambda x: x["posted"], reverse=True)
(HERE / "sam_hits.json").write_text(json.dumps(res, indent=1))
print(len(res))
for x in res: print(x["posted"], x["type"][:14], "|", x["subtier"][:30], "|", x["title"][:80], "|", x["pop"], "|", x["kv"], x["mva"], "W" if x["work"] else "", "INSTR" if x["instrument_only"] else "")
