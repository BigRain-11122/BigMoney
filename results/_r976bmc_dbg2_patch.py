# -*- coding: utf-8 -*-
# r976 debug v2: dump the derived t (pre-assert-fail state) for inspection.
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"results\_w234bmc_prereg_derive.py", encoding="utf-8").read()
needle = 'assert t.count("n1_w232_results.json·15:2x") == 1'
assert needle in src, "assert line not found"
diag = 'open(r"results\\_w234bmc_dbg_out.md", "w", encoding="utf-8", newline="").write(t)\nprint("DBG t dumped, bytes:", len(t.encode("utf-8")))\nimport sys as _s2; _s2.exit(0)'
dbg = src.replace(needle, diag, 1)
open(r"results\_w234bmc_prereg_derive_dbg2.py", "w", encoding="utf-8", newline="").write(dbg)
print("dbg2 written")
