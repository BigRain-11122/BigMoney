"""XLIB_SYNTH: cross-library small-K synthesis re-eval (core48 ETF domain).

Pre-reg (frozen BEFORE the run): research/shortline/XLIB_SYNTH.md
Claim: MSG-20260924-0512 (commit 5aa8159, F-04 lane lock).
Material: P-1a GTJA191 shelf (pool 89) x P-1b WQ101 shelf (pool 36) -- the
recorded core48 IC batches; zero new data sources, zero engine runs.

Design (prereg s1-s4): reproduce all 125 shelf member h10 stats on the
evidence_cutoff=2026-09-22 truncated panel (hard gate, tol 1e-4); cluster
members on IS-window h10 IC-series correlation (greedy rep-based, 0.5);
primary = top-4 family reps, sign-oriented equal-weight z (min_valid 3);
nullA = 1000 oriented K=4 draws from the shelf, nullB = 1000 from the full
265-member computed population; gates V1/V2/V3 + period gate (P-2/PS2 line).

Reuse (no rewrite): shortline_p1_ic.load_panels / _ic_series_fast /
load_alpha191; shortline_p1b_wq101.load_wq101; ps2_synth z/composite/IC math
(delivered batch stays frozen); composite_ic stats_block / IS_END;
science_gates.cutoff_meta.

Ledger: factor ledger only (engine N untouched); member series reproductions
NOT counted (already counted in P-1a/P-1b; PS2/g25 precedent); added = new
composite evaluations (1 primary + 2 sensitivity + 2000 nulls + h20 column
if primary passes).

Outputs: research/shortline/xlib_synth_results.csv
         results/shortline/xlib_synth.json
"""
import glob
import json
import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from composite_ic import IS_END, ic_series, stats_block
from science_gates import cutoff_meta
from shortline_p1_ic import _ic_series_fast, load_alpha191, load_panels
from shortline_p1b_wq101 import load_wq101
from ps2_synth import composite_z, z_rows

OUT_DIR = os.path.join(ROOT, "results", "shortline")
RES_DIR = os.path.join(ROOT, "research", "shortline")
GTJA_JSON = os.path.join(OUT_DIR, "gtja191_ic.json")
WQ_JSON = os.path.join(OUT_DIR, "wq101_ic.json")

CUTOFF = pd.Timestamp("2026-09-22")
H_GATE = 10
H_REPORT = [20]
N_NULL = 1000
SEED_NULLA = 46000
SEED_NULLB = 47000
V1_FLOOR = 0.02
V2_IR = 0.30
V3_RETAIN = 0.5
MIN_PERIODS = 500
CLUSTER_CORR = 0.5
MIN_OVERLAP = 200
K_PRIMARY, MV_PRIMARY = 4, 3
K_SENS = [(3, 2), (5, 3)]           # (K, min_valid) report-only
REPRO_TOL = 1e-4
EQUIV_TOL = 1e-6
N_SHELF_EXPECT = 125
N_POP_EXPECT = 265

warnings.filterwarnings("ignore")
IS_END_TS = pd.Timestamp(IS_END)


def chain_head_total():
    """Data-driven factor-ledger chain head (R32 lesson: no hardcodes)."""
    best = 0
    for pat in (os.path.join(ROOT, "results", "*.json"),
                os.path.join(OUT_DIR, "*.json")):
        for p in glob.glob(pat):
            try:
                with open(p, encoding="utf-8") as f:
                    d = json.load(f)
                tl = d.get("trials_ledger") or {}
                t = tl.get("total")
                if isinstance(t, (int, float)):
                    best = max(best, int(t))
            except Exception:
                continue
    return best


def seg_stats(s):
    return (stats_block(s), stats_block(s[s.index <= IS_END_TS]),
            stats_block(s[s.index > IS_END_TS]))


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _repro_delta(recorded, blk):
    """Reproduction delta; empty-on-both-sides counts as exact match."""
    r = _num(recorded)
    got = blk.get("ic_mean")
    if r is not None and got is not None:
        return abs(float(got) - r)
    if r is None and got is None:
        return 0.0
    return 9.9


def main():
    t0 = time.time()
    print("[XLIB_SYNTH] load panels (truncate to evidence_cutoff)...")
    panels = load_panels()
    panels = {k: v.loc[v.index <= CUTOFF] for k, v in panels.items()}
    close = panels["close"]
    T, N = close.shape
    cal = close.index
    print(f"  panel: {T} dates x {N} symbols (cutoff {CUTOFF.date()})")
    # P-1a/P-1b recorded-line IC convention: pairwise-complete on the
    # ffill-price panel, no extra tradability mask (core48 has no amount
    # mask in the recorded line; the ps2 maskA convention is stock-domain).
    maskC = close.notna().values
    fwd10 = close.shift(-H_GATE) / close - 1

    # ---- recorded shelf / population
    with open(GTJA_JSON, encoding="utf-8") as f:
        gj = json.load(f)
    with open(WQ_JSON, encoding="utf-8") as f:
        wqj = json.load(f)
    shelf = sorted(set(gj["pool"]) | set(wqj["pool"]))
    rec_rows = {r["factor"]: r for j in (gj, wqj) for r in j["rows"]}
    pop = sorted(r["factor"] for j in (gj, wqj) for r in j["rows"]
                 if r.get("status") == "ok")
    print(f"  shelf={len(shelf)} (expect {N_SHELF_EXPECT}) "
          f"population={len(pop)} (expect {N_POP_EXPECT})")
    assert len(shelf) == N_SHELF_EXPECT, "prereg s3 shelf mismatch"
    assert len(pop) == N_POP_EXPECT, "prereg s4 population mismatch"
    assert set(shelf) <= set(pop), "shelf must be subset of population"

    # ---- equivalence probe (batch fast path vs reference ic_series)
    probe = -close.pct_change(60)
    ref = ic_series(probe, fwd10)
    fast = _ic_series_fast(probe, fwd10)
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) else 9.9
    print(f"  equivalence probe: max|diff|={worst:.2e} "
          f"n_ref={len(ref)} n_fast={len(fast)}")
    if worst > EQUIV_TOL or len(ref) != len(fast):
        print("EQUIVALENCE FAIL - abort (no numbers produced)")
        sys.exit(1)

    # ---- build all member value panels -> z panels + h10 IC series
    print("computing member panels (265 population)...")
    mod191 = load_alpha191()
    wq = load_wq101()
    data = {k: panels[k].values for k in
            ("open", "high", "low", "close", "volume", "vwap")}
    data["returns"] = close.pct_change().values
    data["market_cap"] = np.full(close.shape, np.nan)
    engine = wq.Alpha101(data, classifications={})

    def compute_member(name):
        if name.startswith("alpha191_"):
            return getattr(mod191, name)(dict(panels))
        n = int(name.replace("alpha", ""))
        out = getattr(engine, f"alpha{n:03d}")()
        return pd.DataFrame(out, index=close.index, columns=close.columns)

    z_panels = {}
    ic_is = {}
    ic_series_is = {}
    is_sign = {}
    oos_repro = {}
    is_repro = {}
    sanitized = []
    t1 = time.time()
    for i, name in enumerate(pop, 1):
        vals = compute_member(name)
        arr = vals.values
        if arr.dtype == object:  # vendor hygiene (P-2 precedent): to_numeric
            arr = vals.apply(pd.to_numeric, errors="coerce").values
            arr = np.asarray(arr, dtype=np.float64)
            sanitized.append(name)
        z_panels[name] = z_rows(arr, maskC).astype(np.float32)
        s = _ic_series_fast(pd.DataFrame(arr, index=vals.index,
                                         columns=vals.columns), fwd10)
        s_is = s[s.index <= IS_END_TS]
        ic_series_is[name] = s_is
        blk_is = stats_block(s_is)
        blk_oos = stats_block(s[s.index > IS_END_TS])
        ic_is[name] = blk_is.get("ic_mean", np.nan)
        is_sign[name] = 1.0 if blk_is.get("ic_mean", 0) >= 0 else -1.0
        if name in rec_rows:
            is_repro[name] = _repro_delta(rec_rows[name].get("h10_is_ic"),
                                          blk_is)
            oos_repro[name] = _repro_delta(rec_rows[name].get("h10_oos_ic"),
                                          blk_oos)
        if i % 50 == 0:
            print(f"  ... {i}/{len(pop)} ({time.time()-t1:.0f}s)", flush=True)
    print(f"  member panels done ({time.time()-t1:.0f}s)")

    # ---- hard reproduction gate (all shelf members, IS + OOS)
    repro_bad = [n for n in shelf
                 if is_repro.get(n, 9) > REPRO_TOL
                 or oos_repro.get(n, 9) > REPRO_TOL]
    repro_max_is = max(is_repro[n] for n in shelf)
    repro_max_oos = max(oos_repro[n] for n in shelf)
    print(f"  reproduction gate: {len(shelf)-len(repro_bad)}/{len(shelf)} "
          f"within {REPRO_TOL} (max d_is={repro_max_is:.2e} "
          f"d_oos={repro_max_oos:.2e})")
    if repro_bad:
        print(f"REPRODUCTION FAIL - batch VOID: {repro_bad[:8]}")
        sys.exit(2)

    # ---- clustering (prereg s1): greedy rep-based on IS IC-series corr
    def sort_key(n):
        v = ic_is[n]
        fin = bool(np.isfinite(v))
        return (0 if fin else 1, -abs(v) if fin else 0.0, n)

    order = sorted(shelf, key=sort_key)
    reps = []
    clusters = {}
    for name in order:
        placed = None
        for r in reps:
            c = ic_series_is[name].corr(ic_series_is[r], min_periods=MIN_OVERLAP)
            if np.isfinite(c) and c >= CLUSTER_CORR:
                placed = r
                break
        if placed is None:
            reps.append(name)
            clusters[name] = [name]
        else:
            clusters[placed].append(name)
    top_reps = reps[:max(K_PRIMARY, max(k for k, _ in K_SENS))]
    print(f"  clusters: {len(reps)} families; top reps: "
          f"{[(r, round(ic_is[r], 4), len(clusters[r])) for r in top_reps]}")

    # ---- primary composite (top-4 reps, sign-oriented, min_valid 3)
    def build_comp(names, min_valid):
        zs = [z_panels[n] * is_sign[n] for n in names]
        return composite_z(zs, min_valid)

    def comp_ic(comp_arr, fwd_df):
        df = pd.DataFrame(comp_arr, index=close.index, columns=close.columns)
        return _ic_series_fast(df, fwd_df)

    comp = build_comp(top_reps[:K_PRIMARY], MV_PRIMARY)
    s_comp = comp_ic(comp, fwd10)
    b_full, b_is, b_oos = seg_stats(s_comp)
    print(f"  primary: is_ic={b_is.get('ic_mean')} is_ir={b_is.get('ic_ir')} "
          f"oos_ic={b_oos.get('ic_mean')} ({time.time()-t1:.0f}s)")

    # ---- nullA (shelf band) / nullB (population band), 1000 each
    def null_band(pop_names, seed0):
        abs_is = []
        for k in range(N_NULL):
            rng = np.random.default_rng(seed0 + k)
            idx = rng.choice(len(pop_names), K_PRIMARY, replace=False)
            names = [pop_names[j] for j in idx]
            zs = [z_panels[n] * is_sign[n] for n in names]
            s = comp_ic(composite_z(zs, MV_PRIMARY), fwd10)
            blk = stats_block(s[s.index <= IS_END_TS])
            if "ic_mean" in blk:
                abs_is.append(abs(blk["ic_mean"]))
        return abs_is

    print("nullA (1000 shelf K=4 draws)...", flush=True)
    t1 = time.time()
    na = null_band(shelf, SEED_NULLA)
    nulla_p95 = float(np.quantile(na, 0.95)) if na else 9.9
    print(f"  nullA p95={nulla_p95:.4f} ({time.time()-t1:.0f}s)")
    print("nullB (1000 population K=4 draws)...", flush=True)
    t1 = time.time()
    nb = null_band(pop, SEED_NULLB)
    nullb_p95 = float(np.quantile(nb, 0.95)) if nb else 9.9
    print(f"  nullB p95={nullb_p95:.4f} ({time.time()-t1:.0f}s)")

    # ---- gates (prereg s4)
    v1_thr = max(V1_FLOOR, nulla_p95, nullb_p95)
    v1 = abs(b_is["ic_mean"]) > v1_thr
    v2 = abs(b_is["ic_ir"]) >= V2_IR
    v3 = ((b_oos["ic_mean"] > 0) == (b_is["ic_mean"] > 0)
          and abs(b_oos["ic_mean"]) >= V3_RETAIN * abs(b_is["ic_mean"]))
    pg = b_is.get("n_periods", 0) >= MIN_PERIODS
    passed = bool(v1 and v2 and v3 and pg)
    print(f"gates: thr={v1_thr:.4f} V1={v1} V2={v2} V3={v3} "
          f"periods={pg} PASS={passed}")

    # ---- sensitivity columns (report only)
    sens = []
    for k, mv in K_SENS:
        c2 = build_comp(top_reps[:k], mv)
        s2 = comp_ic(c2, fwd10)
        _, bis2, bos2 = seg_stats(s2)
        sens.append({"role": f"sensitivity_k{k}", "k": k, "min_valid": mv,
                     "members": top_reps[:k],
                     "is_ic": bis2.get("ic_mean", ""),
                     "is_ir": bis2.get("ic_ir", ""),
                     "oos_ic": bos2.get("ic_mean", "")})

    # ---- h20 report column for primary if pass (snooping-discount label)
    h20 = {}
    if passed:
        for h in H_REPORT:
            fw = close.shift(-h) / close - 1
            sh = comp_ic(comp, fw)
            _, his, hos = seg_stats(sh)
            h20[f"h{h}"] = {"is_ic": his.get("ic_mean", ""),
                            "oos_ic": hos.get("ic_mean", ""),
                            "snooping_discount": True}

    # ---- ledger + outputs
    prev_head = chain_head_total()
    added = 1 + len(K_SENS) + len(na) + len(nb) + (1 if passed else 0)
    total = prev_head + added
    rep_corr = {}
    for a in top_reps:
        rep_corr[a] = {b: round(float(ic_series_is[a].corr(
            ic_series_is[b], min_periods=MIN_OVERLAP)), 4)
            for b in top_reps if b != a}

    rows = [{"role": "primary", "k": K_PRIMARY, "min_valid": MV_PRIMARY,
             "members": top_reps[:K_PRIMARY],
             "orient": {n: is_sign[n] for n in top_reps[:K_PRIMARY]},
             "is_ic": b_is.get("ic_mean", ""), "is_ir": b_is.get("ic_ir", ""),
             "is_n": b_is.get("n_periods", 0),
             "oos_ic": b_oos.get("ic_mean", ""),
             "full_ic": b_full.get("ic_mean", ""),
             "v1_thr": round(v1_thr, 4), "v1": bool(v1), "v2": bool(v2),
             "v3": bool(v3), "period_gate": bool(pg), "pass": passed}]
    rows += sens
    pd.DataFrame(rows).to_csv(
        os.path.join(RES_DIR, "xlib_synth_results.csv"),
        index=False, encoding="utf-8")

    out = {
        "meta": {
            "batch": "XLIB_SYNTH cross-library small-K synthesis re-eval",
            "pre_reg": "research/shortline/XLIB_SYNTH.md",
            "claim": "MSG-20260924-0512",
            "multiplicity": "ETF-domain external-lib synthesis attempt #2 "
                            "(P-2 K=20 was #1); FAIL -> line closes per prereg",
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "is_end": IS_END, "gate_horizon": H_GATE,
            "engine_runs": 0,
            "universe": f"core48 bare-code, {N} symbols, {T} dates",
        },
        "equivalence": {"max_abs_diff": worst, "tol": EQUIV_TOL,
                        "pass": worst <= EQUIV_TOL},
        "reproduction_gate": {"tol": REPRO_TOL,
                              "n_shelf": len(shelf),
                              "n_pass": len(shelf) - len(repro_bad),
                              "max_delta_is": repro_max_is,
                              "max_delta_oos": repro_max_oos,
                              "pass": not repro_bad},
        "sanitized_panels": sanitized,
        "clustering": {"corr_threshold": CLUSTER_CORR,
                       "min_overlap": MIN_OVERLAP,
                       "n_families": len(reps),
                       "families": {r: clusters[r] for r in reps},
                       "top_reps": top_reps,
                       "rep_is_ic": {r: ic_is[r] for r in top_reps},
                       "rep_pairwise_corr": rep_corr},
        "thresholds": {"nullA_p95": round(nulla_p95, 4),
                       "nullB_p95": round(nullb_p95, 4),
                       "v1_thr": round(v1_thr, 4), "v1_floor": V1_FLOOR,
                       "v2_ir": V2_IR, "v3_retain": V3_RETAIN},
        "primary": rows[0],
        "sensitivity": sens,
        "h20_report": h20,
        "trials_ledger": {
            "prev": prev_head, "added": added, "total": total,
            "note": "factor-ledger accounting (P-1d precedent): added = new "
                    "composite evaluations (1 primary + 2 sensitivity + "
                    f"{len(na)} nullA + {len(nb)} nullB"
                    + (" + 1 h20 report" if passed else "")
                    + "); member series reproductions NOT counted (P-1a/P-1b "
                      "already counted them; PS2/g25 reproduction precedent); "
                      "engine N untouched",
        },
        "audit": {"elapsed_sec": round(time.time() - t0, 1),
                  "ic_computations": len(pop) + added,
                  "workers": 1,
                  "cpu_cap_policy": "O-20260923-1738 single-proc vectorized"},
    }
    out.update(cutoff_meta(CUTOFF.date()))
    with open(os.path.join(OUT_DIR, "xlib_synth.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n=== XLIB_SYNTH: primary PASS={passed} "
          f"(is_ic={b_is.get('ic_mean')} ir={b_is.get('ic_ir')} "
          f"thr={v1_thr:.4f}) | ledger {prev_head}->{total} "
          f"| elapsed {time.time()-t0:.0f}s ===")


if __name__ == "__main__":
    main()
