# On the House

**Live:** https://on-the-house-bm.vercel.app

Free work, done for one small business at a time, then an email telling the owner what we did.

Not a report of advice. Not a product. For each business an agent reads their reviews,
their research report, their live website and public records, finds the one problem that
is theirs alone, and fixes it with no login and no contact with anyone. The fix lives at a
URL they can use today. The email says what we did, "free, on us", and lists two or three
paid jobs at the bottom.

The test every gift must pass: if it still works after swapping in another business's
name, it fails.

## Pipeline

| step | script | what it does | cost |
|---|---|---|---|
| 0 | `pipeline/inputs.py` | joins the Dropbox report corpus, the mail list and the cached Google listing; drops placeholder and agency emails | $0 |
| 1 | `pipeline/signals.py` | live website, OpenStreetMap, review sample, report text | $0 |
| 1b | `pipeline/still_open.py` | agent with web search: is it still trading? (2 of the first 10 picks had closed) | $0 (Claude Code subscription) |
| 2 | `pipeline/find_gift.py` | agent reads every review + the report, names the owner's own problem and a fix | $0 |
| 3 | `pipeline/gifts/<slug>.py` | builds that one gift into `site/`, then `pipeline/deploy.py` ships it | $0 |
| 4 | `pipeline/draft_email.py` | writes `drafts/<slug>.md` and the review page | $0 |
| 5 | `pipeline/send.py` | Mailgun, `--dry-run` by default. Aidan reads and fires. | — |

`menu.json` is the priced list, seeded from the June 2026 servicing debrief.
Anything that needs the owner's login is on the menu, never in the free work.

## Batch 1 (2026-09-26): what proved doable with no login

Worked, and each is the headline for someone in batch 1:

- **A dead site rebuilt from the Wayback Machine** (J. Gilman). CDX index + `id_` raw captures; their words, their prices, their live booking link.
- **A picture-only menu typed up** (Pounds). The model reads the menu images; a phone page and a print page.
- **Health inspection records turned into the sheets the inspector asked for** (Hazel's). Minneapolis open data only; Fargo and Wichita have no scriptable feed we found.
- **A review that isn't about them** (Bare MN), found by reading all 30 of 30 reviews.
- **Their own site contradicting reality** (Polished's closed shop, Day By Day's "Demo" title, Dunn Bros' Sunday hours).
- **A live who's-open-now board from hours they already publish** (Midtown).
- **Neighbours as leads** (Atomic): OpenStreetMap offices within a 5-minute walk of the room.

Not doable without a person: **unclaimed property.** MissingMoney and the ND state site both sit
behind a Cloudflare Turnstile that requires a click; we don't solve captchas. Grants were not tested.

Traps that shipped a wrong claim until caught:
- The Google cache is from 2026-05-18. Two of the first ten picks (Downtowner, Third Drop) had closed since. `still_open.py` now runs first.
- The gift-finder agent's complaint counts were high every time we checked (28 vs 13, 6 vs 5, 14 vs 11). Every number on a gift page is recounted with a regex over the raw reviews.
- `on-the-house.vercel.app` is a stranger's site. Ours is `on-the-house-bm.vercel.app`.
