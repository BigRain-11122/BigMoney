# -*- coding: utf-8 -*-
"""r417 bm-b: W1-W5 sec.7/8 backfill truth-source extraction (read-only)."""
import json
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = r"E:\Fluxgroup\FluxGroup\quant\bigmoney\results"


def load(p):
    return json.load(io.open(os.path.join(R, p), encoding="utf-8"))


# null family cross-check: seeds + first rates (W1-W3 identical p95 probe)
for n in (1, 2, 3):
    s = load(f"trial_labor_w{n}/w{n}_screen.json")
    nf = s["null_family"]
    seed = nf.get("seed")
    rates = nf["rates"][:4]
    print(f"W{n} seed={seed} rates[:4]={rates} p95={nf.get('p95_line')} median={nf.get('median')}")

for n in (1, 2, 3, 4, 5, 6):
    j = load(f"trial_labor_w{n}/w{n}_judge.json")
    tl = j.get("trials_ledger", {})
    nw = j.get("n_wave_disclosure", {})
    print(f"--- W{n} judge: n_judged={j['n_judged_cells']} n_eligible_g2={j.get('n_eligible_g2')}")
    print("    trials_ledger:", json.dumps(tl, ensure_ascii=False)[:240])
    print("    n_wave_disclosure:", json.dumps(nw, ensure_ascii=False)[:300])
    fp = j.get("family_pbo", {})
    print("    family_pbo:", json.dumps(fp, ensure_ascii=False)[:220])
    ds = j.get("descriptive_summary", {})
    if ds:
        print("    descriptive_summary:", json.dumps(ds, ensure_ascii=False)[:260])
    # best cell by sharpe_full among cells
    cells = j.get("cells", [])
    if cells:
        best = max(cells, key=lambda c: c.get("sharpe_full", -99) if isinstance(c.get("sharpe_full"), (int, float)) else -99)
        keys = [k for k in best.keys()][:14]
        print("    best-cell keys:", keys)
        print("    best-cell:", json.dumps({k: best.get(k) for k in ("candidate_id", "sharpe_full", "skill_line", "line_ok", "dsr", "n_trials", "g1_pass", "g2_eligible", "module") if k in best}, ensure_ascii=False)[:300])
    intake = load(f"trial_labor_w{n}/w{n}_intake.json")
    print("    intake:", json.dumps({k: intake.get(k) for k in ("n_eligible", "n_registered", "registered", "verdict") if k in intake}, ensure_ascii=False)[:300])
    print("    intake keys:", list(intake.keys())[:12])
