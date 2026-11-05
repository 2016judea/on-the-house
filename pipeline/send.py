"""Step 5: send ONE drafted email through Mailgun. Dry run unless --send.

    python3 pipeline/send.py <slug>            # prints exactly what would go, touches nothing
    python3 pipeline/send.py <slug> --send     # sends it, records it in drafts/sent.csv

Aidan fires these, one at a time, after reading the draft. Contacting a real person is his
gate, so nothing in the pipeline calls this with --send.

Same Mailgun path as bricks/scripts/outreach/send_mailgun.py (Zoho blocked cold sends on
2026-09-14): From and Reply-To are aidan@brickandmortar.dev so replies land in Zoho, and
click/open tracking is OFF so the gift link stays the real link, not a mailgun redirect.
The ledger refuses a second send to the same slug.
"""
from __future__ import annotations

import argparse
import base64
import csv
import datetime
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = Path.home() / "Desktop/workspace/bricks/.env"
LEDGER = ROOT / "drafts" / "sent.csv"


def env() -> dict:
    out = {}
    for line in ENV.read_text().splitlines():
        if line.startswith("MAILGUN_") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def read(slug: str) -> tuple[str, str, str]:
    p = ROOT / "drafts" / f"{slug}.md"
    if not p.exists():
        sys.exit(f"no draft at {p}")
    lines = p.read_text().split("\n")
    to = next(l.split(": ", 1)[1] for l in lines if l.startswith("To: "))
    subject = next(l.split(": ", 1)[1] for l in lines if l.startswith("Subject: "))
    i = next(n for n, l in enumerate(lines) if l.startswith("Subject: "))
    body = "\n".join(lines[i + 2:]).rstrip()
    return to.strip(), subject.strip(), body


def already_sent(slug: str) -> str | None:
    if not LEDGER.exists():
        return None
    for r in csv.DictReader(LEDGER.open()):
        if r["slug"] == slug:
            return r["sent_at"]
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--send", action="store_true", help="actually send (default is a dry run)")
    a = ap.parse_args()
    to, subject, body = read(a.slug)
    when = already_sent(a.slug)
    if when:
        sys.exit(f"REFUSED: {a.slug} was already sent at {when}.")
    print(f"To: {to}\nSubject: {subject}\n\n{body}\n")
    if not a.send:
        print("DRY RUN. Nothing sent. Add --send to send this one.")
        return
    e = env()
    fields = [("from", f"Aidan <{e['MAILGUN_FROM']}>"), ("to", to), ("h:Reply-To", e["MAILGUN_FROM"]),
              ("subject", subject), ("text", body),
              ("o:tracking", "no"), ("o:tracking-clicks", "no"), ("o:tracking-opens", "no")]
    req = urllib.request.Request(f"https://api.mailgun.net/v3/{e['MAILGUN_DOMAIN']}/messages",
                                 data=urllib.parse.urlencode(fields).encode())
    req.add_header("Authorization", "Basic " + base64.b64encode(f"api:{e['MAILGUN_API_KEY']}".encode()).decode())
    with urllib.request.urlopen(req, timeout=45) as r:
        mid = json.load(r).get("id", "").strip("<>")
    new = not LEDGER.exists()
    with LEDGER.open("a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["slug", "to", "subject", "sent_at", "mailgun_id"])
        w.writerow([a.slug, to, subject, datetime.datetime.now().isoformat(timespec="seconds"), mid])
    print(f"SENT {a.slug} -> {to} · {mid}")


if __name__ == "__main__":
    main()
