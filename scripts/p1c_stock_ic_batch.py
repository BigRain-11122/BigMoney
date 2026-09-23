"""P-1c Stage-B full batch runner (P1C_STOCK_IC.md SS4/SS6, probe PASSED r49).

Subcommands (all idempotent via checkpoints, safe to kill/restart):
  selftest    offline gates: op-layer equivalence (p1c_bigpanel_ops), fast IC
              vs composite_ic.ic_series (<=1e-6), vendor load + one-formula smoke
  run-nulls   K=50 white-noise null lines (stock-pool, seeds 20260923+i)
  run-gtja    GTJA191 leg: per-factor checkpoint results/shortline/p1c_partial/
              (r32 net-room semantics via big-panel streaming op injection)
  run-wq      phase 2 (next round: WQ101 no-cap 82, harness adapter)
  finalize    aggregate checkpoints + V1/V2/V3 gate table (h10 primary) +
              results JSON/CSV + factor-ledger block (engine ledger untouched)

Conventions (P1C_STOCK_IC.md SS4, no rewrite):
  IS_END=2024-12-31 (composite_ic), fwd=close.shift(-h)/close-1, IC=rank-after-
  pairing spearman (_ic_series_fast), tradability mask = noise where close NaN.
Ledger: +computed +error +nulls (r32 factor-ledger accounting).
"""
import argparse
import glob
import importlib.util
import json
import os
import sys
import time
import types

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import p1c_bigpanel_ops as OPS          # streaming op layer (gated PASS r50)
from composite_ic import ic_series, stats_block, IS_END   # established methodology
from shortline_p1_ic import _ic_series_fast               # gated fast IC path

CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
EXT_DIR = os.path.join(ROOT, "research", "shortline", "external")
OUT_DIR = os.path.join(ROOT, "results", "shortline")
RES_DIR = os.path.join(ROOT, "research", "shortline")
PARTIAL_DIR = os.path.join(OUT_DIR, "p1c_partial")
NULLS_JSON = os.path.join(OUT_DIR, "p1c_nulls.json")
RESULT_JSON = os.path.join(OUT_DIR, "p1c_stock_ic.json")
RESULT_CSV = os.path.join(RES_DIR, "p1c_stock_ic_results.csv")

HORIZONS = [5, 10, 20]
N_NULLS = 50
SEED0 = 20260923
NULL_Q = 0.95
MIN_PERIODS_GATE = 500
V2_IR_LINE = 0.30          # pre-registered absolute IR line (SS4)
V1_FLOOR = 0.02            # pre-registered V1 floor
EQUIV_TOL = 1e-6
FIELDS = ["open", "high", "low", "close", "volume", "amount", "vwap",
          "turnover", "pct_chg"]


# ------------------------------------------------------------------ panels

def load_universe():
    meta = json.load(open(os.path.join(CACHE_DIR, "meta.json"),
                          encoding="utf-8"))
    syms = [os.path.basename(p)[:-8]
            for p in sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))]
    assert len(syms) == meta["shape"]["N"], "bars dir vs cache shape mismatch"
    dates = np.load(os.path.join(CACHE_DIR, "dates.npy"))
    idx = pd.to_datetime(dates, unit="us")
    return idx, syms, meta


def load_panels(idx, syms):
    """All 9 field panels, float64; OHLC ffilled (core48 harness convention)."""
    panels = {}
    for f in FIELDS:
        mm = np.load(os.path.join(CACHE_DIR, f + ".npy"), mmap_mode="r")
        arr = np.asarray(mm, dtype=np.float64)
        df = pd.DataFrame(arr, index=idx, columns=syms)
        if f in ("open", "high", "low", "close"):
            df = df.ffill()
        panels[f] = df
        del mm, arr
        print(f"  panel {f}: {df.shape} built", flush=True)
    return panels


def fwd_rets(panels):
    close = panels["close"]
    return {h: close.shift(-h) / close - 1.0 for h in HORIZONS}


# ------------------------------------------------------------ vendor loader

def _missing_op(*args, **kwargs):
    raise NotImplementedError("external op unavailable (ta-lib-free env)")


def _load_external(name, filename):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(EXT_DIR, filename))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_alpha191_bigpanel():
    """Vendor alpha191 with the big-panel streaming ops as lib.ops.factor_ops.

    Mirrors the r32/bm-a injection pattern; r32 finding: bodies use
    WMA/MIN/REGRESI/rolling_slope without importing them -> setattr post-load.
    """
    if "talib" not in sys.modules:
        talib = types.ModuleType("talib")
        talib.__getattr__ = lambda name: _missing_op
        sys.modules["talib"] = talib
    for pkg in ("lib", "lib.ops", "lib.utils"):
        if pkg not in sys.modules:
            m = types.ModuleType(pkg)
            m.__getattr__ = lambda name: _missing_op
            sys.modules[pkg] = m
    _load_external("lib.base", "gtja191_lib_base.py")
    _load_external("lib.utils.method_attrs", "gtja191_lib_method_attrs.py")
    sys.modules["lib.ops.factor_ops"] = OPS       # streaming big-panel layer
    mod = _load_external("alpha191_external", "gtja191_alpha191.py")
    for name in ("WMA", "MIN", "REGRESI", "rolling_slope"):
        setattr(mod, name, getattr(OPS, name))
    return mod


# ------------------------------------------------------------------- gates

def gates_v123(blk_is, blk_oos, thr_h):
    """Pre-registered V1/V2/V3 + n_periods (P1C_STOCK_IC.md SS4)."""
    if "ic_mean" not in blk_is or "ic_mean" not in blk_oos:
        return {"v1": False, "v2": False, "v3": False, "a3": False,
                "pass": False}
    v1 = abs(blk_is["ic_mean"]) > max(V1_FLOOR, thr_h["p95_abs_ic"])
    v2 = abs(blk_is["ic_ir"]) >= V2_IR_LINE
    v3 = ((blk_oos["ic_mean"] > 0) == (blk_is["ic_mean"] > 0)
          and abs(blk_oos["ic_mean"]) >= 0.5 * abs(blk_is["ic_mean"]))
    a3 = blk_is["n_periods"] >= MIN_PERIODS_GATE
    return {"v1": bool(v1), "v2": bool(v2), "v3": bool(v3),
            "a3": bool(a3), "pass": bool(v1 and v2 and v3 and a3)}


def _classify(exc):
    if isinstance(exc, NotImplementedError):
        return "skip_talib"
    if isinstance(exc, NameError):
        return "skip_qlib_or_missing_name"
    if isinstance(exc, KeyError):
        return "skip_missing_field"
    return "error"


# ------------------------------------------------------------------ legs

def run_nulls(panels, fwd):
    if os.path.exists(NULLS_JSON):
        print("nulls checkpoint exists, skip", flush=True)
        return json.load(open(NULLS_JSON, encoding="utf-8"))
    close = panels["close"]
    abs_means = {h: [] for h in HORIZONS}
    abs_irs = {h: [] for h in HORIZONS}
    t0 = time.time()
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED0 + k)
        vals = pd.DataFrame(rng.standard_normal(close.shape),
                            index=close.index, columns=close.columns)
        vals = vals.where(close.notna())      # tradability mask, same as real
        for h in HORIZONS:
            s = _ic_series_fast(vals, fwd[h])
            blk = stats_block(s[s.index <= IS_END])
            if "ic_mean" in blk:
                abs_means[h].append(abs(blk["ic_mean"]))
                abs_irs[h].append(abs(blk["ic_ir"]))
        del vals
        if (k + 1) % 10 == 0:
            print(f"  nulls {k + 1}/{N_NULLS} ({time.time() - t0:.0f}s)",
                  flush=True)
    thr = {f"h{h}": {
        "p95_abs_ic": round(float(np.quantile(abs_means[h], NULL_Q)), 4),
        "p95_abs_ir": round(float(np.quantile(abs_irs[h], NULL_Q)), 4),
        "n_nulls": len(abs_means[h]),
    } for h in HORIZONS}
    thr["meta"] = {"n_nulls": N_NULLS, "seed0": SEED0,
                   "mask": "white noise where close finite",
                   "elapsed_s": round(time.time() - t0, 1)}
    with open(NULLS_JSON, "w", encoding="utf-8") as f:
        json.dump(thr, f, indent=2, ensure_ascii=False)
    print(json.dumps(thr, indent=2), flush=True)
    return thr


def run_gtja(panels, fwd, thr, limit=0):
    mod = load_alpha191_bigpanel()
    funcs = {nm: fn for nm, fn in vars(mod).items()
            if nm.startswith("alpha191_") and callable(fn)}
    os.makedirs(PARTIAL_DIR, exist_ok=True)
    thr_h = {h: thr.get(f"h{h}", {"p95_abs_ic": 0.0}) for h in HORIZONS}
    todo = sorted(funcs.items())
    if limit:
        todo = todo[:limit]
    n_done = n_skip = n_err = 0
    t0 = time.time()
    for i, (nm, fn) in enumerate(todo, 1):
        ck = os.path.join(PARTIAL_DIR, nm + ".json")
        if os.path.exists(ck):
            n_done += 1
            continue
        rec = {"factor": nm, "status": "ok", "skip_reason": "",
               "compute_s": 0.0}
        tc = time.time()
        try:
            out = fn(panels)
        except Exception as e:
            rec["status"] = _classify(e)
            rec["skip_reason"] = f"{type(e).__name__}: {str(e)[:120]}"
            out = None
        if out is not None and (not isinstance(out, pd.DataFrame)
                                or out.empty):
            rec["status"] = "skip_not_implemented"
            rec["skip_reason"] = "empty or non-DataFrame output"
            out = None
        if out is None and rec["status"] == "ok":
            rec["status"] = "skip_not_implemented"
            rec["skip_reason"] = "returned None (unfinished stub)"
        if out is not None:
            rec["compute_s"] = round(time.time() - tc, 2)
            for h in HORIZONS:
                s = _ic_series_fast(out, fwd[h])
                blk_full = stats_block(s)
                blk_is = stats_block(s[s.index <= IS_END])
                blk_oos = stats_block(s[s.index > IS_END])
                g = gates_v123(blk_is, blk_oos, thr_h[h])
                p = f"h{h}_"
                for seg, blk in (("full", blk_full), ("is", blk_is),
                                 ("oos", blk_oos)):
                    rec[p + seg + "_ic"] = blk.get("ic_mean", "")
                    rec[p + seg + "_ir"] = blk.get("ic_ir", "")
                    rec[p + seg + "_n"] = blk.get("n_periods", 0)
                rec[p + "pass"] = g["pass"]
                if h == 10:
                    rec["gates"] = g
                    rec["in_pool"] = g["pass"]      # h10 = primary judgement
            del out
        with open(ck, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, ensure_ascii=False)
        if rec["status"] == "ok":
            n_done += 1
        elif rec["status"].startswith("skip"):
            n_skip += 1
        else:
            n_err += 1
        if i % 10 == 0:
            print(f"  {i}/{len(todo)} done={n_done} skip={n_skip} "
                  f"err={n_err} ({time.time() - t0:.0f}s)", flush=True)
    return {"todo": len(todo), "done": n_done, "skip": n_skip, "err": n_err}


def _chain_head_total():
    """Max trials_ledger.total across results/*.json AND results/shortline/*.json.

    R24 scan convention, extended r60: the factor-ledger series lives in
    results/shortline/ (P-1c 3028, P-1d 3238) and would be invisible to a
    top-level-only scan -> WQ finalize would fork the chain off the engine
    head (2791). Both dirs are one chain per the max-total convention.
    Legacy flat-list trials_ledger files are schema-skipped as before.
    """
    best = 0
    for sub in ("", os.path.join("shortline", "")):
        for p in glob.glob(os.path.join(ROOT, "results", sub, "*.json")):
            try:
                with open(p, encoding="utf-8") as f:
                    obj = json.load(f)
                tl = obj.get("trials_ledger")
                tot = tl.get("total", 0) if isinstance(tl, dict) else 0
                if isinstance(tot, (int, float)) and tot > best:
                    best = int(tot)
            except Exception:
                continue
    return best


def finalize():
    thr = json.load(open(NULLS_JSON, encoding="utf-8")) \
        if os.path.exists(NULLS_JSON) else None
    rows = []
    for p in sorted(glob.glob(os.path.join(PARTIAL_DIR, "*.json"))):
        try:
            with open(p, encoding="utf-8") as f:
                rows.append(json.load(f))
        except Exception:
            continue
    if not rows:
        print("no checkpoints yet", flush=True)
        return 1
    n_ok = sum(1 for r in rows if r["status"] == "ok")
    n_err = sum(1 for r in rows if r["status"] == "error")
    n_skip = sum(1 for r in rows if r["status"].startswith("skip"))
    # authoritative gate recompute from stored stats + null lines
    # (checkpoint gate flags are advisory; nulls are the batch's own)
    if thr:
        for r in rows:
            if r["status"] != "ok":
                continue
            for h in HORIZONS:
                blk_is = {"ic_mean": r.get(f"h{h}_is_ic"),
                          "ic_ir": r.get(f"h{h}_is_ir"),
                          "n_periods": r.get(f"h{h}_is_n", 0)}
                blk_oos = {"ic_mean": r.get(f"h{h}_oos_ic")}
                g = gates_v123(blk_is, blk_oos, thr[f"h{h}"])
                r[f"h{h}_pass"] = g["pass"]
                if h == 10:
                    r["gates"] = g
                    r["in_pool"] = g["pass"]
    pool = [r["factor"] for r in rows if r.get("in_pool")]
    per_h = {f"h{h}": sum(1 for r in rows if r.get(f"h{h}_pass"))
             for h in HORIZONS}
    prev = _chain_head_total()
    added = n_ok + n_err + (N_NULLS if thr else 0)
    out = {
        "meta": {
            "batch": "P-1c stock-pool GTJA191 IC (Stage-B full batch)",
            "pre_reg": "research/shortline/P1C_STOCK_IC.md",
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "is_end": str(IS_END),
            "universe": "stock pool 5129 ok + cache 5222 cols, T=8792",
            "op_layer": "scripts/p1c_bigpanel_ops.py (30/30 gates vs net-room)",
            "n_checkpoints": len(rows),
        },
        "thresholds": thr,
        "counts": {"ok": n_ok, "skip": n_skip, "error": n_err,
                   "pool_h10": len(pool), "per_h_pass": per_h},
        "pool_h10": pool,
        "trials_ledger": {"prev": prev, "added": added,
                          "total": prev + added,
                          "note": "factor-ledger accounting (r32): "
                                  "computed+error+nulls; engine N untouched"},
        "rows": rows,
    }
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    pd.DataFrame(rows).to_csv(RESULT_CSV, index=False)
    print(f"finalize: ok={n_ok} skip={n_skip} err={n_err} "
          f"pool={len(pool)} ledger {prev}->{prev + added}", flush=True)
    print(f"saved: {RESULT_JSON}", flush=True)
    return 0


# ---------------------------------------------------------------- selftest

def selftest():
    t0 = time.time()
    print("[1/3] op-layer equivalence gates (real slice + synthetic)...",
          flush=True)
    if not OPS.selftest():
        print("OP LAYER FAIL", flush=True)
        return 1
    idx, syms, meta = load_universe()
    print(f"[2/3] vendor load + one-formula smoke "
          f"(T={len(idx)} N={len(syms)})...", flush=True)
    mod = load_alpha191_bigpanel()
    funcs = {nm: fn for nm, fn in vars(mod).items()
             if nm.startswith("alpha191_") and callable(fn)}
    print(f"  {len(funcs)} alpha191 functions enumerated", flush=True)
    sl_cols = syms[:60]
    small = {f: pd.DataFrame(
        np.asarray(np.load(os.path.join(CACHE_DIR, f + ".npy"),
                           mmap_mode="r")[-600:, :60], dtype=np.float64),
        index=idx[-600:], columns=sl_cols) for f in FIELDS}
    for f in ("open", "high", "low", "close"):
        small[f] = small[f].ffill()
    probe_fn = funcs.get("alpha191_001") or funcs[min(funcs)]
    out = probe_fn(small)
    ok_form = out is not None and isinstance(out, pd.DataFrame) \
        and not out.empty and out.notna().any().any()
    print(f"  formula smoke alpha191_001: "
          f"{'OK' if ok_form else 'FAIL'} "
          f"shape={None if out is None else out.shape}", flush=True)
    if not ok_form:
        return 1
    print("[3/3] fast IC equivalence vs composite_ic.ic_series (slice)...",
          flush=True)
    close_full = small["close"]
    fwd20 = close_full.shift(-20) / close_full - 1.0
    probe = -close_full.pct_change(60)
    ref = ic_series(probe, fwd20)
    fast = _ic_series_fast(probe, fwd20)
    common = ref.index.intersection(fast.index)
    worst = float((ref[common] - fast[common]).abs().max()) \
        if len(common) else 9.9
    ok_ic = worst <= EQUIV_TOL and len(ref) == len(fast)
    print(f"  n_ref={len(ref)} n_fast={len(fast)} max|diff|={worst:.2e} "
          f"{'PASS' if ok_ic else 'FAIL'}", flush=True)
    print(f"SELFTEST {'PASS' if ok_ic else 'FAIL'} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return 0 if ok_ic else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode",
                    choices=["selftest", "run-nulls", "run-gtja", "run-wq",
                             "finalize", "status"])
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    if args.mode == "selftest":
        sys.exit(selftest())
    if args.mode == "status":
        ck = len(glob.glob(os.path.join(PARTIAL_DIR, "*.json")))
        print(f"checkpoints={ck} nulls={os.path.exists(NULLS_JSON)}",
              flush=True)
        sys.exit(0)
    if args.mode == "run-wq":
        print("phase 2 (next round): WQ101 no-cap 82 harness adapter",
              flush=True)
        sys.exit(0)
    idx, syms, meta = load_universe()
    panels = load_panels(idx, syms)
    fwd = fwd_rets(panels)
    if args.mode == "run-nulls":
        run_nulls(panels, fwd)
        sys.exit(0)
    if args.mode == "run-gtja":
        if not os.path.exists(NULLS_JSON):
            print("REFUSED: nulls checkpoint missing - run-nulls first "
                  "(prereg: no judgement without null lines)", flush=True)
            sys.exit(2)
        thr = json.load(open(NULLS_JSON, encoding="utf-8"))
        print(json.dumps({k: v for k, v in thr.items() if k != "meta"}),
              flush=True)
        r = run_gtja(panels, fwd, thr, limit=args.limit)
        print(json.dumps(r), flush=True)
        sys.exit(0)
    if args.mode == "finalize":
        sys.exit(finalize())


if __name__ == "__main__":
    main()
