# -*- coding: utf-8 -*-
# Debug: run the full derive stages and locate surviving PERPETUAL-N1-W214 contexts.
import io, re, sys
sys.stdout.reconfigure(encoding="utf-8")
src = io.open(r"results\_w215bmc_editor_derive.py", encoding="utf-8").read()
body = src.split("# ---------------- STAGE F")[0]
ns = {}
exec(body, ns)
t = ns["t"]
for m in re.finditer("PERPETUAL-N1-W214", t):
    print(repr(t[max(0, m.start() - 100):m.start() + 60]))
print("count:", t.count("PERPETUAL-N1-W214"))
