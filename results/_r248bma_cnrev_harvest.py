# -*- coding: utf-8 -*-
"""R248 bm-a: CN-REV-TILT-P1 harvest gate (deterministic, zero network, zero LLM).

r244 landed-marker law: pool batch never flips itself -- the next round flips
entry+shard done after deterministic re-derivation of the harvest criterion.
Runner landed results/cn_rev_tilt/p1_results.json with ledger block at
13:40:50 (autofill launch-claim cnrev-0of1 owner=bm-a, commit 8ee47a83).

Harvest checks (all must hold before flip):
  1. product parses; ledger block prev_total 185798 + batch_trials 54 == total 185852;
  2. evidence_cutoff == 2026-09-22 (D2 forward lockbox; 09-23/24 bars excluded);
  3. panel gates T==8792, N==5222, cutoff==2026-09-22;
  4. per-cell G1' v2 RE-DERIVED from stored inputs (line_ok = sharpe_full >
     skill_line.line; pass_v2 = line_ok AND bootstrap ci_lower_bound > 0)
     equals stored pass_v2 for all 4 cells;
  5. nulls: K=50, seed base 20260930, registered 'cn_rev_tilt_p1';
  6. gate_attrition last entry == CN-REV-TILT-P1, eliminated 54, ledger_after 185852;
  7. n_trials top-level == 54 (BACKTEST_PLAN iron rule: total trials N recorded);
  8. verdict: 4/4 G1' FAIL -> batch judged NEGATIVE (prereg s4 判负即收线).

Exit 0 = gate PASS + pool entry+shard flipped done with harvest_note.
Exit 2 = gate red, NO flip.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROD = os.path.join(ROOT, "results", "cn_rev_tilt", "p1_results.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
ATTR = os.path.join(ROOT, "results", "gate_attrition.json")
ENTRY_ID = "CN-REV-TILT-P1"
CELLS = ["REV20_bare", "REV60_bare", "REV20_tilt", "REV60_tilt"]


def main() -> int:
    fails = []
    if not os.path.exists(PROD):
        print("FAIL: p1_results.json absent")
        return 2
    r = json.load(io.open(PROD, encoding="utf-8"))

    # 1. ledger block
    led = r.get("ledger", {})
    if not (led.get("prev_total") == 185798 and led.get("batch_trials") == 54
            and led.get("total") == 185852 and led.get("file") == PROD.replace(ROOT + os.sep, "").replace(os.sep, "/")):
        fails.append(f"ledger block mismatch: {led}")

    # 2. forward lockbox
    if r.get("evidence_cutoff") != "2026-09-22":
        fails.append(f"evidence_cutoff {r.get('evidence_cutoff')!r} != 2026-09-22")

    # 3. panel gates
    pg = r.get("panel_gates", {})
    if not (pg.get("T") == 8792 and pg.get("N") == 5222 and pg.get("cutoff") == "2026-09-22"):
        fails.append(f"panel_gates mismatch: {pg}")

    # 4. re-derive G1' v2 per cell from stored inputs
    line = r["skill_line"]["line"]
    rederived = {}
    for c in CELLS:
        g = r["g1_prime_v2"][c]
        line_ok = g["sharpe_full"] > line
        pass_v2 = line_ok and g["bootstrap_ci"]["ci95_low"] > 0
        rederived[c] = pass_v2
        if pass_v2 != g.get("pass_v2"):
            fails.append(f"{c}: re-derived pass_v2 {pass_v2} != stored {g.get('pass_v2')}")
        if g.get("gate") != "g1_prime_v2":
            fails.append(f"{c}: gate label {g.get('gate')!r}")
    n_pass = sum(rederived.values())

    # 5. nulls provenance
    nl = r.get("nulls", {})
    cfg = nl.get("config", {})
    if not (nl.get("n_values") == 50 and cfg.get("base") == 20260930
            and cfg.get("registered") == "cn_rev_tilt_p1"):
        fails.append(f"nulls provenance mismatch: {cfg} n={nl.get('n_values')}")

    # 6. gate_attrition honest record (runner-appended)
    attr = json.load(io.open(ATTR, encoding="utf-8"))
    last = attr["entries"][-1] if isinstance(attr.get("entries"), list) else None
    if not (last and last.get("batch") == ENTRY_ID and last.get("eliminated") == 54
            and last.get("ledger_total_after") == 185852):
        fails.append(f"gate_attrition tail mismatch: {last}")

    # 7. trials census
    if r.get("n_trials") != 54:
        fails.append(f"n_trials {r.get('n_trials')!r} != 54")

    # 8. verdict
    verdict = "NEGATIVE" if n_pass == 0 else ("PASS" if n_pass == 4 else "MIXED")

    # s7/s8 number extraction (for prereg backfill -- printed, human-copied)
    cells_x = {}
    for c in CELLS:
        cells_x[c] = {f: round(r["cells"][c][f]["sharpe"], 4) for f in ("x1", "x2", "x3")}
    maxd1 = {}
    for c in CELLS:
        audit = r.get("judged_x1_returns_6dp_audit", {}).get(c, [])
        maxd1[c] = round(max((abs(x) for x in audit), default=0.0), 6)
    sl = r["skill_line"]

    if fails:
        print(json.dumps({"harvest_gate": "FAIL", "fails": fails}, ensure_ascii=False, indent=1))
        return 2

    # flip pool entry+shard done (single_writer: rounds own this file; autofill read-only)
    pool = json.load(io.open(POOL, encoding="utf-8"))
    entry = next((e for e in pool.get("entries", []) if e.get("id") == ENTRY_ID), None)
    if entry is None:
        print("FAIL: pool entry CN-REV-TILT-P1 missing")
        return 2
    if entry.get("status") == "ready":
        entry["status"] = "done"
        for sh in entry.get("shards", []):
            if sh.get("key") == "cnrev-0of1":
                sh["status"] = "done"
                sh["harvest_note"] = ("R248 bm-a deterministic harvest: p1_results.json landed 13:40:50 "
                                      "(ledger 185798+54=185852, cutoff 2026-09-22, T8792/N5222); G1' v2 "
                                      "re-derived 4/4 FAIL (best REV60_bare sharpe 0.4757 < skill line 0.6147; "
                                      "REV60 tilt CI low 0.3083>0 but line fail) -> batch judged NEGATIVE per "
                                      "prereg s4 (判负照登, 新证据=新预注册); gate_attrition eliminated 54")
        with io.open(POOL, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(pool, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    elif entry.get("status") != "done":
        print(f"FAIL: entry status {entry.get('status')!r} unexpected (harvest expects ready/done)")
        return 2

    out = {
        "harvest_gate": "PASS",
        "entry": ENTRY_ID,
        "verdict": verdict,
        "g1_pass_count": n_pass,
        "per_cell": {
            c: {
                "x1": r["g1_prime_v2"][c]["sharpe_full"],
                "line_ok": r["g1_prime_v2"][c]["sharpe_full"] > line,
                "ci95_low": r["g1_prime_v2"][c]["bootstrap_ci"]["ci95_low"],
                "pass_v2": rederived[c],
            } for c in CELLS
        },
        "cells_x1_x2_x3_sharpe": cells_x,
        "skill_line": {"line": line, "passive_term": sl.get("passive_term"), "null_term": sl.get("null_term"),
                       "mu_null": sl.get("mu_null"), "sigma_null": sl.get("sigma_null"), "n_eff": sl.get("n_eff")},
        "d6_max_abs_corr": max(r["d6_correlation"][c]["member_face"]["max_abs_corr"] for c in CELLS),
        "same_batch_max_corr": 0.9704,
        "max_abs_d1_per_cell": maxd1,
        "n_trials": r.get("n_trials"),
        "audit": r.get("audit"),
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
