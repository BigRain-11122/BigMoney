# -*- coding: utf-8 -*-
"""R345 bm-a probe: seed registry keys + W2A pool entry structure (read-only)."""
import io, json, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = io.open("scripts/science_gates.py", encoding="utf-8").read()
for m in re.finditer(r'"(census_fusion[^"]*)"\s*:\s*(\d+)', src):
    print("SEED:", m.group(1), "=", m.group(2))

pool = json.load(io.open("results/runnable_pool.json", encoding="utf-8"))
for e in pool["entries"]:
    if e["id"] == "CENSUS-FUS-S2-W2A":
        print(json.dumps(e, ensure_ascii=False, indent=1))
