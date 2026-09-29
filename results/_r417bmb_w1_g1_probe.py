# -*- coding: utf-8 -*-
"""r417 bm-b: W1 g1_pass=true cells deep-dive (read-only truth probe)."""
import json
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
j = json.load(io.open(r"E:\Fluxgroup\FluxGroup\quant\bigmoney\results\trial_labor_w1\w1_judge.json", encoding="utf-8"))
cells = j["cells"]
passes = [c for c in cells if c.get("g1_pass")]
print("g1_pass=true count:", len(passes))
for c in passes:
    g1 = c.get("g1_prime_v2", {})
    print("=" * 10, c["candidate_id"])
    print("  legL_sharpe_full:", c.get("legL_sharpe_full"), "n_trades:", c.get("legL_n_trades"), "n_entries:", c.get("legL_n_entries"))
    print("  sample_sufficient:", c.get("sample_sufficient"))
    print("  verdict:", c.get("verdict"))
    print("  g1_prime_v2:", json.dumps({k: g1.get(k) for k in ("line", "line_ok", "ci_ok", "trade_gate", "entries_ok", "sharpe_full")}, ensure_ascii=False))
    print("  dsr:", json.dumps(c.get("dsr"), ensure_ascii=False)[:160])
    print("  dual_nulls:", json.dumps(c.get("dual_nulls"), ensure_ascii=False)[:200])
    segs = c.get("n_eff_start_windows") or c.get("legs")
    if isinstance(segs, dict):
        print("  n_eff_start_windows:", json.dumps(segs, ensure_ascii=False)[:220])
# top-level summary if any
for k in j.keys():
    if "summary" in k or "pass" in k or "verdict" in k:
        print("TOP", k, "=", json.dumps(j[k], ensure_ascii=False)[:300])
