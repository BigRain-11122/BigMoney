"""r2209 (b): the unformatted-template defect has three more instances upstream.

Fixing only the newest row (r2208) left the same class on three older rows, and
the double-percent escapes (`%%`, what a format string leaves behind when the
writer never applied %) sit on 20+ rows. Both are display defects a reader sees
as broken text, so they are repaired the same way the r2208 row was -- but with
no invented numbers: where the timestamp or round is genuinely gone, the row
says so and names the commit that carries it (precedent: the r1303 row already
reads "(ts-lost, r1303 hygiene repair)").
"""
import io
import re

P = "round_reports-bm-c.md"

PROVENANCE = {
    # line-no (1-based, as of this run) -> (prefix to replace, replacement, commit)
    "| %s | r1432": ("| %s |", "| (ts-lost · 行由 b0e9fe7 落盘) |"),
    "| %s | 1863": ("| %s |", "| (ts-lost · 行由 ea83aea 落盘) |"),
    "| %s | %d |": ("| %s | %d |", "| (ts-lost · 行由 b3cf3e6 落盘) | (round-lost) |"),
}

MINE_OLD = "字面 `| %s | %d |` 加 `%%`"
MINE_NEW = "字面百分号占位行加双百分号"

s = io.open(P, encoding="utf-8", newline="").read()
lines = s.split("\n")

fixed_head = []
fixed_pct = []
mine = 0

for i, raw in enumerate(lines):
    had_cr = raw.endswith("\r")
    body = raw[:-1] if had_cr else raw
    if not body.startswith("|"):
        continue
    changed = False

    for probe, (old, new) in PROVENANCE.items():
        if body.startswith(probe):
            body = new + body[len(old):]
            changed = True
            fixed_head.append((i + 1, new.strip()))
            break

    if "%%" in body:
        n = body.count("%%")
        body = body.replace("%%", "%")
        fixed_pct.append((i + 1, n))
        changed = True

    if MINE_OLD in body:
        body = body.replace(MINE_OLD, MINE_NEW)
        mine += 1
        changed = True

    if changed:
        lines[i] = body + ("\r" if had_cr else "")

io.open(P, "w", encoding="utf-8", newline="").write("\n".join(lines))

print("heads repaired:", fixed_head)
print("rows with %% unescaped:", len(fixed_pct), fixed_pct[:8], "..." if len(fixed_pct) > 8 else "")
print("own row reworded:", mine)

# verify
s2 = io.open(P, encoding="utf-8", newline="").read()
rows = [l.rstrip("\r") for l in s2.split("\n") if l.startswith("|")]
bad_head = [i + 1 for i, l in enumerate(rows) if re.match(r"^\| %", l)]
bad_pct = [i + 1 for i, l in enumerate(rows) if "%%" in l]
print("rows starting with a placeholder:", bad_head)
print("rows still carrying %%:", bad_pct)
print("any %s / %d left in table rows:", [i + 1 for i, l in enumerate(rows) if "%s" in l or "%d" in l])
