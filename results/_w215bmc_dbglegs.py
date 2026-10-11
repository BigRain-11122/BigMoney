# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding="utf-8")
t = io.open(r"results\_w215bmc_freeze_edits.py", encoding="utf-8").read()
s214 = 'assert pf.N1_BANDS[214] == {{"a": ({fmt(pf_mod.N1_BANDS[214]["a"][0])})'
s213 = 'assert pf.N1_BANDS[213] == {{"a": ({fmt(pf_mod.N1_BANDS[213]["a"][0])})'
print("count214:", t.count(s214))
print("count213:", t.count(s213))
i = t.find("w213_leg = [")
print(repr(t[i:i+260]))
