"""P2 null-hypothesis calibration v2 -- engine-effect recompute (RW-6, T-127).

Re-executes the FROZEN prereg design (research/NULL_CALIBRATION.md, frozen
2026-09-23 pre-run) on the FULLY-FIXED engine:
  RW-1  exits fill T+1 open (was same-close look-ahead)
  RW-2  evidence_cutoff hard truncation at data assembly
  RW-3  single-source cost spec (FeeSchedule-derived Face A 13.041bp)
  RW-4  panel gate (canonical bare-code core48)

Same seeds, same 48-symbol bare-code universe, SAME window (evidence_cutoff
2026-09-22 = the v1 run's panel end) -> pure engine-effect A/B against
results/p2_calibration.json (v1). v1 file is FROZEN gate-constant canon and
is NOT touched. Ledger +0 (r259 re-execution single-count law; the 122 trials
were already counted by the v1 entry).

Output: results/p2_calibration_v2.json with mu/sigma old-vs-new and the
skill_line_v2 recompute at the CURRENT ledger head (n_eff held equal on both
sides = engine-effect-only line shift attribution).

Selftest subcommand: offline fixture checks (no network, no engine).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd

from config import PATHS
import science_gates as sg

CUTOFF = "2026-09-22"   # v1 run's panel end -- same window, engine A/B only


def load_core_at_cutoff(min_listing_days: int = 60) -> dict:
    """v1 load_core semantics + hard truncation at the frozen cutoff."""
    import p2_null_calibration as v1
    out = {}
    ps = pd.Timestamp(CUTOFF)
    for code, df in v1.load_core(min_listing_days).items():
        out[code] = df[df.index <= ps]
    return out


def run_full() -> int:
    import p2_null_calibration as v1
    from knowledge.rules import FeeSchedule

    t0 = time.time()
    prices = load_core_at_cutoff()
    n_syms = len(prices)
    assert n_syms == 48, f"universe drift: {n_syms} != 48 bare codes"
    idx_all = sorted({d for df in prices.values() for d in df.index})
    idx = pd.DatetimeIndex(idx_all)
    closes = pd.DataFrame(
        {s: df["close"] for s, df in prices.items()}).reindex(idx).sort_index().ffill()
    n_days, n_syms = len(idx), closes.shape[1]
    fee = FeeSchedule()
    cost_rate = (fee.commission_rate + fee.handling_fee +
                 fee.supervision_fee + fee.slippage_a)

    # family C (passive, cheap) -- v1 machinery verbatim
    passive = {}
    bh = v1.passive_buyhold(closes, cost_rate)
    passive["ew48_buyhold"] = {"full": v1.seg_metrics(bh),
                               "oos": v1.seg_metrics(bh, v1.OOS_START),
                               "n_trades": 0, "oos_trades": 0}
    mr = v1.passive_monthly_rebal(closes, cost_rate)
    passive["ew48_monthly_rebal"] = {"full": v1.seg_metrics(mr),
                                     "oos": v1.seg_metrics(mr, v1.OOS_START),
                                     "n_trades": 0, "oos_trades": 0}

    # family A: 100 random-entry x engine exits (same seeds as v1)
    fam_a = []
    for k in range(v1.N_BASELINES):
        p = v1.BASELINE_P[k // 50]
        rng = np.random.default_rng(10_000 + k)
        entry = pd.DataFrame((rng.random((n_days, n_syms)) < p).astype(int),
                             index=idx, columns=list(closes.columns))
        exit_ = pd.DataFrame(False, index=idx, columns=list(closes.columns))
        r = v1.run_one(prices, idx, entry, exit_, {}, f"rand_p{p}_s{k % 50}")
        fam_a.append({**r, "p": p, "seed": k % 50,
                      "note": f"random entry p={p} seed={k % 50}; exits=engine rules"})
        print(f"  A[{k+1}/{v1.N_BASELINES}] full_s={r['full']['sharpe']:>7.3f} "
              f"oos_s={r['oos']['sharpe']:>7.3f} ({time.time()-t0:.0f}s)", flush=True)

    # family B: 20 paired random entry + random exit (same seeds as v1)
    fam_b = []
    for k in range(v1.N_PAIRED):
        p = v1.BASELINE_P[k // 50]
        rng = np.random.default_rng(10_000 + k)
        entry = pd.DataFrame((rng.random((n_days, n_syms)) < p).astype(int),
                             index=idx, columns=list(closes.columns))
        rng_x = np.random.default_rng(20_000 + k)
        exit_ = pd.DataFrame((rng_x.random((n_days, n_syms)) < v1.P_EXIT),
                             index=idx, columns=list(closes.columns))
        r = v1.run_one(prices, idx, entry, exit_, {}, f"randexit_p{p}_s{k % 50}")
        fam_b.append({**r, "p": p, "seed": k % 50,
                      "note": f"random entry p={p} seed={k % 50} + random exit p={v1.P_EXIT}"})
        print(f"  B[{k+1}/{v1.N_PAIRED}] full_s={r['full']['sharpe']:>7.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)

    # null stats exactly as science_gates.null_sharpes computes them
    values = [float(r["full"]["sharpe"]) for r in fam_a + fam_b]
    cov = {"n_values": len(values),
           "schemas_parsed": ["p2_calibration_v2:families[random*].runs[].full.sharpe"],
           "known_unparsed": [], "mu": sum(values) / len(values),
           "sigma": sg._pstdev(values)}
    v1_pool = sg.null_sharpes()   # v1 canon read (frozen file, untouched)
    v1_cov = v1_pool["coverage"]

    # line recompute at the SAME current n_eff on both sides
    line_v2 = sg.skill_line_v2(batch_cells=0, null_pool={"values": values, "coverage": cov})
    line_v1_at_same_neff = sg.skill_line_v2(batch_cells=0, null_pool=v1_pool)

    out = {
        "batch": "P2-null-calibration-v2-engine-effect",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "preregistered_doc": "research/NULL_CALIBRATION.md (frozen 2026-09-23 pre-run; v2 = same design re-executed on the fixed engine, RW-6)",
        "evidence_cutoff": CUTOFF,
        "universe": {"pool": "core48-bare-codes", "n_syms": n_syms,
                     "history": f"{idx[0].date()} .. {idx[-1].date()}"},
        "oos_start": v1.OOS_START,
        "engine_fixes": {"rw1_tplus1_open_exits": True, "rw2_cutoff_truncation": True,
                         "rw3_single_source_cost": True, "rw4_panel_gate": True},
        "families": {
            "A_random_engine_exit": {
                "n": v1.N_BASELINES,
                "full_sharpe_p95": round(float(np.percentile(
                    [r["full"]["sharpe"] for r in fam_a], 95)), 4),
                "runs": fam_a},
            "B_random_entry_random_exit": {"n": v1.N_PAIRED, "runs": fam_b},
            "C_passive": {"runs": passive,
                          "note": "no engine; identical to v1 family C by construction"},
        },
        "null_pool_old_vs_new": {
            "v1": {"n_values": v1_cov["n_values"], "mu": v1_cov["mu"],
                   "sigma": v1_cov["sigma"]},
            "v2": {"n_values": cov["n_values"], "mu": cov["mu"],
                   "sigma": cov["sigma"]},
            "mu_delta": round(cov["mu"] - v1_cov["mu"], 6),
            "sigma_delta": round(cov["sigma"] - v1_cov["sigma"], 6),
        },
        "skill_line_v2_old_vs_new": {
            "n_eff_held_equal": line_v1_at_same_neff["n_eff"],
            "v1_line_at_current_neff": line_v1_at_same_neff["line"],
            "v2_line_at_current_neff": line_v2["line"],
            "line_delta_engine_effect": round(
                line_v2["line"] - line_v1_at_same_neff["line"], 4),
            "passive_term": line_v2.get("passive"),
            "formula": "max(passive+0.10, mu + sigma*sqrt(2*ln N_eff))",
            "ledger_note": "+0 (r259 re-execution single-count; 122 trials "
                           "already counted by v1 entry)",
        },
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "n_backtests": v1.N_BASELINES + v1.N_PAIRED,
                  "workers": 1, "cpu_parallel": "serial (single-process)",
                  "machine": json.loads(open(
                      os.path.join(PATHS.root, "fleet", "machine.json"),
                      encoding="utf-8").read()).get("machine_id", "unknown")},
    }
    path = os.path.join(PATHS.results_dir, "p2_calibration_v2.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\nv1 mu={v1_cov['mu']:.4f} sigma={v1_cov['sigma']:.4f} "
          f"-> v2 mu={cov['mu']:.4f} sigma={cov['sigma']:.4f}")
    print(f"skill_line_v2 @n_eff={line_v1_at_same_neff['n_eff']}: "
          f"{line_v1_at_same_neff['line']} -> {line_v2['line']} "
          f"(engine effect {line_v2['line']-line_v1_at_same_neff['line']:+.4f})")
    print(f"saved: {path} ({out['audit']['elapsed_sec']}s)")
    return 0


def selftest() -> int:
    """Offline checks: v1 module importable, cutoff truncation, seeds stable."""
    import p2_null_calibration as v1
    assert v1.N_BASELINES == 100 and v1.N_PAIRED == 20
    assert v1.BASELINE_P == [0.02, 0.05] and v1.P_EXIT == 0.05
    rng = np.random.default_rng(10_000 + 0)
    m = (rng.random((3, 2)) < 0.5).astype(int)
    rng2 = np.random.default_rng(10_000 + 0)
    assert (m == (rng2.random((3, 2)) < 0.5).astype(int)).all(), "seed drift"
    d = json.loads(open(os.path.join(PATHS.results_dir, "..", "results",
                                     "p2_calibration.json"),
                        encoding="utf-8").read())
    assert d["universe"]["n_syms"] == 48, "v1 canon universe changed"
    assert d["universe"]["history"].endswith(CUTOFF), \
        "v1 history end != frozen cutoff"
    cov = sg.null_sharpes()["coverage"]
    assert cov["n_values"] == 120 and cov["mu"] is not None
    print("selftest: PASS (design constants + seed determinism + v1 canon intact)")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(run_full())
