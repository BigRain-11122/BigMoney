"""P-1b WQ101 no-cap subset factor batch IC + GTJA191 021/116/147 retest.

Dispatch: O-20260923-1738 (CEO compute mobilization) / MSG-1740 -> bm-a.
Pre-registration (written BEFORE the run): research/shortline/P1_WQ101_IC.md.

Methodology reuse (no rewrite): shortline_p1_ic harness - fast IC path with
equivalence gate, white-noise null calibration (K=50, same seeds as P-1a),
A1-A4 gates + strong tier, run_batch bookkeeping; composite_ic stats/IS_END.

Engineering: vendor-direct execution of the MIT Alpha101 class (dense
date x symbol numpy calcs). polars is stubbed: the vendored module only uses
it in the long-form I/O boundary factor_alpha101(), which this batch never
calls. Exclusion set = _NEUTRALIZED_ALPHAS (18, need sector/industry) +
alpha056 (cap) per pre-reg s2 -> computable 82/101.

021/116/147 retest: rolling_slope = REGBETA(x, SEQUENCE, w) closed-form,
gated against np.polyfit per window, injected into the vendored gtja191
module namespace (both machines skipped these in P-1a - untested, not
invalid).

Outputs: research/shortline/wq101_ic_results.csv,
research/shortline/gtja191_retest_021_116_147.csv,
results/shortline/wq101_ic.json
"""
import os, sys, json, time, types, importlib.util
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from composite_ic import ic_series, stats_block, IS_END
from shortline_p1_ic import (load_panels, _ic_series_fast, null_thresholds,
                             run_batch, load_alpha191, _shim_selfcheck,
                             HORIZONS, N_NULLS, EQUIV_TOL)

EXT = os.path.join(ROOT, "research", "shortline", "external",
                   "worldquant101_alpha101.py")
OUT_DIR = os.path.join(ROOT, "results", "shortline")
RES_DIR = os.path.join(ROOT, "research", "shortline")
CAP_EXCLUDED = {56}  # alpha056: returns * market_cap, no ETF cap convention
SLOPE_TOL = 1e-10


def load_wq101():
    if "polars" not in sys.modules:
        sys.modules["polars"] = types.ModuleType("polars")  # I/O boundary only
    spec = importlib.util.spec_from_file_location("wq101_external", EXT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["wq101_external"] = mod
    spec.loader.exec_module(mod)
    return mod


def _rolling_slope_1d(arr, period):
    """REGBETA(arr, SEQUENCE, w): LS slope vs time index over trailing window.

    All-finite-window policy (conservative warmup, pre-reg s2). Vendor's own
    reference comment: rolling(...).apply(polyfit(seq, x, 1)[0]).
    """
    arr = np.asarray(arr, dtype=float)
    w = int(period)
    out = np.full(arr.shape, np.nan)
    if arr.size < w or w < 2:
        return out
    sw = sliding_window_view(arr, w)
    ic = np.arange(w, dtype=float)
    ic = ic - ic.mean()
    denom = float((ic * ic).sum())
    with np.errstate(invalid="ignore"):
        slopes = sw @ ic / denom
    out[w - 1:] = slopes
    out[w - 1:][np.isnan(sw).any(axis=1)] = np.nan
    return out


def _slope_selfcheck():
    rng = np.random.default_rng(11)
    x = rng.standard_normal(300)
    w = 12
    mine = _rolling_slope_1d(x, w)
    ref = np.full(x.shape, np.nan)
    for t in range(w - 1, len(x)):
        ref[t] = np.polyfit(np.arange(w, dtype=float),
                            x[t - w + 1:t + 1], 1)[0]
    ok1 = np.allclose(mine[w - 1:], ref[w - 1:], atol=SLOPE_TOL)
    y = x.copy()
    y[40:45] = np.nan
    my2 = _rolling_slope_1d(y, w)
    win_has_nan = np.isnan(sliding_window_view(y, w)).any(axis=1)
    bad = np.nonzero(win_has_nan)[0]
    ok2 = bool(np.all(np.isnan(my2[w - 1:][bad]))
               and np.isnan(my2[:w - 1]).all())
    print(f"  slope-vs-polyfit={ok1} nan-window-policy={ok2}")
    return bool(ok1 and ok2)


def strict_h10(rec, thr_h10):
    """Merged-criteria h10 READINGS (reference columns, not gates)."""
    ic_is = rec.get("h10_is_ic")
    ir_is = rec.get("h10_is_ir")
    ic_oos = rec.get("h10_oos_ic")
    if not all(isinstance(v, (int, float)) for v in (ic_is, ir_is, ic_oos)):
        return {}
    v1 = abs(ic_is) > max(0.02, thr_h10["p95_abs_ic"])
    v2 = abs(ir_is) >= 0.30
    v3 = ((ic_oos > 0) == (ic_is > 0)) and abs(ic_oos) >= 0.5 * abs(ic_is)
    return {"h10_v1": bool(v1), "h10_v2": bool(v2), "h10_v3": bool(v3),
            "h10_strict_all": bool(v1 and v2 and v3)}


def main():
    t0 = time.time()
    print("[P-1b] loading panels (core48 bare-code, full history)...")
    panels = load_panels()
    close = panels["close"]
    print(f"  panels: {close.shape[0]} dates x {close.shape[1]} symbols")
    fwd = {h: close.shift(-h) / close - 1 for h in HORIZONS}

    print("gate 1: fast-IC equivalence vs reference ic_series...")
    probe = -close.pct_change(60)
    ref = ic_series(probe, fwd[20])
    fast = _ic_series_fast(probe, fwd[20])
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) else 9.9
    print(f"  n_ref={len(ref)} n_fast={len(fast)} max|diff|={worst:.2e}")
    if worst > EQUIV_TOL or len(ref) != len(fast):
        print("EQUIVALENCE FAIL - aborting (no numbers produced)")
        sys.exit(1)

    print("gate 2: rolling_slope closed-form vs np.polyfit...")
    if not _slope_selfcheck():
        print("SLOPE SELF-CHECK FAIL - aborting")
        sys.exit(1)

    print("gate 3: gtja shim self-check (needed for 021/116/147 retest)...")
    if not _shim_selfcheck():
        print("SHIM SELF-CHECK FAIL - aborting")
        sys.exit(1)

    print(f"building null baseline (K={N_NULLS}, same seeds as P-1a)...")
    thr = null_thresholds(close, fwd)
    r9_path = os.path.join(OUT_DIR, "gtja191_ic.json")
    null_repro = None
    if os.path.exists(r9_path):
        r9 = json.load(open(r9_path, encoding="utf-8")).get("thresholds", {})
        null_repro = all(
            r9.get(k, {}).get(m) == thr[k][m]
            for k in thr for m in ("p95_abs_ic", "p95_abs_ir"))
        print(f"  null lines reproduce P-1a bit-exact: {null_repro}")
    for k, v in thr.items():
        print(f"  {k}: p95_abs_ic={v['p95_abs_ic']} p95_abs_ir={v['p95_abs_ir']}")

    print("loading WQ101 vendor module (polars stubbed, calc layer = numpy)...")
    wq = load_wq101()
    neutralized = set(wq._NEUTRALIZED_ALPHAS)
    excluded = sorted(neutralized | CAP_EXCLUDED)
    computable = [n for n in range(1, 102) if n not in excluded]
    print(f"  excluded {len(excluded)}: neutralized={sorted(neutralized)} "
          f"cap={sorted(CAP_EXCLUDED)} -> computable {len(computable)}/101")
    assert len(excluded) == 19 and len(computable) == 82, "pre-reg s2 mismatch"

    data = {k: panels[k].values for k in
            ("open", "high", "low", "close", "volume", "vwap")}
    data["returns"] = close.pct_change().values
    data["market_cap"] = np.full(close.shape, np.nan)
    engine = wq.Alpha101(data, classifications={})
    def _wrap(n):
        def fn(d):
            out = getattr(engine, f"alpha{n:03d}")()
            return pd.DataFrame(out, index=close.index, columns=close.columns)
        return fn
    funcs = {f"alpha{n:03d}": _wrap(n) for n in computable}

    print(f"running WQ101 batch ({len(funcs)} factors, h={HORIZONS})...")
    rows = run_batch(funcs, panels, fwd, thr)
    for rec in rows:
        rec.update(strict_h10(rec, thr["h10"]))

    print("retest: gtja191 021/116/147 with injected rolling_slope...")
    mod191 = load_alpha191()
    mod191.rolling_slope = _rolling_slope_1d
    retest_funcs = {k: getattr(mod191, k) for k in
                    ("alpha191_021", "alpha191_116", "alpha191_147")}
    rrows = run_batch(retest_funcs, panels, fwd, thr)
    for rec in rrows:
        rec.update(strict_h10(rec, thr["h10"]))

    ok = [r for r in rows if r["status"] == "ok"]
    pool = [r["factor"] for r in ok if r.get("in_pool")]
    strong = [r["factor"] for r in ok if r.get("strong_tier")]
    skip_counts = {}
    for r in rows:
        if r["status"] != "ok":
            skip_counts[r["status"]] = skip_counts.get(r["status"], 0) + 1
    per_h = {f"h{h}": sum(1 for r in ok if r.get(f"h{h}_pass")) for h in HORIZONS}
    strict_pass = [r["factor"] for r in ok if r.get("h10_strict_all")]

    print("\n=== P-1b WQ101 batch summary ===")
    print(f"  factors: {len(rows)} total, {len(ok)} computed, skips={skip_counts}")
    print(f"  pool (A1-A4 any h): {len(pool)}  strong tier: {len(strong)}")
    print(f"  per-h pass: {per_h}  h10 strict V1&V2&V3: {len(strict_pass)}")
    print(f"  retest 021/116/147: "
          f"{[(r['factor'], r['status'], r.get('in_pool'), r.get('h10_v2')) for r in rrows]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    pd.DataFrame(rows).to_csv(
        os.path.join(RES_DIR, "wq101_ic_results.csv"), index=False)
    pd.DataFrame(rrows).to_csv(
        os.path.join(RES_DIR, "gtja191_retest_021_116_147.csv"), index=False)

    out = {
        "meta": {
            "batch": "P-1b WQ101 no-cap subset IC + gtja191 021/116/147 retest",
            "pre_reg": "research/shortline/P1_WQ101_IC.md",
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "is_end": IS_END,
            "universe": f"core48 bare-code, {close.shape[1]} symbols, "
                        f"{close.shape[0]} dates",
            "excluded": {"neutralized": sorted(neutralized),
                         "cap": sorted(CAP_EXCLUDED)},
            "n_computable": len(computable),
            "n_nulls": N_NULLS,
            "strategy_ledger_note": "factor screening batch; strategy engine "
                                     "ledger N=1435 untouched",
            "elapsed_s": round(time.time() - t0, 1),
        },
        "gates": {"fast_ic_max_abs_diff": worst, "n_ref": len(ref),
                  "n_fast": len(fast), "slope_polyfit_ok": True},
        "null_reproduce_p1a_bitexact": null_repro,
        "thresholds": thr,
        "counts": {"computed": len(ok), "skips": skip_counts,
                   "pool": len(pool), "strong": len(strong),
                   "per_h_pass": per_h, "h10_strict_all": len(strict_pass)},
        "pool": pool,
        "strong_tier": strong,
        "h10_strict_all": strict_pass,
        "rows": rows,
        "gtja_retest": {"rows": rrows},
    }
    with open(os.path.join(OUT_DIR, "wq101_ic.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nsaved: research/shortline/wq101_ic_results.csv")
    print(f"saved: research/shortline/gtja191_retest_021_116_147.csv")
    print(f"saved: results/shortline/wq101_ic.json")
    print(f"elapsed: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
