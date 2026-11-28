"""r2209: the r2208 row was appended as an unformatted template.

The last row of round_reports-bm-c.md literally starts with "| %s | %d |" and
carries "%%" escapes, i.e. the writer built a format string and never applied
it. A reader sees a broken row. Fix = apply the two substitutions in place
(timestamp from the file's own write time, round 2208), then unescape %%.
"""
import io

P = "round_reports-bm-c.md"
STAMP = "2026-11-28T08:06+08:00"

s = io.open(P, encoding="utf-8", newline="").read()
crlf = "\r\n" in s

lines = s.split("\n")
idx = None
for i in range(len(lines) - 1, -1, -1):
    if lines[i].lstrip("\r").startswith("| %s | %d |"):
        idx = i
        break
if idx is None:
    print("no unformatted row found -- nothing to do")
    raise SystemExit(0)

row = lines[idx]
had_cr = row.endswith("\r")
body = row[:-1] if had_cr else row
body = body.replace("| %s | %d |", "| " + STAMP + " | 2208 |", 1)
body = body.replace("%%", "%")
lines[idx] = body + ("\r" if had_cr else "")
io.open(P, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("fixed row at line", idx + 1, "crlf=", crlf)
