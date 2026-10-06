# -*- coding: utf-8 -*-
import io
import re

s = io.open("results/_r792bma_w164_freeze_verify.py", encoding="utf-8", newline="").read()
for m in re.finditer(r"(?<![\w\".(])16[2-5](?![\w\".])", s):
    a, b = max(0, m.start() - 55), min(len(s), m.end() + 35)
    print(repr(s[a:b]))
