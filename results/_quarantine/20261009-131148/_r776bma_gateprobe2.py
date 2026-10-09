# -*- coding: utf-8 -*-
"""Seed band values + closed families content for prereg drafting."""
import json
import sys

sys.path.insert(0, "scripts")
import science_gates  # noqa: E402

sr = science_gates.SEED_REGISTRY
for k in sorted(sr.keys()):
    v = sr[k]
    print(k, "->", json.dumps(v, ensure_ascii=False)[:160])

print("===CLOSED_FAMILIES===")
print(json.dumps(science_gates.CLOSED_FAMILIES, ensure_ascii=False, indent=1)[:2800])
