# -*- coding: utf-8 -*-
"""r251 bm-c W13 berth drafting: SEED_REGISTRY live tail-read (collision pre-check, read-only)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "scripts")
import science_gates as sg

reg = {k: v for k, v in dict(sg.SEED_REGISTRY).items() if isinstance(v, int)}
items = sorted(reg.items(), key=lambda kv: kv[1])
print("registry entries:", len(reg))
print("max value:", items[-1][1])
for k, v in items[-10:]:
    print(" ", k, "=", v)
w13_hits = [k for k in reg if "w13" in k.lower()]
print("existing w13 keys:", w13_hits)
