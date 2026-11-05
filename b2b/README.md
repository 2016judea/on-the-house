# b2b — free work for one named person each

Built 2026-09-26. Each folder is a favor done for one recipient from data we already
had, plus a cover note draft. Nothing here has been sent.

| folder | for | page | note | rebuild |
|---|---|---|---|---|
| `sba-lender/` | Roshanthi Cantin, Falcon National Bank | `index.html` | `NOTE_DRAFT.md` (LinkedIn) | `python3 sos_lookup.py "Falcon National Bank" && python3 build.py` |
| `assessor/` | Anthony M Bauer, Hennepin County Assessor | `index.html` | `NOTE_DRAFT.md` (reply on D065206) | `~/Desktop/workspace/bricks/.venv/bin/python build.py` |
| `refurbisher/` | T&R Electric | `index.html` | `NOTE_DRAFT.md` (reply in thread) | download the two SAM CSVs to `cache/` (see `open_bids.py`), then `open_bids.py`, `sam_scan.py`, `build.py` |

Every number on a page is computed by that folder's `build.py`; `findings.json` holds them.
`cache/` (SOS pages, SAM bulk CSVs ~1.1 GB) is gitignored.
