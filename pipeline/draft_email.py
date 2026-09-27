"""Step 4 (agent): draft the email for one owner. Never sends.

Shape, set by Aidan 2026-09-26: subject = the thing we did. Body: what we did in one
sentence naming THEIR thing, the link, "free, on us", "if there's any other work you'd like
done, just let us know", then 2-3 priced next jobs as a short afterthought. 5th-grade words.
Register: aidan-voice skill, business/explainer — short, no hedges, signed "Best, Aidan".

The agent writes; this script checks. A draft that fails a check is not written.
Writes drafts/<slug>.md, then rebuilds drafts/INDEX.md and drafts/index.html.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

from inputs import ROOT
from llm import ask_json

BASE = "https://on-the-house-bm.vercel.app"
NAME = {"dunn-brothers-coffee-company": "Dunn Bros Coffee on Grand", "perfect-image": "Facials with Rachel (listed on Google as Perfect Image)"}
OWNER = {"j-gilman-salon": "Justin", "bare-mn-skin-care-studio": "Jillian", "perfect-image": "Rachel"}
SIGN = "Best,\nAidan\nBrick & Mortar\naidan@brickandmortar.dev"
MUST = ["free, on us", "if there's any other work you'd like done, just let us know"]

PROMPT = """Write a short email from Aidan (Brick & Mortar) to the owner of {name}.

We already did a free piece of work for them. Here is exactly what, and the evidence:
HEADLINE: {headline}
EVIDENCE: {evidence}
HOW THEY USE IT: {to_use}
LINK: {link}

Rules — every one is checked by a script:
- subject: names the thing we did for them, specific to them, under 60 characters. No "free", no "quick question".
- greeting: "{greeting}"
- first sentence says what we did, naming their specific thing (reword HEADLINE). No introduction of who we are first.
- use at most ONE fact from EVIDENCE, and only if it makes the first sentence land. Plain words: no 'title tag', 'CNAME', 'metadata'.
- then the link on its own line, exactly: {link}
- then one or two short sentences on how to use it today.
- then this exact sentence: "It's free, on us."
- then this exact sentence: "If there's any other work you'd like done, just let us know."
- then the line "A few other things we could do:" and exactly these items as "- title: price" lines, words unchanged:
{menu}
- no sign-off; the script adds it.
- 5th-grade reading level. Short sentences. At least one under five words. No hedging words
  (maybe, just wanted, I feel, it seems). No flattery. No exclamation marks. Straight apostrophes.
- body under 90 words, not counting the menu lines.
- never claim anything not in HEADLINE/EVIDENCE. Never say "we noticed" or "I hope this finds you well".

JSON: {{"subject": "...", "body": "..."}}"""


def tidy(body: str) -> str:
    """One blank line between paragraphs; the menu bullets stay together."""
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    out = []
    for l in lines:
        if out and not (l.startswith("- ") and (out[-1].startswith("- ") or out[-1].endswith(":"))):
            out.append("")
        out.append(l)
    return "\n".join(out)


def check(d: dict, link: str, items: list[str]) -> list[str]:
    errs = []
    b = d["body"]
    low = b.lower().replace("’", "'")
    if len(d["subject"]) > 60:
        errs.append("subject too long")
    if link not in b:
        errs.append("link missing")
    for m in MUST:
        if m not in low:
            errs.append(f"missing: {m}")
    for it in items:
        if it not in b:
            errs.append(f"menu line altered: {it}")
    prose = "\n".join(l for l in b.split("\n") if not l.startswith("- "))
    if len(prose.split()) > 110:
        errs.append(f"too long: {len(prose.split())} words")
    if "!" in b:
        errs.append("exclamation mark")
    if re.search(r"(?i)\b(maybe|just wanted|i hope this|we noticed)\b", b):
        errs.append("hedge/cliche")
    return errs


def draft(slug: str) -> dict:
    biz = {b["slug"]: b for b in json.load(open(ROOT / "data/businesses.json"))}[slug]
    plan = json.load(open(ROOT / "work" / slug / "plan.json"))
    menu = json.load(open(ROOT / "menu.json"))["items"]
    items = [f'{menu[k]["title"]}: {menu[k]["price"]}' for k in plan["menu"][:3]]
    link = BASE + plan["gift_path"]
    greeting = f"Hi {OWNER[slug]}," if slug in OWNER else "Hi there,"
    prompt = PROMPT.format(name=NAME.get(slug, biz["name"]), headline=plan["headline"], evidence="; ".join(plan["evidence"]),
                           to_use=plan["to_use_it"], link=link, greeting=greeting,
                           menu="\n".join(f"- {i}" for i in items))
    for attempt in range(3):
        d = ask_json(prompt)
        d["body"] = re.sub(r"^(Hi [^\n]*,)\n(?!\n)", r"\1\n\n", d["body"].replace("’", "'").strip())
        d["body"] = tidy(d["body"])
        errs = check(d, link, items)
        if re.search(r"(?i)\byour (dunn bros |rewards )?app\b", d["body"]):
            errs.append("the app is the chain's, not theirs: say 'the Dunn Bros app'")
        if not errs:
            break
        prompt += f"\n\nYour last draft failed these checks, fix them: {errs}"
    else:
        raise SystemExit(f"{slug}: draft failed checks {errs}")
    md = f"To: {biz['email']}\nSubject: {d['subject']}\n\n{d['body']}\n\n{SIGN}\n"
    (ROOT / "drafts").mkdir(exist_ok=True)
    (ROOT / "drafts" / f"{slug}.md").write_text(md)
    return {"slug": slug, "name": biz["name"], "to": biz["email"], "subject": d["subject"], "link": link}


def index() -> None:
    rows = []
    for p in sorted((ROOT / "drafts").glob("*.md")):
        if p.name == "INDEX.md":
            continue
        t = p.read_text()
        to = re.search(r"^To: (.*)$", t, re.M)[1]
        subj = re.search(r"^Subject: (.*)$", t, re.M)[1]
        link = re.search(r"https://on-the-house-bm\.vercel\.app/\S+", t)[0]
        rows.append((p.stem, to, subj, link, t))
    md = ["# On the House — drafts, batch 1", "", "DRAFTS. Nothing has been sent. `python3 pipeline/send.py <slug>` is a dry run; add `--send` to fire one.", "",
          "| business | to | subject | gift |", "|---|---|---|---|"]
    md += [f"| {s} | {to} | {subj} | {link} |" for s, to, subj, link, _ in rows]
    (ROOT / "drafts" / "INDEX.md").write_text("\n".join(md) + "\n")
    cards = "".join(
        f'<article><h2>{html.escape(subj)}</h2><p class="m">To {html.escape(to)} · <a href="{link}">open the gift</a> · <code>python3 pipeline/send.py {s} --send</code></p>'
        f'<pre>{html.escape(t.split(chr(10) + chr(10), 1)[1])}</pre></article>' for s, to, subj, link, t in rows)
    (ROOT / "drafts" / "index.html").write_text(f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>On the House — drafts</title><style>body{{margin:0;background:#fbf8f3;color:#1d1b18;font:16px/1.5 Georgia,serif}}main{{max-width:44rem;margin:0 auto;padding:1rem}}
article{{background:#fff;border:1px solid #e4ddd2;border-radius:12px;padding:1rem;margin:1rem 0}}h2{{font-size:1.15rem;margin:0}}.m{{font:13px system-ui;color:#6b645b}}
pre{{white-space:pre-wrap;font:15px/1.5 Georgia,serif;margin:.6rem 0 0}}</style>
<main><h1>{len(rows)} drafts</h1><p class=m>Nothing has been sent. Read, edit the .md file if needed, then fire one at a time.</p>{cards}</main>""")


if __name__ == "__main__":
    for s in sys.argv[1:]:
        r = draft(s)
        print(f'{s:32} {r["subject"]}')
    index()
