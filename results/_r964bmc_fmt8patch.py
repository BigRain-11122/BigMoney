# -*- coding: utf-8 -*-
# patch fmt8 assertion to 8-decimal precision (w230-only mu = 0.09077200)
import sys
sys.stdout.reconfigure(encoding="utf-8")
BS = chr(92)
for p in [r"results\_w231bmc_prereg_derive_tpl.py", r"results\_w231bmc_prereg_derive.py"]:
    t = open(p, encoding="utf-8").read()
    old = 'assert fmt8(w230only["mu"]) == "' + BS + 'u2212" + "0.090772", fmt8(w230only["mu"])'
    new = 'assert fmt8(w230only["mu"]) == "' + BS + 'u2212" + "0.09077200", fmt8(w230only["mu"])'
    assert t.count(old) == 1, p
    open(p, "w", encoding="utf-8", newline="").write(t.replace(old, new))
    print("patched", p)
