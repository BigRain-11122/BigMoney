"""r2209 (f): rows whose head slot had also lost its leading pipe.

After the global pass these read "(值丢失) | r1120 | ..." -- a row that no longer
looks like a table row at all. Restore the pipe and name the commit that carries
the line, same convention as the table sweep.
"""
import io
import re
import subprocess

P = "round_reports-bm-c.md"
HEAD = re.compile(r"^(\s*)\(值丢失\)\s*\|")

s = io.open(P, encoding="utf-8", newline="").read()
lines = s.split("\n")


def blame_sha(line_no):
    out = subprocess.run(
        ["git", "blame", "-L", "%d,%d" % (line_no, line_no), "--porcelain", "--", P],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    first = (out.stdout or "").split("\n", 1)[0].strip()
    return first.split(" ")[0][:7] if first else "unknown"


fixed = []
for i, raw in enumerate(lines):
    had_cr = raw.endswith("\r")
    body = raw[:-1] if had_cr else raw
    m = HEAD.match(body)
    if not m:
        continue
    sha = blame_sha(i + 1)
    new = "| (ts-lost · 行由 %s 落盘) |" % sha + body[m.end():]
    lines[i] = new + ("\r" if had_cr else "")
    fixed.append((i + 1, sha))

io.open(P, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("repaired heads:", fixed)

s2 = io.open(P, encoding="utf-8", newline="").read()
rows = [l.rstrip("\r") for l in s2.split("\n") if l.strip()]
print("stray (值丢失) at head:", [i for i, l in enumerate(rows, 1) if l.lstrip().startswith("(值丢失)")])
print("placeholders anywhere:", [i for i, l in enumerate(rows, 1)
                                 if "%s" in l or "%d" in l or "%%" in l])
