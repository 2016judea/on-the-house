# Facebook Marketplace sweep — 2026-10-10

Headless Chrome on Aidan's copied FB session (browser-as-aidan), Minneapolis · 40 mi,
18 queries in 3 segments, 212 listings read, 186 distinct sellers. Raw: listings_2026-10-10.json.
Nothing sent, nothing posted, no groups joined.

## Business sellers → which gift (line one quotes their own listing, rule 11)

| Seller | Profile | Their listing | Gift |
|---|---|---|---|
| Moises Castano | marketplace/profile/1477754961 | "Restaurant Kitchen Equipment – request a quote" (equipment, hoods, remodels) | MPLS restaurant build / re-hood permits (Blue Vector list, re-rendered for him) |
| Rustam Muharamov | marketplace/profile/100014792100721 | 4 listings: commercial kitchen / restaurant spaces for lease | same permit list (who is opening) |
| Steve DeRuyck + Joel Hops (D&B Restaurant Supply, S. St Paul) | profile/100004119578467, /61591296914581 | NSF stainless work tables, 7 days pickup | same permit list |
| Randy SPizza | profile/1232707126 | 3 used Superior walk-in coolers | same permit list |
| Sonna Tatsopteu | profile/100084001552157 | walk-in cooler panels | same permit list |
| Kim Hughes | profile/61551823419126 | new Dukers fryers, ships | same permit list |
| Paul Jablonsky | profile/100004346678593 | NE Mpls commercial/ghost kitchen rental being spec'd | same permit list |
| Tang Fung | profile/1171759792 | 2,000 sqft commercial kitchen for lease, Little Canada | same permit list |
| Jeff Peterson | profile/100000485857927 | concrete/asphalt + "all types of demolition", Hopkins | Demolition Notice |
| Ben Hauling | profile/100001201963313 | free scrap metal hauling pickup | Demolition Notice |
| Matt Austin | profile/100030908154038 | "I pick up scrap metal, computers, wire", Shakopee | Demolition Notice |
| Marcia Kolb | profile/100000245494668 | 3 architectural salvage trim lots | Demolition Notice |
| Sarah Marie | profile/100009204932948 | architectural salvage lot | Demolition Notice |

Parts queries (industrial surplus, pumps, valves, breakers) returned only individuals — no fit for Legacy Requests.
13 is a probe against the 50-recipient floor (BUSINESS.md rule 4); widen with St Paul + more queries before calling it.

## Posting AI services / photography
Marketplace bans services (physical goods only) and removal can lock the account out — not there.
Groups that take service posts (all public unless noted, members · posts/day):
- AI services: DROPPED by Aidan 2026-10-10 ("nix this").
- Wedding photography: Everything wedding related Minnesota 14K · 60+; MN Wedding Sell & Swap 25K · 90+ (private); Minnesota Weddings: Find Your Dream Vendors 2.9K · 10+; Minneapolis Photographers 8.7K · 10+; Minnesota Micro Weddings 1.1K

## Demolition Notice gifts, 2026-10-10
5 pages, one per salvage seller, cut by trade from the Minneapolis wrecking-permit feed: demolition-notice.vercel.app/for/{5735d7d6 Jeff, 798faff6 Ben, 978feaee Matt, 778cec14 Marcia, ca8ff007 Sarah}/ (scrapwatch `scripts/build_gifts.mjs`). Messages drafted in `tokens_demolition.csv`, **NOT SENT**: run `zsh send_demolition.sh` (headless, port 9491, ~60s pacing, writes sent_at) once Aidan says send himself. Follow-up 10/17 in ~/.claude/pending.json.

## 2026-10-10 kitchen-trade gifts (8 pages, drafts only)
8 pages at brickandmortar.dev/for/<token>/ (tokens.csv), each framed for the seller's trade, rendered by pipeline/permits/fbm_render.py from permits + the city's new truck/caterer/grocery licences (fbm_pull.py). D&B: one message, sent via Steve DeRuyck's listing; Joel Hops skipped as the same business. Messages are in messages_restaurant.json. The coordinator session sends them; sent_at stays blank until it does.

## Sent 2026-10-10 (main session, send_marketplace.js)
13 of 13 delivered and visible in Marketplace inbox → Buying: 5 demolition (13:16–13:21), 8 restaurant (13:29–13:39; Joel Hops skipped as same business as D&B/Steve).
Moises logged clicked_unverified by the script but the thread shows the full message at 13:29.
**Replies:** Ben Hauling, 13:19 — "I I can definitely remove items out of each property".
Photography groups: photo_groups_2026-10-10.md (3 join requests pending).

## Photography post — 2026-10-10
Joined "Minnesota Weddings: Find Your Dream Vendors" (facebook.com/groups/1332551547894958, public, no questions, no approval) and posted the Craigslist wedding copy verbatim as Aidan Jude. Live immediately, not held for review. Link preview rendered the aidanjude.vercel.app home card, not the photography page.
Ben Hauling reply: drafted response (not sent) — "Not my properties — each one on the list names who's tearing it down. That's who to call, ideally before the walls come down. Want me to send you the new ones as the city issues them?"
- 14:2x: post deleted and reposted so the preview shows the wedding frame (aidanjude.vercel.app og/photography.jpg, writing-topology 6f5abb8; FB Sharing Debugger re-scraped). Ben reply SENT 14:22.
- Lead seen in the group: anonymous couple, Oct 2028 wedding, Hastings / River Falls, $2,000 budget (posted ~10/06, 14 comments).
