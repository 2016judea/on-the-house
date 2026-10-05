# Permit gifts — sent 2026-09-28

Free, no-strings lists built from the live Minneapolis permit register (CCS_Permits)
for businesses whose next customer shows up there first. Hosted at unguessable
`brickandmortar.dev/for/<token>/` paths (noindex, CSV alongside). Scripts:
`../../pipeline/permits/` (pull → build → render; template shared).

| sent | business | to | page | the list |
|---|---|---|---|---|
| 9/28 | Vineland Tree | trees@vinelandtree.com | /for/c6470f39/ | 584 homes with outdoor construction since Mar 1 |
| 9/28 | AOC Building Solutions | info@aocbuildingsolutions.com | /for/0e73a821/ | 269 commercial spaces near the turnover clean |
| 9/28 | Architectural Antiques | ian@archantiques.com | /for/5a49a5d6/ | 42 open wrecking permits, year built, wrecker |
| 9/28 | Dusty Signs | dan@dustysigns.com | /for/17222c0c/ | 38 storefront build-outs |
| 9/28 | ASF Store Fixtures | info@asfmn.com | /for/d5839737/ | 19 retail build-outs, 15 dispensaries |
| 9/28 | Jos. F. Palen Co. | josfpalen@yahoo.com | /for/37a866e2/ | 65 kitchens built or torn out |
| 9/28 | 3 Bears Landscaping | office@3bearslandscaping.com | /for/3265551f/ | 356 finished yards, 110 within 2 mi |
| 10/04 SENT 19:44 (Zoho, msg 1791161078366138300) | Blue Vector Bookkeeping (Joel Oine, found on Craigslist) | info@bluevectorbooks.com | /for/d9143508/ | 51 Minneapolis restaurant/bar/café build-outs, 10 at final inspection |
| 10/04 SENT 19:45 (SMS from Messages.app on Aidan's Mac, on his 'go ahead and text him') | Bloomington surplus reseller (952-854-5786, found on Craigslist, no name) | text to 952-854-5786 | /for/f1489cf3/ | 17 open commercial wrecking permits + 13 metro WARN sites |

Replies: none yet. Log them here verbatim.

Traps hit: Minneapolis publishes no project value (fees only); `permitType='Commercial'`
includes condo units (filter occupancyType Comm/Mixed, dedupe per unit); business names
parsed from permit text were wrong ("Levels", "ACW") so they were dropped; the MN cannabis
office's license list sits behind a bot wall; Saint Paul's register stopped mid-2025.
