# -*- coding: utf-8 -*-
"""r417 bm-b: extract per-wave judge G1 counts, skill lines, event timestamps (read-only)."""
import json
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"E:\Fluxgroup\FluxGroup\quant\bigmoney\results"


def load(p):
    return json.load(io.open(os.path.join(R, p), encoding="utf-8"))


for n in (1, 2, 3, 4, 5, 6):
    s = load(f"trial_labor_w{n}/w{n}_screen.json")
    j = load(f"trial_labor_w{n}/w{n}_judge.json")
    cells = j.get("cells", [])
    g1_pass = sum(1 for c in cells if c.get("g1_pass"))
    g2_elig = sum(1 for c in cells if c.get("g2_eligible"))
    # skill line + best sharpe
    best = None
    line_val = None
    for c in cells:
        g1 = c.get("g1_prime_v2") or {}
        lv = g1.get("line") or g1.get("skill_line")
        if isinstance(lv, (int, float)) and (line_val is None or lv > line_val):
            line_val = lv
        sf = c.get("legL_sharpe_full")
        if isinstance(sf, (int, float)) and (best is None or sf > best[1]):
            best = (c.get("candidate_id"), sf, g1.get("line_ok"), g1.get("skill_line"))
    print(f"W{n}: screen_generated={s.get('generated')} judge_generated={j.get('generated')} "
          f"n_judged={len(cells)} g1_pass={g1_pass} g2_eligible={g2_elig}")
    print(f"    best-cell: {best}")
    # descriptive clauses compact
    ds = j.get("descriptive_summary", {})
    if ds:
        cl = ds.get("clauses", {})
        compact = {k: f"{v.get('n_true')}/{v.get('n_evaluable')}" for k, v in cl.items()}
        print("    clauses:", json.dumps(compact, ensure_ascii=False))
