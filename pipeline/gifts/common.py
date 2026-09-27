"""Shared page shell for every gift.

Every page is noindex: it is a draft handed to one owner, not a public listing, and it
must never outrank or pass for the business's own site. Every page carries a one-line
strip saying who built it, from what, and when, so nobody mistakes it for the owner's
official page.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "site"
BASE_URL = "https://on-the-house-bm.vercel.app"  # on-the-house.vercel.app belongs to a stranger (200 on 2026-09-26)

CSS = """
:root{--ink:#1d1b18;--mute:#6b645b;--line:#e4ddd2;--paper:#fbf8f3;--card:#fff;--accent:#8a3b12;--ok:#2f6b3a;--bad:#a3261b}
@media (prefers-color-scheme:dark){:root{--ink:#f1ece4;--mute:#b3aa9d;--line:#3a352f;--paper:#171513;--card:#211e1b;--accent:#e39a6b;--ok:#7cc38a;--bad:#f08a7f}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.5 ui-serif,Georgia,"Iowan Old Style",serif}
.wrap{max-width:44rem;margin:0 auto;padding:1.25rem 1rem 4rem}
.strip{font:13px/1.4 ui-sans-serif,system-ui,sans-serif;color:var(--mute);border-bottom:1px solid var(--line);padding:.6rem 1rem;text-align:center;background:var(--card)}
.strip a{color:inherit}
h1{font-size:2rem;line-height:1.15;margin:1.2rem 0 .4rem;letter-spacing:-.01em}
h2{font-size:1.25rem;margin:2.2rem 0 .6rem}
h3{font-size:1.05rem;margin:1.2rem 0 .3rem}
p{margin:.5rem 0}
.lede{font-size:1.15rem;color:var(--mute)}
.sans{font-family:ui-sans-serif,system-ui,sans-serif}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:1rem 1.1rem;margin:.8rem 0}
.btn{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;font:600 16px/1 ui-sans-serif,system-ui,sans-serif;padding:.85rem 1.2rem;border-radius:999px;margin:.4rem 0}
@media (prefers-color-scheme:dark){.btn{color:#171513}}
.meta{font:14px/1.45 ui-sans-serif,system-ui,sans-serif;color:var(--mute)}
table{border-collapse:collapse;width:100%;font:15px/1.4 ui-sans-serif,system-ui,sans-serif}
td,th{border-bottom:1px solid var(--line);padding:.45rem .3rem;text-align:left;vertical-align:top}
.scroll{overflow-x:auto}
q,blockquote{font-style:italic}
blockquote{margin:.6rem 0;padding-left:.9rem;border-left:3px solid var(--line);color:var(--mute)}
.ok{color:var(--ok)}.bad{color:var(--bad)}
ul{padding-left:1.2rem}
@media print{.strip,.noprint{display:none}body{background:#fff;color:#000}.card{break-inside:avoid}}
"""


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def page(slug: str, title: str, body: str, *, strip: str, sub: str = "", extra_head: str = "", css: str = "") -> Path:
    out = SITE / slug / (sub or "") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>{esc(title)}</title>
<style>{CSS}{css}</style>{extra_head}</head><body>
<div class="strip">{strip}</div>
<div class="wrap">{body}</div>
</body></html>
""")
    return out


def load(slug: str, name: str):
    return json.load(open(ROOT / "work" / slug / name))


def save_plan(slug: str, plan: dict) -> None:
    json.dump(plan, open(ROOT / "work" / slug / "plan.json", "w"), indent=1)
