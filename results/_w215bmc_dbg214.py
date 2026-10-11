# -*- coding: utf-8 -*-
# Debug: replicate derive stages A-C + D prefix shifts, list remaining bare 214 contexts.
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
src = io.open(r"results\_w215bmc_editor_derive.py", encoding="utf-8").read()
head = src.split("# ---------------- STAGE D")[0]
# strip the trailing io.open/py_compile writes and post-checks (they live after STAGE D anyway)
ns = {}
exec(head, ns)
t = ns["t"]
for p in ("PERPETUAL-N1-W214", "PERPETUAL_N1_W214", "n1w214", "n1_w214", "_w214bmc", "w214_", "W214"):
    t = t.replace(p, p.replace("214", "215"))
ctx = [t[max(0, m.start() - 36):m.start() + 8].replace("\n", "/") for m in re.finditer("214", t)]
print("remaining bare-214:", len(ctx))
for c in ctx:
    print(c)
