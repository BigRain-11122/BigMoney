# -*- coding: utf-8 -*-
"""Append gate_attrition line for THEME_DEEPEN_P1 (append-only, kind=measurement)."""
import json

p = "results/gate_attrition.json"
d = json.load(open(p, encoding="utf-8"))
hist = d["history"]
assert not [h for h in hist if h.get("batch") == "THEME_DEEPEN_P1"], "already"
last = hist[-1]
entry = {
    "batch": "THEME_DEEPEN_P1",
    "ts": "2026-10-06 13:5x",
    "kind": "measurement",
    "retro_fill": False,
    "cells_ledger_delta": 9401,
    "ledger_total_after": 750812,
    "gates": {
        "banned_direction_gate": "ADMIT zero-hit (first-run BAN-04 wording "
                                 "false-hit healed, re-run ADMIT)",
        "d6_vs_reg6": {"max_abs_corr": 0.1638, "any_reject": False},
        "verdicts": {
            "W1": "positive", "W2": "negative", "W3p": "negative",
            "H1_first_wave_advantage": "supported_p=0.0165",
            "H2_confirmation_edge": "negative_p=0.082",
        },
        "expansion_attrition": "6/8 dropped (5 no-ignition-in-window genuine "
                               "strictness + 1 pre-bars), 2 computed",
    },
    "note": "T-2026-10-06-173-P1 r776 bm-a; prereg research/THEME_DEEPEN_P1_PREREG.md "
            "freeze 66d5ec5d4; wave-position retail-follow judgment face + "
            "introduction-taxonomy descriptive census",
}
hist.append(entry)
d["history"] = hist
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("appended; history len:", len(hist))
