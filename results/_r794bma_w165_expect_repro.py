# -*- coding: utf-8 -*-
"""r794 bm-a: replicate the deriver's full pass on the W164 prereg_build tool
and print the derived EXPECT block to adjudicate the zero-count key origin."""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# exec only the pass-table region of the deriver (up to `def generic`)
src = io.open(r"results/_r794bma_w165_deriv_all.py", encoding="utf-8").read()
head = src.split("# tool 1: face_probe")[0]
ns = {}
exec(head, ns)
PH0, PH1, PH2, PH3, SURG = ns["PH0"], ns["PH1"], ns["PH2"], ns["PH3"], ns["SURG"]


def generic(s):
    for a, b in PH0:
        s = s.replace(a, b)
    for a, b in PH1:
        s = s.replace(a, b)
    for a, b in PH2:
        s = s.replace(a, b)
    for a, b in PH3:
        s = s.replace(a, b)
    return s


def apply_surg(s):
    for a, b in SURG:
        s = s.replace(a, b)
    return s


s = io.open(r"results/_r792bma_w164_prereg_build.py", encoding="utf-8").read()
s = generic(s)
s = apply_surg(s)

m = re.search(r"EXPECT = \{.*?\n\}", s, re.S)
print("=== derived EXPECT block (before empirical rebuild) ===")
print(m.group(0))
pairs = re.findall(r'"([^"]+)": (\d+)', m.group(0))
print("=== pairs ===")
for k, old in pairs:
    print(repr(k), "->", old)
