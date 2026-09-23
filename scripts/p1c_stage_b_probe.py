"""P-1c Stage B probe (P1C_STOCK_IC.md SS5): streaming operator layer,
equivalence gates vs net-room reference semantics, full-universe timing.

Probe-first discipline (SS5 / O-2215 D1): the stock-pool IC full batch runs
only after this probe's gates PASS. The probe itself is engineering only:
zero statistical trials, ledger N unchanged.

Operators covered (net-room research/shortline/screening/gtja191_ops.py
semantics, mirrored exactly):
  - rolling mean      (pandas rolling(n).mean(), min_periods=n)
  - WMA/DECAYLINEAR   (_roll_weight: out[t]=sum_k w[k]*X[t-n+1+k],
                       NaN-propagating) -> scipy.signal.lfilter FIR stream
                       (b = reversed weights), numpy chunked-matmul fallback
  - HIGHDAY           (days since rolling n-day max, center-NaN kept NaN,
                       window NaN filled to -inf) -> column-blocked argmax
  - rolling Pearson   (pandas rolling(n).corr(), n jointly-valid pairs)
                       -> prefix-sum stream

Every replaced operator gets an equivalence gate (R9 einsum lesson) on BOTH
a real cache slice (incl. 688 columns + pre-listing NaN) and a synthetic
panel with punched NaN holes.
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
OUT_JSON = os.path.join(ROOT, "results", "shortline", "p1c_stage_b_probe.json")

try:
    from scipy.signal import lfilter
    HAVE_SCIPY = True
except ImportError:                                    # pragma: no cover
    HAVE_SCIPY = False

TOL = 1e-8          # equivalence tolerance: max(|a-b|) <= TOL * max(1,|ref|)
COL_CHUNK = 1024    # timing-leg column chunk (float64 T x chunk)
HD_BLOCK = 256      # HIGHDAY inner block
WMA_FALLBACK_BLOCK = 128


# ---------------------------------------------------------------- streaming

def _prefix(X):
    cs = np.cumsum(X, axis=0)
    head = np.zeros((1, X.shape[1]), dtype=X.dtype)
    return np.vstack([head, cs])


def roll_mean_stream(X, n):
    """Rolling mean; NaN if any NaN in the window (pandas min_periods=n)."""
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    Xf = np.where(np.isfinite(X), X, 0.0)
    s = _prefix(Xf)
    sa = s[n:] - s[:-n]
    k = _prefix((~np.isfinite(X)).astype(np.float64))
    kc = k[n:] - k[:-n]
    out[n - 1:] = np.where(kc == 0, sa / n, np.nan)
    return out


def roll_wma_stream(X, n, weights=None):
    """Rolling weighted sum, net-room _roll_weight semantics (NaN-propagating).

    out[t] = sum_k w[k] * X[t-n+1+k]   ->   FIR: b[m] = w[n-1-m], a=1.
    scipy lfilter carries NaN in state for exactly n-1 steps, identical to
    sliding-window NaN propagation; head rows t<n-1 overwritten to NaN.
    """
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    if weights is None:
        weights = np.arange(1, n + 1, dtype=float)
        weights = weights / weights.sum()
    if HAVE_SCIPY:
        y = lfilter(weights[::-1], [1.0], X, axis=0)
        out[n - 1:] = y[n - 1:]
        return out
    # fallback: chunked sliding-window matmul (bounded memory)
    for c0 in range(0, C, WMA_FALLBACK_BLOCK):
        c1 = min(c0 + WMA_FALLBACK_BLOCK, C)
        win = sliding_window_view(X[:, c0:c1], n, axis=0)  # (T-n+1, cb, n)
        out[n - 1:, c0:c1] = win @ weights
    return out


def roll_highday_stream(X, n, block=HD_BLOCK):
    """Days since rolling n-day max (0 = max today); center-NaN rows NaN."""
    T, C = X.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    for c0 in range(0, C, block):
        c1 = min(c0 + block, C)
        v = X[:, c0:c1]
        na = ~np.isfinite(v)
        vf = np.where(na, -np.inf, v)
        win = sliding_window_view(vf, n, axis=0)      # view, no copy
        res = ((n - 1) - win.argmax(axis=2)).astype(np.float64)
        res[na[n - 1:]] = np.nan
        out[n - 1:, c0:c1] = res
    return out


def roll_corr_stream(A, B, n):
    """Rolling Pearson; NaN unless n jointly-valid pairs in the window."""
    T, C = A.shape
    out = np.full((T, C), np.nan)
    if T < n:
        return out
    ok = np.isfinite(A) & np.isfinite(B)
    Af = np.where(ok, A, 0.0)
    Bf = np.where(ok, B, 0.0)
    sA, sB = _prefix(Af), _prefix(Bf)
    sAB, sAA, sBB = _prefix(Af * Bf), _prefix(Af * Af), _prefix(Bf * Bf)
    cnt = _prefix(ok.astype(np.float64))

    def d(S):
        return S[n:] - S[:-n]

    k = d(cnt)
    sa, sb, sab, saa, sbb = d(sA), d(sB), d(sAB), d(sAA), d(sBB)
    with np.errstate(invalid="ignore", divide="ignore"):
        cov = sab - sa * sb / n
        va = saa - sa * sa / n
        vb = sbb - sb * sb / n
        r = cov / np.sqrt(va * vb)
    out[n - 1:] = np.where(k == n, r, np.nan)
    return out


# ------------------------------------------------- reference (net-room) ops

def ref_roll_weight(values, weights):
    """Net-room _roll_weight, verbatim semantics."""
    T, C = values.shape
    K = len(weights)
    if T < K:
        return np.full((T, C), np.nan)
    win = sliding_window_view(values, K, axis=0)
    res = np.full((T, C), np.nan)
    res[K - 1:] = win @ weights
    return res


def ref_highday(A, n):
    """Net-room HIGHDAY, unblocked."""
    T, C = A.shape
    res = np.full((T, C), np.nan)
    if T >= n:
        vf = np.where(np.isfinite(A), A, -np.inf)
        win = sliding_window_view(vf, n, axis=0)
        res[n - 1:] = (n - 1) - win.argmax(axis=2)
    res[~np.isfinite(A)] = np.nan
    return res


# ------------------------------------------------------------------ gating

def _cmp(a, b, name, gate_rows):
    na, nb = np.isnan(a), np.isnan(b)
    mask_equal = bool((na == nb).all())
    m = ~na & ~nb
    if m.any():
        diff = float(np.max(np.abs(a[m] - b[m])))
        ref = float(np.max(np.maximum(np.abs(b[m]), 1.0)))
        ok = mask_equal and diff <= TOL * ref
    else:
        diff, ref = 0.0, 1.0
        ok = mask_equal
    gate_rows.append({"gate": name, "nan_mask_equal": mask_equal,
                      "max_abs_diff": diff, "tol_scale": ref, "pass": ok})
    return ok


def _gate_on_panel(X, gate_rows, tag):
    rng = np.random.default_rng(7)
    Bv = rng.normal(size=X.shape)
    w10 = np.arange(1, 11, dtype=float)
    w10 = w10 / w10.sum()
    ok = True
    ok &= _cmp(roll_mean_stream(X, 20),
               pd.DataFrame(X).rolling(20).mean().values,
               f"{tag}:roll_mean(20)", gate_rows)
    ok &= _cmp(roll_wma_stream(X, 10),
               ref_roll_weight(X, w10),
               f"{tag}:wma(10)", gate_rows)
    ok &= _cmp(roll_wma_stream(X, 10, weights=np.array(
        [2 * i / (10 * 11) for i in range(1, 11)])),
        ref_roll_weight(X, np.array([2 * i / (10 * 11)
                                     for i in range(1, 11)])),
        f"{tag}:decaylinear(10)", gate_rows)
    ok &= _cmp(roll_highday_stream(X, 20, block=64),
               ref_highday(X, 20),
               f"{tag}:highday(20)", gate_rows)
    ok &= _cmp(roll_corr_stream(X, Bv, 20),
               pd.DataFrame(X).rolling(20).corr(pd.DataFrame(Bv)).values,
               f"{tag}:corr(20)", gate_rows)
    return ok


def run_gates():
    gate_rows = []
    # real slice: mid-history rows, 120 syms, force-include 688 columns
    # column order = builder convention: sorted glob of bars dir (the builder
    # writes no syms.json; meta.json only records counts)
    meta = json.load(open(os.path.join(CACHE_DIR, "meta.json"), encoding="utf-8"))
    syms = [os.path.basename(p)[:-8]
            for p in sorted(glob.glob(os.path.join(BARS_DIR, "*.parquet")))]
    assert len(syms) == meta["shape"]["N"], "bars dir vs cache shape mismatch"
    N = meta["shape"]["N"]
    star_cols = [i for i, s in enumerate(syms)
                 if s.startswith("688") or s.startswith("689")][:20]
    rng = np.random.default_rng(20260923)
    cols = sorted(set(list(rng.choice(N, size=100, replace=False)) + star_cols))
    close = np.load(os.path.join(CACHE_DIR, "close.npy"), mmap_mode="r")
    r0 = 3000
    X = np.asarray(close[r0:r0 + 400, cols], dtype=np.float64)
    X = np.where(np.isfinite(X), X, np.nan)
    ok = _gate_on_panel(X, gate_rows, "real_slice")
    # synthetic NaN-hole panel (incl. an all-NaN column and a NaN run)
    Y = rng.normal(size=(200, 40))
    Y[50:70, 3] = np.nan
    Y[:, 7] = np.nan
    Y[120:126, 20:25] = np.nan
    ok &= _gate_on_panel(Y, gate_rows, "synthetic_holes")
    return ok, gate_rows


# ------------------------------------------------------------------ timing

def ic_pass(F, R, min_n=100):
    """Timing proxy: per-day cross-sectional spearman (argsort ranks).
    Production batch reuses the equivalence-gated fast IC from P-1a;
    this leg measures the per-factor IC cost envelope only."""
    T = F.shape[0]
    ics = np.full(T, np.nan)
    for t in range(T):
        f, r = F[t], R[t]
        m = np.isfinite(f) & np.isfinite(r)
        if m.sum() < min_n:
            continue
        fv, rv = f[m], r[m]
        fr = np.argsort(np.argsort(fv)).astype(float)
        rr = np.argsort(np.argsort(rv)).astype(float)
        fr -= fr.mean()
        rr -= rr.mean()
        den = float(np.sqrt((fr * fr).sum() * (rr * rr).sum()))
        if den > 0:
            ics[t] = float((fr * rr).sum() / den)
    return ics


def _load_chunked(field):
    mm = np.load(os.path.join(CACHE_DIR, field + ".npy"), mmap_mode="r")
    T, N = mm.shape
    out = np.empty((T, N), dtype=np.float64)
    for c0 in range(0, N, COL_CHUNK):
        c1 = min(c0 + COL_CHUNK, N)
        out[:, c0:c1] = np.asarray(mm[:, c0:c1], dtype=np.float64)
    return out


def run_timing():
    meta = json.load(open(os.path.join(CACHE_DIR, "meta.json"),
                          encoding="utf-8"))
    T, N = meta["shape"]["T"], meta["shape"]["N"]
    rows = {}
    close = _load_chunked("close")
    t0 = time.time()
    F_mean = roll_mean_stream(close, 20)
    rows["roll_mean_n20_full"] = round(time.time() - t0, 2)
    t0 = time.time()
    F_wma = roll_wma_stream(close, 10)
    rows["roll_wma_n10_full"] = round(time.time() - t0, 2)
    t0 = time.time()
    F_hd = roll_highday_stream(close, 20)
    rows["highday_n20_full"] = round(time.time() - t0, 2)
    volume = _load_chunked("volume")
    t0 = time.time()
    F_corr = roll_corr_stream(close, volume, 20)
    rows["corr_n20_full"] = round(time.time() - t0, 2)
    # forward 10d returns on the full universe (IC target side)
    t0 = time.time()
    FR = np.full((T, N), np.nan)
    FR[:-10] = close[10:] / close[:-10] - 1.0
    rows["fwd_ret_build"] = round(time.time() - t0, 2)
    t0 = time.time()
    ics = ic_pass(F_wma, FR)
    n_ic = int(np.isfinite(ics).sum())
    rows["ic_pass_full_wma"] = round(time.time() - t0, 2)
    # a heavy GTJA-style composite timing probe: mean->wma->highday chain
    t0 = time.time()
    F_chain = roll_wma_stream(roll_mean_stream(close, 20), 10)
    F_chain2 = roll_highday_stream(close, 20)
    _ = F_chain + F_chain2
    rows["chain_3ops_full"] = round(time.time() - t0, 2)
    peak_mb = round(close.nbytes / 1e6 * 2.2, 1)  # input+output rule of thumb
    return {"shape": {"T": T, "N": N}, "timings_sec": rows,
            "n_ic_days_measured": n_ic, "est_worker_peak_mb": peak_mb,
            "fir_path": "scipy.signal.lfilter" if HAVE_SCIPY
            else "numpy chunked matmul fallback"}


def project_eta(timing, n_factors=268, n_nulls=150, workers=12):
    t = timing["timings_sec"]
    per_factor = (t.get("roll_mean_n20_full", 0) + t.get("roll_wma_n10_full", 0)
                  + t.get("highday_n20_full", 0) + t.get("ic_pass_full_wma", 0)
                  ) / 3.0          # ~3 heavy ops per representative factor
    null_cost = t.get("ic_pass_full_wma", 0)
    serial = per_factor * n_factors + null_cost * n_nulls
    return {"per_factor_sec": round(per_factor, 2),
            "serial_total_sec": round(serial, 1),
            "serial_total_min": round(serial / 60, 1),
            "parallel_min_at_workers": round(serial / workers / 60, 1),
            "workers_assumed": workers,
            "n_factors_assumed": n_factors,
            "n_nulls_assumed": n_nulls}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "run"], default="selftest",
                    nargs="?")
    args = ap.parse_args()
    ok, gate_rows = run_gates()
    print(json.dumps(gate_rows, indent=2))
    if not ok:
        print("STAGE-B PROBE GATES FAIL", flush=True)
        sys.exit(1)
    if args.mode == "selftest":
        print("STAGE-B PROBE GATES PASS (selftest)", flush=True)
        sys.exit(0)
    timing = run_timing()
    eta = project_eta(timing)
    payload = {"batch": "P1C-StageB-probe",
               "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
               "gates_pass": ok, "gate_rows": gate_rows,
               "timing": timing, "eta": eta,
               "verdict": "PROBE_PASS -> full batch may start (next round)",
               "ledger_note": "engineering probe only, trials N unchanged"}
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)
    print("STAGE-B PROBE PASS", flush=True)


if __name__ == "__main__":
    main()
