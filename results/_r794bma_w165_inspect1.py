# -*- coding: utf-8 -*-
"""r794 bm-a: inspect the derived W165 face_probe band sites for the
trailing-comma lookahead miss."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

s = io.open(r"results/_r794bma_w165_face_probe.py", encoding="utf-8").read()
for m in re.finditer(r"1[5-7][0-9]: \{.{0,40}", s):
    print("ROW:", m.group(0))
print("---tuple sites:")
for m in re.finditer(r"\(3\d{2}_\d{3}, 3\d{2}_\d{3}\)", s):
    print(m.group(0))
print("---dotted values followed by a comma (should have advanced):")
for m in re.finditer(r"3\d{2}_\d{3},", s):
    print(m.group(0))
