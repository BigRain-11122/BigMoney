# -*- coding: utf-8 -*-
"""One-off: add the pf row-key literal bump to the W310 gen map."""
import io

p = "results/_w310bmc_gen_patch.py"
s = io.open(p, encoding="utf-8").read()
anchor = "    ('309: {\"batch\"', '310: {\"batch\"'),\n"
assert anchor in s, "anchor missing"
s = s.replace(anchor, anchor + "    ('309: {{\"a\"', '310: {{\"a\"'),\n")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")