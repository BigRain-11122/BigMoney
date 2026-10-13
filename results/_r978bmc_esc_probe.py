# -*- coding: utf-8 -*-
# r978 probe: find malformed \uXXXX escapes in _r977bmc_r35gen.py (SyntaxError root-cause)
import re
src = open(r"results\_r977bmc_r35gen.py", encoding="utf-8").read()
lines = src.splitlines()
bad = []
for i, l in enumerate(lines, 1):
    for m in re.finditer(r"\\u([0-9a-fA-F]{0,3})(?![0-9a-fA-F])", l):
        bad.append((i, m.start(), l[max(0, m.start() - 40):m.start() + 25]))
for b in bad:
    print(b)
print("bad count", len(bad))
