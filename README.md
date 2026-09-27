# On the House

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
| 3 | `pipeline/gifts/<slug>.py` | builds that one gift into `site/` | $0 |
| 4 | `pipeline/draft_email.py` | writes `drafts/<slug>.md` and the review page | $0 |
| 5 | `pipeline/send.py` | Mailgun, `--dry-run` by default. Aidan reads and fires. | — |

`menu.json` is the priced list, seeded from the June 2026 servicing debrief.
Anything that needs the owner's login is on the menu, never in the free work.
