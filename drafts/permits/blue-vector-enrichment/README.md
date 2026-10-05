# Blue Vector enrichment probe, 2026-10-05

Joel Oine's ask (verbatim in ../README.md, 10/05 second reply): turn "who pulled a
restaurant permit" into "which hospitality businesses are undergoing a change right now,
and what can we learn about them." This tested each field he named against the 51 rows of
/for/d9143508/. Nothing sent. `restaurants-opening-enriched.csv` is the result.

## Coverage, counted (51 rows / 10 at final inspection)

| Field he named | Source | Free? | 51 rows | Final insp. |
|---|---|---|---|---|
| Business name | any source below | yes | 42 | 8 |
|  | permit "name" column alone (the gift as sent) | yes | 3 | 1 |
| Website | Google Places nearby, 35 m | free tier | 23 | 5 |
| Phone | Google Places | free tier | 25 | 4 |
| Liquor license | City `On_Sale_Liquor` (ArcGIS, edited 9/22) | yes | 11 | 1 |
| New vs existing | liquor license NUMBER (sequential; >420000 = issued 2026) | yes | 5 new | 0 |
| Opening stage | food inspections: first-ever visit date per facility | yes | 20 | 3 |
| Owner / group | MN Secretary of State, Manager field | yes, curl works | spot-checked | — |
| News | web search | yes | chef-driven only | — |
| Hiring | job boards | — | not found | — |

## What each source actually is

- **Google listing with 0–5 reviews = about to open.** 10 rows. Evergreen Café at
  4600 Nicollet shows 0 reviews and a website; it is the row Joel turned into a meeting.
  Pre-open places also show CLOSED_TEMPORARILY (Jujube at 1100 2nd St S).
- **Liquor license numbers are sequential.** The status field is useless (151 "Pending"
  are mostly the March–April renewal batch), but a high number is a new license: new
  concept (Indigena by Owamni, Killen's Irish Pub) or re-licence of an old name
  (Saffron, 432080), which is the ownership-change signal he asked for.
  The layer is a snapshot with no history: a weekly diff is the feed.
- **Food inspections, first visit per HealthFacilityIDNumber.** 66 kitchens citywide got
  their first-ever inspection between 7/01 and 9/29 (46 restaurants, 12 trucks, 8 grocery).
  That is a "just opened" feed across all of Minneapolis, not just permit addresses.
  No pre-operational inspection type exists in the data (Routine / Follow-Up / VerRec only).
- **MN SOS** (mblsportal.sos.mn.gov) answers plain curl: search by name, then detail page
  gives filing date, status, Manager name and address. Shepherds Table MN LLC: filed
  2023-03-22, Manager Elia Read. Food-license names are often the LLC, so they chain.
- **News** exists for chef-driven openings only (Evergreen: Star Tribune, MSP Mag,
  Hoodline; Bellecour: Star Tribune). Star Tribune's "Restaurant Roll Call" is a running list.
- **Hiring**: no per-business signal from search. Not cheap.

## Errors this found in the gift as sent

- "Bellcour" on the page is the permit's typo; it is **Bellecour** (Gavin Kaysen, third
  location, Wells Fargo Center, late fall 2026).
- **1 49th St W is Justice Page Middle School's kitchen**, listed as final inspection. A
  school cafeteria is not a bookkeeping prospect.

## Someone already sells part of this

The Development Tracker (thedevelopmenttracker.com) tracks Twin Cities tenants
"from early signals through completion", Evergreen Cafe included. Free account plus a
paid TDT+ tier. It is CRE-oriented; it shows no liquor, food-license, SOS or contact join.

## Scripts

`join.py` (permits → parcel → food, liquor, sibling permits), `feed.py` (citywide liquor
and first-inspection feeds). Google pass was inline: Places searchNearby, 35 m radius,
restaurant/cafe/bar/bakery/coffee_shop/meal_takeaway/brewery, 45 calls.
