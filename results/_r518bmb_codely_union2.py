# -*- coding: utf-8 -*-
raw = open("CODELY.md", "rb").read().decode("utf-8")
lines = raw.split("\n")
strip = lambda l: l.rstrip("\r")
opens = [i for i, l in enumerate(lines) if strip(l).startswith("<<<<<<< ")]
closes = [i for i, l in enumerate(lines) if strip(l).startswith(">>>>>>> ")]
seps = [i for i, l in enumerate(lines) if strip(l) == "======="]
assert len(opens) == 1 and len(closes) == 1
oi, ci = opens[0], closes[0]
mid = [s for s in seps if oi < s < ci][0]
head_side = lines[oi + 1: mid]     # bm-c r330 two entries (19:2x)
mine_side = lines[mid + 1: ci]     # [blank?, r532 bm-a, my r518 lesson]
# classify mine-side lines
r532 = [l for l in mine_side if "r532 bm-a" in l]
r518 = [l for l in mine_side if "r518 bm-b" in l]
blank = [l for l in mine_side if strip(l) == ""]
others = [l for l in mine_side if l not in r532 and l not in r518 and l not in blank]
assert not others, f"unexpected mine-side lines: {others[:2]}"
assert len(head_side) == 2 and all("r330 bm-c" in l for l in head_side)
# chronological union: r532 (19:1x) < r330 (19:2x) < r518 (19:3x)
resolved = lines[:oi] + r532 + head_side + r518 + lines[ci + 1:]
for l in resolved:
    s = strip(l)
    assert not (s.startswith("<<<<<<< ") or s.startswith(">>>>>>> ") or s == "======="), "marker remains"
out = "\n".join(resolved)
assert out.count("r518 bm-b") >= 2 and "r330 bm-c" in out and "r532 bm-a" in out
open("CODELY.md", "w", encoding="utf-8", newline="").write(out)
import subprocess
subprocess.run(["git", "add", "CODELY.md"], check=True)
print("CODELY union v2 done: r532 + r330x2 + r518-lesson, all preserved")
