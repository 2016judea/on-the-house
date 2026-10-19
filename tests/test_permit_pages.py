"""The permit and hospitality pages (pipeline/permits/render.py and the scripts that exec its header)
embed their rows as JSON inside a <script>. Scraped text goes in verbatim, so the embed must survive
a "</script>" in a permit description or a business name."""
import json
import os
import re
from pathlib import Path

import pytest

PERMITS = Path(__file__).resolve().parent.parent / "pipeline" / "permits"


@pytest.fixture
def render(monkeypatch):
    # the same header hospitality_render.py, render2.py and render_vendors.py exec (it reads template.html from cwd)
    monkeypatch.chdir(PERMITS)
    ns = {"__file__": str(PERMITS / "render.py")}
    exec((PERMITS / "render.py").read_text().split("# ---------------- Vineland")[0], ns)
    return ns


def test_a_script_closing_tag_in_a_row_cannot_end_the_page_script(render, tmp_path):
    rows = [{"addr": "117 Lake St W", "what": 'Remodel - </script><img src=x onerror="alert(1)"> - Bar & Grill', "by": "O'Neil <Co>"}]
    out = tmp_path / "x.html"
    render["page"](str(out), "{}", rows, {"__TITLE__": "t", "__H1__": "h"})
    html = out.read_text()
    m = re.search(r"const ROWS=(.*?);\n", html)
    assert m, "rows are embedded on the ROWS line"
    assert "</script><img" not in html
    # the browser reads "<\/" as "</": the row round-trips
    assert json.loads(m.group(1)) == rows


def test_js_json_only_touches_the_closing_slash(render):
    assert render["js_json"]({"a": "x</y & <b>"}) == '{"a":"x<\\/y & <b>"}'
