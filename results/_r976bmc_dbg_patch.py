# -*- coding: utf-8 -*-
# r976 debug: diagnose the n1_w232_results.json·15:2x chain-leg assert failure.
# Clones the derive, swaps the failing assert for a diagnostic dump, runs it.
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w234bmc_prereg_derive.py", encoding="utf-8").read()
needle = 'assert t.count("n1_w232_results.json\u00b715:2x") == 1'
alt = 'assert t.count("n1_w232_results.json·15:2x") == 1'
diag = '''
import re as _re
for _tok in ["n1_w232_results.json·15:2x", "n1_w233_results.json·15:2x",
             "n1_w2@L32@_results.json", "n1_w231_results.json·13:2x",
             "n1_w233_results.json·19:5x", "@L32@", "n1_@u_w@_results"]:
    _c = t.count(_tok)
    print(f"DBG[{_tok}] x{_c}")
    for _m in list(_re.finditer(_re.escape(_tok), t))[:3]:
        print("   ctx:", t[max(0, _m.start()-80):_m.end()+40].replace("\\n", " | "))
sys.exit(0)
'''
target = needle if needle in src else (alt if alt in src else None)
assert target, "failing assert line not found in derive"
dbg = src.replace(target, diag, 1)
open(r"results\_w234bmc_prereg_derive_dbg.py", "w", encoding="utf-8", newline="").write(dbg)
print("dbg clone written")
