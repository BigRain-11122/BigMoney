# -*- coding: utf-8 -*-
"""T-173 prereg freeze prep: seed bands + closed-family theme hits + gate names."""
import json
import re
import sys

sys.path.insert(0, "scripts")
import science_gates  # noqa: E402

sr = getattr(science_gates, "SEED_REGISTRY", None)
if isinstance(sr, dict):
    keys = sorted(sr.keys(), key=lambda x: int(x) if str(x).isdigit() else 0)
    print("seed bands (tail):", keys[-12:])
else:
    print("SEED_REGISTRY type:", type(sr))

cf = getattr(science_gates, "CLOSED_FAMILIES", None)
s = json.dumps(cf, ensure_ascii=False, default=str)
print("CLOSED_FAMILIES json len:", len(s))
for m in re.finditer(r"[A-Za-z0-9_\-]*[Tt]heme[A-Za-z0-9_\-]*", s):
    print("THEME-HIT:", m.group(0)[:80])

# gate function availability
for name in ("g1_prime_v2", "g2_registration_v2", "t_from_sharpe", "m1_t_value_gate",
             "append_ledger", "cutoff_meta", "closed_family_check"):
    print(name, hasattr(science_gates, name))
