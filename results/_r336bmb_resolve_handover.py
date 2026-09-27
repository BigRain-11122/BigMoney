# -*- coding: utf-8 -*-
"""r336 bm-b HANDOVER anchor-insert resolution (r210 law): origin-first-lander (bm-a r340
row) keeps tail slot; later-comer (bm-b r335 row, 17:4x < r340 17:5x) inserts its increment
immediately BEFORE the origin row. Both rows verbatim, no whole-line overwrite, no
number-grabbing. Byte-safe via python (r209: no PS redirection on encoding-sensitive files)."""
import io
import re
import subprocess
import sys

P = "research/HANDOVER.md"
data = open(P, "rb").read()
if b"<<<<<<<" not in data:
    print("no markers present -- nothing to do"); sys.exit(0)

eol = b"\r\n" if data.count(b"\r\n") >= (data.count(b"\n") - data.count(b"\r\n")) and data.count(b"\r\n") > 0 else b"\n"
m = re.search(rb"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*", data, re.S)
assert m, "conflict block not found"
head_block, theirs_block = m.group(1), m.group(2)
assert b"round 340 bm-a" in head_block, "HEAD side must be origin-first-lander bm-a r340 row"
assert b"round 335 bm-b" in theirs_block, "theirs side must be bm-b r335 row"
resolved = theirs_block + eol + head_block          # later-comer increment inserted before origin-lander row
out = data[: m.start()] + resolved + data[m.end():]
for marker in (b"<<<<<<<", b"=======", b">>>>>>>"):
    assert marker not in out, f"marker {marker} leaked"
# both rows survive, order = 335 (17:4x) then 340 (17:5x)
assert out.find(b"round 335 bm-b") < out.find(b"round 340 bm-a") + 40 or True
i335 = out.find(b"*round 335 bm-b")
i340 = out.find(b"**round 340 bm-a")
assert i335 != -1 and i340 != -1 and i335 < i340, "row order violated"
with io.open(P, "wb") as f:
    f.write(out)
r = subprocess.run(["git", "add", "--", P], capture_output=True)
assert r.returncode == 0, r.stderr.decode()
eol_name = "CRLF" if eol == b"\r\n" else "LF"
print(f"HANDOVER anchor-insert OK: bm-b r335 row inserted before origin-lander bm-a r340 row; "
      f"file {len(data)}B -> {len(out)}B (eol={eol_name})")
