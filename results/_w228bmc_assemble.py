# -*- coding: utf-8 -*-
# Assemble _w228bmc_prereg_derive.py = head + generated SUB block + tail.
import py_compile, sys
sys.stdout.reconfigure(encoding="utf-8")
head = open(r"results\_w228bmc_head.py", encoding="utf-8").read()
sub = open(r"results\_w228bmc_sub_block.py", encoding="utf-8").read()
tail = open(r"results\_w228bmc_tail.py", encoding="utf-8").read()
out = head.rstrip("\n") + "\n\n# ---------- per-pair submaps: index -> ordered (find, replace) ----------\n" + sub.rstrip("\n") + "\n" + tail
open(r"results\_w228bmc_prereg_derive.py", "w", encoding="utf-8", newline="").write(out)
py_compile.compile(r"results\_w228bmc_prereg_derive.py", doraise=True)
import os
print("assembled OK:", os.path.getsize(r"results\_w228bmc_prereg_derive.py"), "bytes")
