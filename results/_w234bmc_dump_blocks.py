# -*- coding: utf-8 -*-
# r976 helper: dump exact STALE/NEW block source text from committed W233 tpl.
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
t = open(r"results\_w233bmc_prereg_derive_tpl.py", encoding="utf-8").read()

def block(varname):
    i = t.index(varname + " = [")
    j = t.index("]\n", i) + 2
    return t[i:j]

stale_src = block("STALE")
new_src = block("NEW")
open(r"results\_w234bmc_stale_src.txt", "w", encoding="utf-8", newline="").write(stale_src)
open(r"results\_w234bmc_new_src.txt", "w", encoding="utf-8", newline="").write(new_src)
print("stale block bytes:", len(stale_src.encode("utf-8")), "| new block bytes:", len(new_src.encode("utf-8")))
print("--- STALE src ---")
print(stale_src)
print("--- NEW src ---")
print(new_src)
