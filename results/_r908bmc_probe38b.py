# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
t = open(r"research\PERPETUAL_N1_W212_PREREG.md", encoding="utf-8").read()
i = t.find("W136..W211")
j = t.find("\u3011\u3002", i)
phys = t[i:j+2]
print("PHYSICAL VERBATIM:")
print(phys)
print()
print("repr:", repr(phys))
