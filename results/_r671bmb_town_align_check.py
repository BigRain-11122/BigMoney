import io, re, json

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r671bmb_town_align_check.txt"
lines = []

b = io.open("town.html", encoding="utf-8", errors="replace").read()
lines.append("town.html bytes=%d" % len(b))

# extract building objects: { id:'xxx', ... label:'xxx', dept:'xxx'
blds = re.findall(r"\{\s*id:'([a-z0-9]+)'.*?label:'([^']*)'", b)
lines.append("buildings found: %d" % len(blds))
for bid, label in blds:
    lines.append("  bld id=%s label=%s" % (bid, label))

depts = re.findall(r"dept:'([^']*)'", b)
lines.append("dept strings: %d" % len(depts))
for d in depts:
    lines.append("  dept: %s" % d)

# org_chart v2 department table rows
oc = io.open("firm/org_chart.md", encoding="utf-8", errors="replace").read()
m = re.search(r"## 部门表（.*?）\n(.*?)(?=\n## |\Z)", oc, re.S)
if m:
    tbl = m.group(1)
    rows = [ln for ln in tbl.split("\n") if ln.startswith("|") and "---" not in ln]
    lines.append("org_chart v2 table rows: %d" % (len(rows) - 1))
    for r in rows[1:]:
        cells = [c.strip() for c in r.split("|")]
        if len(cells) > 2:
            lines.append("  org dept: %s" % cells[1])

# footer changelog tail
m2 = re.search(r"org_chart[^<]{0,400}r650", b)
lines.append("footer r650 marker present: %s" % bool(m2))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written")
