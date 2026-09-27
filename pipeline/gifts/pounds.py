"""Pounds, Fargo — the menu only exists as nine pictures; type it up and make a table copy.

Evidence:
  - poundsfargo.com/menu is 9 JPEGs (MENU2026-01..08, PoundsChicken, SaladfixMENU2024-05,
    broadwayBEERlist). The page has 92 words of text, none of them a dish. A phone reader,
    Google, and every AI assistant see no menu at all.
  - 5 Google reviews (2022-24) complain there is no physical menu, only a QR code ("They don't have
    physical menus; you scan a QR code").
Transcribed by reading each image on 2026-09-26. Their spelling kept as printed.
"""
from __future__ import annotations

from common import esc, page, save_plan

SLUG = "pounds"

# (section, note, [(name, what's on it, price)])
MENU = [
    ("Burgers", "comes with Pounds fries", [
        ("The Grail", "smoked gouda, bacon slices, wavy sauce, caramelized onions, shredded lettuce", "15.59"),
        ("Basic B", "'merican cheese, bacon slices, ketchup, mustard, dill pickles", "14.99"),
        ("The Hangover", "over easy egg, chedda cheese, bacon, house fries, ketchup", "15.79"),
        ("Supa Sunset", "pulled pork, bacon, pepperjack, crispy fried onions, topped with Dr Pepper BBQ", "16.79"),
        ("Big Mac N' Chz", "cheddar, wavy sauce, lettuce, dill pickles, topped with mac n' chz", "15.59"),
        ("Californication", "avo smash, lettuce, tomatoes, onions, topped with zesty avo ranch", "15.79"),
        ("Blaze It (hot)", "pepper jack, bacon, jalapeños, crispy fried onions, torch sauce", "15.99"),
    ]),
    ("Good Ass Chicken Sandwiches", "on a Martin's potato roll, comes with fries", [
        ("O.G.", "juicy house made breaded chicken breast, dill pickle chips, mayo", "14.29"),
        ("Spicy", "spicy dusted breaded chicken breast, dill pickle chips, mayo", "14.79"),
        ("SoCal", "breaded chicken breast, lettuce, sliced tomato, onion, hunny musturd", "14.79"),
        ("Dilly", "breaded chicken breast, extra dill pickle chips, pickle ranch", "14.79"),
        ("Rancher", "breaded chicken breast, bacon, cheddar, ranch", "15.29"),
    ]),
    ("Sandwiches", "comes with Pounds fries", [
        ("Da Club 2.0", "roasted pulled chicken, bacon, cheddar, gouda, avocado smash, lettuce, tomato, hunny mustard. On toasted sour dough", "14.79"),
        ("Chicken Tendie Melt", "chicken tenders, bacon, cheddar, tomato, dr. pepper bbq. On toasted sour dough", "14.29"),
        ("Piggy Smalls", "pulled pork, dr. pepper bbq, crispy onions, dill pickles. On a Martin's potato roll", "14.59"),
        ("CBA", "roasted pulled chicken, cheddar, bacon, avocado, tomato, zesty avocado ranch, lettuce. On a Martin's potato roll", "14.29"),
    ]),
    ("Tendy Tango & Wings", "", [
        ("Tendy Tango", "3 house buttermilk soaked crispy tenders, choice of dipper, comes with Pounds fries", "13.79"),
        ("Pounds Wings, 5", "house prepared prime chicken wings, sauce on the side to keep 'em crispy", "9.59"),
        ("Pounds Wings, 12", "sauces: Dr Pepper BBQ, hunny mustard, bomb buffalo (hot), torch sauce (hottest), sweeter chili lime", "17.89"),
    ]),
    ("Loaded Mac & Cheese", "house mac sauce: cream cheese, gouda, cheddar, white american", [
        ("3D Cheese", "topped with cheddar and a mini grilled cheese", "13.79"),
        ("Everything Bagel", "parmesan, toasted bread crumbs, chives, everything bagel seasoning", "13.79"),
        ("Chicken Truffle Mac", "roasted pulled chicken, truffle parmesan, toasted bread crumbs", "14.29"),
        ("Chicken Bacon Ranch", "crispy chicken & bacon, shredded cheddar, buttermilk ranch", "14.59"),
        ("Gooda Mac", "crispy chicken, gouda, crispy onions, wavy sauce", "14.29"),
        ("BBQ Porker", "house pulled pork, diced pickled jalapeños, dr. pepper BBQ", "14.29"),
        ("Buff Ranch Mac (hot)", "crispy chicken, parmesan, chives, buff ranch", "14.59"),
    ]),
    ("Hippie Bowls", "more healthy than not. Base of coconut lime rice & mixed root vegetables", [
        ("Te Amo", "corn & black bean salsa, avocado smash, tomatoes, chives, cholou lime sour cream", "13.79"),
        ("Yin and Yang", "sesame seeds, avocado smash, kimchi, chives, sweeter chili sauce", "13.79"),
        ("Barbequtie", "roasted pulled chicken, diced pickled jalapeños, crispy onions, dr. pepper BBQ", "13.79"),
        ("Chickaboom", "roasted pulled chicken, shredded parmesan, chives, buff ranch", "13.79"),
        ("Strawbs Salad", "kale blend, strawberries, roasted sunflower seeds, onions, strawberry blush vinaigrette", "side 4.79 / full 8.79"),
        ("Trusty Salad", "iceberg lettuce, tomatoes, sunflower seeds, onions, cheddar", "side 4.79 / full 8.79"),
    ]),
    ("Bites", "mix & match starters: 1 for 7.50, 2 for 14.00, 3 for 18.00", [
        ("Duo Fries", "crispy house fries and seasoned curly fries, with ranch", ""),
        ("Grilled Cheese Stix", "thicc sour dough, melty cheddar, american, creamy tomato soup", ""),
        ("Pickle Fries", "breaded fried dill pickle spears, zesty avocado ranch", ""),
        ("Chicken Tendies", "3 house buttermilk soaked crispy tenders, wavy sauce", ""),
        ("Poutine", "crispy house fries, Wisconsin cheese curds, rich brown gravy. Add pulled pork 3.79", ""),
        ("Queso Fries (new)", "crispy house fries, corn & bean queso, cholou lime sour cream, chives", ""),
    ]),
    ("Add-ons & upgrades", "", [
        ("Add to any mac or bowl", "pulled or crispy chicken, pulled pork, or smoky bacon", "+3.79"),
        ("Swap your fries", "parm truff fries +1 · curly fries +1.29 · sweet potato fries +1.29 · mac & cheese +3 · mixed veggies +3 · coconut lime rice +2.5", ""),
        ("Gluten free bun", "", "+2.50"),
        ("Beyond patty", "on any burger", "+2.50"),
        ("Ranch flight", "zesty avocado, buff ranch, jalapeño cheddar, pickle", "+2.99"),
    ]),
    ("Sides", "Pounds fries · parm truffle fries · curly fries · sweet potato fries · mac and cheese · coconut lime rice · mixed root veg", []),
    ("Dippers", "wavy sauce · Dr Pepper BBQ · hunny mustard · bomb buffalo (hot) · torch sauce (hottest) · sweeter chili lime · boring ranch · zesty avocado ranch · buff ranch · jalapeño cheddar ranch (hot) · pickle ranch", []),
    ("Fruitopias", "fruit & sunshine, 5.99", [
        ("Strawberry Nanner", "rum, sour, strawberry & banana purée, lemon", ""),
        ("Cherry Lime Cooler", "cherry vodka, cherry syrup, sprite & sour", ""),
        ("Whiskey Peach Wave", "whiskey, sour, peach purée, lemonade", ""),
        ("Mangoberry Zing", "tequila, triple sec, sour, mango & berry purée, chili lime", ""),
        ("Strawberry Mango Fresh", "vodka, strawberry liquor, mango purée, lemonade", ""),
        ("Huckleberry Ginn", "ginn, sour, lemonade, huckleberry purée", ""),
        ("Berry Marg Blast", "tequila, triple sec, sour, wild berry purée", ""),
    ]),
    ("Tipsy Teas & more", "", [
        ("Tipsy Teas", "Longer Island · Sourberry Snap · Sour Raz · Tropical Island · Peachy Keen", "5.99"),
        ("Spiked Capri Sun", "Tito's vodka and lime", "5.79"),
    ]),
    ("Keg beer", "tall or shorty", [
        ("House", "Coors Light lager 4.2% · Kona Big Wave golden ale 4.4% · Modelo mexican lager 4.5%", ""),
        ("Taps from near here", "Modist Supra Deluxe lager 5.0% · Drekker Purple People Eater fruited sour 5.5% · Sierra Nevada Juicy Little Thing IPA 6.5% · 1911 pineapple mango cider 6.9% · Drekker Broken Rudder 5.0% · Grain Belt Blu blueberry lager 4.7% · Indeed pistachio cream ale 5.5% · Bemidji autumn IPA 7.0% · Blakes Triple Jam 6.5%", ""),
        ("Cans", "Drekker 16oz: Ectogasm juicy hazy IPA, Techno Viking sour pilsner · High Noon 12oz peach or pineapple", ""),
        ("Fortys", "Coors Light or Bud Light, 40oz bottle", ""),
    ]),
]


def section_html(name, note, items, compact=False):
    rows = "".join(
        f'<div class="item"><div class="row"><b>{esc(n)}</b><span>{esc(p)}</span></div>'
        f'{f"<div class=meta>{esc(d)}</div>" if d else ""}</div>' for n, d, p in items)
    return f'<section><h2>{esc(name)}</h2>{f"<p class=meta>{esc(note)}</p>" if note else ""}{rows}</section>'


CSS = """
.item{padding:.45rem 0;border-bottom:1px solid var(--line)}
.row{display:flex;justify-content:space-between;gap:1rem;font-family:ui-sans-serif,system-ui,sans-serif}
.row span{white-space:nowrap;color:var(--mute)}
.jump{display:flex;flex-wrap:wrap;gap:.4rem;margin:.8rem 0}
.jump a{font:14px ui-sans-serif,system-ui,sans-serif;border:1px solid var(--line);border-radius:999px;padding:.3rem .7rem;color:inherit;text-decoration:none}
"""

PRINT_CSS = """
@page{size:letter;margin:.45in}
body{background:#fff;color:#111;font-size:11px}
.wrap{max-width:none;padding:0}
.cols{column-count:3;column-gap:.3in}
section{break-inside:avoid;margin-bottom:.12in}
h1{font-size:22px;margin:0 0 4px}
h2{font-size:13px;margin:6px 0 2px;text-transform:uppercase;letter-spacing:.06em}
.item{padding:2px 0;border:0}
.row{font-size:11px}.meta{font-size:10px}
@media screen{.wrap{max-width:60rem;padding:1rem}}
"""


def main() -> None:
    jump = "".join(f'<a href="#s{i}">{esc(n)}</a>' for i, (n, _, _) in enumerate(MENU))
    secs = "".join(section_html(n, note, items).replace("<section>", f'<section id="s{i}">', 1)
                   for i, (n, note, items) in enumerate(MENU))
    body = f"""
<p class="meta">6 Broadway N, Fargo · <a href="tel:+17014781234">701-478-1234</a> · Mon–Thu 11am–10pm · Fri–Sat 11am–12am · Sun closed</p>
<h1>Pounds menu</h1>
<p class="lede">The whole menu, in words, so it loads on any phone and Google can read it.</p>
<p class="noprint"><a class="btn" href="print/">Printable table menu</a></p>
<nav class="jump noprint">{jump}</nav>
{secs}
<p class="meta">Typed from the menu pictures on poundsfargo.com/menu, September 26, 2026. Prices as printed there.</p>
"""
    strip = "Typed up for Pounds by Brick &amp; Mortar from the menu pictures on your own website. Nothing on your site was changed."
    page(SLUG, "Pounds menu — Fargo", body, strip=strip, css=CSS)
    pbody = f"""<h1>Pounds</h1><p class="meta">6 Broadway N, Fargo · 701-478-1234 · poundsfargo.com</p>
<div class="cols">{''.join(section_html(n, note, items) for n, note, items in MENU)}</div>"""
    page(SLUG, "Pounds — table menu", pbody, sub="print",
         strip='Print this page (letter, 2 sides). <a href="../">Back</a>', css=CSS + PRINT_CSS)
    n_items = sum(len(i) for _, _, i in MENU)
    save_plan(SLUG, {
        "slug": SLUG, "headline": "We typed up your menu, so it isn't only pictures, and made a table copy you can print.",
        "gift_path": f"/{SLUG}/", "print_path": f"/{SLUG}/print/",
        "evidence": ["poundsfargo.com/menu is 9 images and no menu text",
                     "5 Google reviews (2022-2024) complain there is no physical menu, only a QR code; one liked it",
                     f"{n_items} items transcribed"],
        "to_use_it": "Print the table menu from the button on the page. Link the page from Instagram or your QR code.",
        "menu": ["online_ordering", "gbp_cleanup", "review_replies_monthly"],
    })
    print("built", SLUG, n_items, "items")


if __name__ == "__main__":
    main()
