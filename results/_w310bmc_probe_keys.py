# -*- coding: utf-8 -*-
"""Probe: which pf row-key literals exist in the W309 splice editor."""
import io

s = io.open("results/_w309bmc_freeze_edits.py", encoding="utf-8").read()
keys = ['309: {{"a"', '309: {"a"', '308: {{"a"', '308: {"a"']
print({k: s.count(k) for k in keys})
g = io.open("results/_w310bmc_gen_patch.py", encoding="utf-8").read()
print("gen has F-I-F-T-H key:", "HUNDRED-AND-TWENTY-FIFTH" in g)