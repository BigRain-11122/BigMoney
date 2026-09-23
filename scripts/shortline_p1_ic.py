"""P-1a GTJA191 factor batch IC screening (playbook §6 first batch, O-1545).

External lib import shims (research env stays ta-lib/qlib-free by design,
playbook §2.2 "缺则降级"): talib stub, factors.ops.rolling pure-numpy impl,
lib.* registered under original names. Missing qlib -> lib's own try/except.

Methodology reuse (no rewrite): composite_ic.ic_series / stats_block / IS_END.
A vectorized fast IC path (_ic_series_fast) is gated by an equivalence
self-check against the reference ic_series before the batch (max |diff| <= 1e-6).

Pre-registered gates live in research/shortline/P1_GTJA191_IC.md (§4),
written BEFORE the run; no post-hoc threshold tuning.

Outputs: research/shortline/gtja191_ic_results.csv + results/shortline/gtja191_ic.json
"""
import os, sys, json, time, types, importlib.util
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # scripts/ for composite_ic reuse

from composite_ic import ic_series, stats_block, IS_END  # established methodology

EXT_DIR = os.path.join(ROOT, "research", "shortline", "external")
OUT_DIR = os.path.join(ROOT, "results", "shortline")
RES_DIR = os.path.join(ROOT, "research", "shortline")

HORIZONS = [5, 10, 20]
N_NULLS = 50
SEED0 = 20260923
NULL_Q = 0.95
MIN_PERIODS_GATE = 500
EQUIV_TOL = 1e-6


# ---------------------------------------------------------------- import shims
def _missing_op(*args, **kwargs):
    raise NotImplementedError("external op unavailable (ta-lib/qlib-free research env)")


def _sliding(arr, n):
    from numpy.lib.stride_tricks import sliding_window_view
    return sliding_window_view(arr, n, axis=0)


def _wma(arr, weight):
    """Rolling weighted mean along axis 0; NaN propagates (replaces cython _wma).

    First-batch bug (kept in the ledger): einsum labels reused 'w' for both
    the symbol axis and the weight axis -> every WMA/DECAYLINEAR factor died
    with a broadcast error. Fixed via tensordot(contract window axis).
    """
    arr = np.asarray(arr, dtype=float)
    n = len(weight)
    out = np.full_like(arr, np.nan)
    if arr.shape[0] >= n:
        out[n - 1:, :] = np.tensordot(_sliding(arr, n),
                                       np.asarray(weight, dtype=float),
                                       axes=([2], [0]))
    return out


def _max_distance(arr, n):
    """Days since trailing-window max (0 = today); caller pre-fills NaN as -inf."""
    arr = np.asarray(arr, dtype=float)
    out = np.full_like(arr, np.nan)
    if arr.shape[0] >= n:
        out[n - 1:, :] = (n - 1) - _sliding(arr, n).argmax(axis=2)
    return out


def _min_distance(arr, n):
    arr = np.asarray(arr, dtype=float)
    out = np.full_like(arr, np.nan)
    if arr.shape[0] >= n:
        out[n - 1:, :] = (n - 1) - _sliding(arr, n).argmin(axis=2)
    return out


def _alpha191_143(close_vals, delay_vals):
    """Recursive self-return composite (only referenced by unfinished #143)."""
    c = np.asarray(close_vals, dtype=float)
    d = np.asarray(delay_vals, dtype=float)
    ret = c / d - 1.0
    out = np.ones_like(c)
    for t in range(1, c.shape[0]):
        r = ret[t]
        grow = np.where(np.isfinite(r) & (r > 0), r, 0.0)
        prev = out[t - 1]
        out[t] = np.where(np.isfinite(prev), prev * (1.0 + grow), np.nan)
    out[~np.isfinite(ret)] = np.nan
    return out


def _install_shims():
    if "talib" in sys.modules:
        return
    talib = types.ModuleType("talib")
    talib.__getattr__ = lambda name: _missing_op  # PEP 562
    sys.modules["talib"] = talib

    rolling = types.ModuleType("factors.ops.rolling")
    rolling._wma = _wma
    rolling._max_distance = _max_distance
    rolling._min_distance = _min_distance
    rolling._alpha191_143 = _alpha191_143
    for pkg in ["factors", "factors.ops"]:
        m = types.ModuleType(pkg)
        m.__getattr__ = lambda name: _missing_op
        sys.modules[pkg] = m
    sys.modules["factors.ops.rolling"] = rolling


def _load_external(name, filename):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(EXT_DIR, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_alpha191():
    _install_shims()
    for pkg in ["lib", "lib.ops", "lib.utils"]:
        if pkg not in sys.modules:
            m = types.ModuleType(pkg)
            m.__getattr__ = lambda name: _missing_op
            sys.modules[pkg] = m
    _load_external("lib.base", "gtja191_lib_base.py")
    _load_external("lib.utils.method_attrs", "gtja191_lib_method_attrs.py")
    _load_external("lib.ops.factor_ops", "gtja191_lib_factor_ops.py")
    return _load_external("alpha191_external", "gtja191_alpha191.py")


# ---------------------------------------------------------------- data panels
def load_panels():
    from config import PATHS
    daily = PATHS.daily_dir
    files = sorted(f for f in os.listdir(daily)
                   if f.endswith(".csv") and f[:-4].isdigit())
    cols = ["open", "high", "low", "close", "volume", "amount"]
    series = {c: {} for c in cols}
    for f in files:
        df = pd.read_csv(os.path.join(daily, f),
                         parse_dates=["date"]).set_index("date").sort_index()
        for c in cols:
            if c in df.columns:
                series[c][f[:-4]] = df[c]
    panels = {}
    for c in cols:
        p = pd.DataFrame(series[c]).sort_index()
        if c in ("open", "high", "low", "close"):
            p = p.ffill()  # price convention per composite_ic
        panels[c] = p
    panels["vwap"] = panels["amount"] / panels["volume"]
    return panels


# ---------------------------------------------------------------- fast IC path
def _ic_series_fast(factor: pd.DataFrame, fwd_ret: pd.DataFrame) -> pd.Series:
    """Vectorized per-date cross-sectional spearman IC.

    Mathematically identical to composite_ic.ic_series (spearman = pearson of
    average ranks, pairwise-complete rows, >=5 names, zero-variance -> NaN).
    Gated by an equivalence self-check before the batch.
    """
    # rank AFTER pairing (reference ranks within the per-date intersection,
    # so late-listed symbols must not dilute ranks) - equivalence-gated
    mask = factor.notna() & fwd_ret.notna()
    n = mask.sum(axis=1)
    F = factor.where(mask).rank(axis=1)
    R = fwd_ret.where(mask).rank(axis=1)
    fm = F.mean(axis=1)
    rm = R.mean(axis=1)
    df_ = F.sub(fm, axis=0)
    dr_ = R.sub(rm, axis=0)
    cov = (df_ * dr_).sum(axis=1)
    sf = np.sqrt((df_ ** 2).sum(axis=1))
    sr = np.sqrt((dr_ ** 2).sum(axis=1))
    ic = cov / (sf * sr)
    ic = ic.where(sf > 0)
    ic = ic.where(sr > 0)
    ic = ic.where(n >= 5)
    return ic.dropna()


def null_thresholds(close, fwd):
    """White-noise factor nulls (pre-registered K=50, seeds SEED0+i)."""
    abs_means = {h: [] for h in HORIZONS}
    abs_irs = {h: [] for h in HORIZONS}
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED0 + k)
        vals = pd.DataFrame(rng.standard_normal(close.shape),
                            index=close.index, columns=close.columns)
        vals = vals.where(close.notna())  # mimic tradability mask
        for h in HORIZONS:
            s = _ic_series_fast(vals, fwd[h])
            blk = stats_block(s[s.index <= IS_END])
            if "ic_mean" in blk:
                abs_means[h].append(abs(blk["ic_mean"]))
                abs_irs[h].append(abs(blk["ic_ir"]))
    return {f"h{h}": {
        "p95_abs_ic": round(float(np.quantile(abs_means[h], NULL_Q)), 4),
        "p95_abs_ir": round(float(np.quantile(abs_irs[h], NULL_Q)), 4),
        "n_nulls": len(abs_means[h]),
    } for h in HORIZONS}


def gate_h(blk_is, blk_oos, thr_h):
    """Pre-registered gates A1-A4 (P1_GTJA191_IC.md §4)."""
    if "ic_mean" not in blk_is or "ic_mean" not in blk_oos:
        return {"pass": False, "strong": False}
    a1 = abs(blk_is["ic_mean"]) > thr_h["p95_abs_ic"]
    a2 = abs(blk_is["ic_ir"]) > thr_h["p95_abs_ir"]
    a3 = blk_is["n_periods"] >= MIN_PERIODS_GATE
    a4 = ((blk_oos["ic_mean"] > 0) == (blk_is["ic_mean"] > 0)
          and abs(blk_oos["ic_mean"]) > 0)
    passed = bool(a1 and a2 and a3 and a4)
    strong = bool(passed and abs(blk_oos["ic_mean"])
                  >= 0.5 * abs(blk_is["ic_mean"]))
    return {"a1": bool(a1), "a2": bool(a2), "a3": bool(a3), "a4": bool(a4),
            "pass": passed, "strong": strong}


def _classify(exc):
    if isinstance(exc, NotImplementedError):
        return "skip_talib"
    if isinstance(exc, NameError):
        return "skip_qlib_or_missing_name"
    if isinstance(exc, KeyError):
        return "skip_missing_field"
    return "error"


def run_batch(funcs, panels, fwd, thr):
    rows = []
    for i, (nm, fn) in enumerate(sorted(funcs.items()), 1):
        t0 = time.time()
        rec = {"factor": nm, "status": "ok", "skip_reason": "",
               "compute_s": 0.0}
        try:
            out = fn(dict(panels))
        except Exception as e:
            rec["status"] = _classify(e)
            rec["skip_reason"] = f"{type(e).__name__}: {str(e)[:100]}"
            out = None
        if out is not None and (not isinstance(out, pd.DataFrame) or out.empty):
            rec["status"] = "skip_not_implemented"
            rec["skip_reason"] = "empty or non-DataFrame output"
            out = None
        if out is None and rec["status"] == "ok":
            # fn returned None without raising (unfinished stub, e.g. #143)
            rec["status"] = "skip_not_implemented"
            rec["skip_reason"] = "returned None (unfinished stub)"
        if out is not None:
            rec["compute_s"] = round(time.time() - t0, 2)
            any_pass, any_strong = False, False
            for h in HORIZONS:
                s = _ic_series_fast(out, fwd[h])
                blk_full = stats_block(s)
                blk_is = stats_block(s[s.index <= IS_END])
                blk_oos = stats_block(s[s.index > IS_END])
                g = gate_h(blk_is, blk_oos, thr[f"h{h}"])
                p = f"h{h}_"
                for seg, blk in [("full", blk_full), ("is", blk_is),
                                ("oos", blk_oos)]:
                    rec[p + seg + "_ic"] = blk.get("ic_mean", "")
                    rec[p + seg + "_ir"] = blk.get("ic_ir", "")
                    rec[p + seg + "_n"] = blk.get("n_periods", 0)
                rec[p + "pass"] = g["pass"]
                rec[p + "strong"] = g["strong"]
                any_pass |= g["pass"]
                any_strong |= g["strong"]
            rec["in_pool"] = any_pass
            rec["strong_tier"] = any_strong
        rows.append(rec)
        if i % 25 == 0:
            print(f"  ... {i}/{len(funcs)} factors "
                  f"({time.time() - t0:.1f}s last, pool="
                  f"{sum(r.get('in_pool', False) for r in rows)})")
    return rows


def _shim_selfcheck():
    """Gate the numpy shim ops against pandas rolling references before batch."""
    rng = np.random.default_rng(7)
    x = rng.standard_normal((60, 3))
    n = 5
    w = (np.arange(n) + 1) / (np.arange(n) + 1).sum()
    got = _wma(x, w)
    s = pd.DataFrame(x)
    ref = s.rolling(n).apply(lambda v: float((v * w).sum()), raw=True)
    ok1 = np.allclose(got[n - 1:], ref.values[n - 1:])
    rmax = s.rolling(n).apply(lambda v: float(n - 1 - np.argmax(v)), raw=True)
    rmin = s.rolling(n).apply(lambda v: float(n - 1 - np.argmin(v)), raw=True)
    ok2 = np.allclose(_max_distance(x, n)[n - 1:], rmax.values[n - 1:])
    ok3 = np.allclose(_min_distance(x, n)[n - 1:], rmin.values[n - 1:])
    print(f"  wma={ok1} maxdist={ok2} mindist={ok3}")
    return ok1 and ok2 and ok3


def main():
    t0 = time.time()
    print("loading external GTJA191 with import shims...")
    mod = load_alpha191()
    funcs = {nm: fn for nm, fn in vars(mod).items()
             if nm.startswith("alpha191_") and callable(fn)}
    print(f"  {len(funcs)} factor functions")

    panels = load_panels()
    close = panels["close"]
    print(f"  panels: {close.shape[0]} dates x {close.shape[1]} symbols")
    fwd = {h: close.shift(-h) / close - 1 for h in HORIZONS}

    print("equivalence self-check: fast IC vs reference ic_series...")
    probe = -close.pct_change(60)
    ref = ic_series(probe, fwd[20])
    fast = _ic_series_fast(probe, fwd[20])
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) if len(common) else 9.9
    n_ref, n_fast = len(ref), len(fast)
    print(f"  n_ref={n_ref} n_fast={n_fast} max|diff|={worst:.2e}")
    if worst > EQUIV_TOL or n_ref != n_fast:
        print("EQUIVALENCE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    print("shim self-check (wma/maxdist/mindist vs pandas rolling)...")
    if not _shim_selfcheck():
        print("SHIM SELF-CHECK FAIL - aborting batch")
        sys.exit(1)

    print(f"building null baseline (K={N_NULLS} white-noise factors)...")
    thr = null_thresholds(close, fwd)
    for k, v in thr.items():
        print(f"  {k}: p95_abs_ic={v['p95_abs_ic']} p95_abs_ir={v['p95_abs_ir']}")

    print("running factor batch...")
    rows = run_batch(funcs, panels, fwd, thr)

    ok = [r for r in rows if r["status"] == "ok"]
    pool = [r["factor"] for r in ok if r.get("in_pool")]
    strong = [r["factor"] for r in ok if r.get("strong_tier")]
    skip_counts = {}
    for r in rows:
        if r["status"] != "ok":
            skip_counts[r["status"]] = skip_counts.get(r["status"], 0) + 1
    per_h_pass = {f"h{h}": sum(1 for r in ok if r.get(f"h{h}_pass"))
                  for h in HORIZONS}

    print(f"\n=== P-1a GTJA191 batch summary ===")
    print(f"  factors: {len(rows)} total, {len(ok)} computed, "
          f"skips={skip_counts}")
    print(f"  pool (A1-A4 any h): {len(pool)}  strong tier: {len(strong)}")
    print(f"  per-h pass: {per_h_pass}")
    if pool:
        print(f"  pool: {pool}")
    if strong:
        print(f"  strong: {strong}")

    os.makedirs(OUT_DIR, exist_ok=True)
    pd.DataFrame(rows).to_csv(
        os.path.join(RES_DIR, "gtja191_ic_results.csv"), index=False)

    out = {
        "meta": {
            "batch": "P-1a GTJA191 IC screening",
            "pre_reg": "research/shortline/P1_GTJA191_IC.md",
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "is_end": IS_END,
            "n_factors": len(funcs),
            "n_nulls": N_NULLS,
            "universe": f"core48 bare-code, {close.shape[1]} symbols, "
                        f"{close.shape[0]} dates",
            "strategy_ledger_note": "factor screening batch; strategy "
                                     "engine ledger N untouched",
            "elapsed_s": round(time.time() - t0, 1),
        },
        "equivalence_check": {"max_abs_diff": worst,
                              "n_ref": n_ref, "n_fast": n_fast,
                              "tol": EQUIV_TOL, "pass": worst <= EQUIV_TOL},
        "thresholds": thr,
        "counts": {"computed": len(ok), "skips": skip_counts,
                   "pool": len(pool), "strong": len(strong),
                   "per_h_pass": per_h_pass},
        "pool": pool,
        "strong_tier": strong,
        "rows": rows,
    }
    with open(os.path.join(OUT_DIR, "gtja191_ic.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nsaved: research/shortline/gtja191_ic_results.csv")
    print(f"saved: results/shortline/gtja191_ic.json")
    print(f"elapsed: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
