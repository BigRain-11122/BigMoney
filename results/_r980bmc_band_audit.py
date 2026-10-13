# -*- coding: utf-8 -*-
# r980 probe: list all variable band f-strings and W6 usages in the generator
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_r977bmc_r35gen.py", encoding="utf-8").read()
for m in re.finditer(r'f"[^"]*\{(A0|A1|B0|B1)[^"]*"', src):
    print(repr(m.group(0)))
print("---W6 usage---")
for m in re.finditer(r'.{15}W6[AB].{30}', src):
    print(repr(m.group(0)))
