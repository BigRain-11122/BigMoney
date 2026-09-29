# -*- coding: utf-8 -*-
"""r438 bm-b: fix the 2969->2970 arithmetic slip in w10 runner text
faces (3344 - 374 = 2970; anchor dict itself already generated 2970)."""
p = "scripts/trial_labor_w10.py"
t = open(p, encoding="utf-8").read()
n = (t.count("2,969") + t.count("closed 2969")
     + t.count('rmeta["closed_days"] == 2969'))
t = t.replace("2,969", "2,970")
t = t.replace("closed 2969", "closed 2970")
t = t.replace('rmeta["closed_days"] == 2969',
              'rmeta["closed_days"] == 2970')
open(p, "w", encoding="utf-8", newline="\n").write(t)
print("replaced", n, "occurrences")
