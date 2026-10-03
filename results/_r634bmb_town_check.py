"""r634 bm-b town.html vs org_chart v2 alignment check (queued small task).

Read-only probe: extract department rows from firm/org_chart.md v2 table
and building/landmark titles from town.html; diff names; report to JSON.
"""
import json
import re

oc = open(r"firm/org_chart.md", encoding="utf-8").read()
th = open(r"town.html", encoding="utf-8").read()

rows = re.findall(r"^\|(.*)$", oc, re.M)
depts = []
for r in rows:
    cells = [c.strip() for c in r.split("|")]
    if (
        len(cells) >= 3
        and cells[0]
        and not set(cells[0]) <= set("- ")
        and cells[0] not in ("部门", "层级", "层级/部门")
    ):
        depts.append(cells[0])

# town.html building labels: canvas text() calls + info-panel titles
h = re.findall(r"<h[23][^>]*>([^<]+)</h[23]>", th)
attrs = re.findall(r'title="([^"]+)"', th)
btns = re.findall(r"<button[^>]*>([^<]{2,30})</button>", th)
canvas_labels = re.findall(r"text\('([^']+)'", th)
info_titles = re.findall(r"i-title[^\n]*?\n?[^\n]*", th)
draw_fns = re.findall(r"function (draw\w+)", th)

out = {
    "org_depts": depts,
    "canvas_text_labels": canvas_labels,
    "draw_functions": draw_fns,
    "town_buttons": btns,
}
open(r"results/_r634bmb_town_check.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1)
)
print("written")
