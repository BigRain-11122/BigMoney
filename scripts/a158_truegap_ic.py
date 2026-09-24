"""A158_TRUEGAP_IC batch runner (research/shortline/A158_TRUEGAP_IC.md, FROZEN r119 bm-b).

Subcommands (prereg s6 frozen set: gates / run / selftest):
  selftest  offline engineering gates: affine-clone law (z faces, FP-precision
            disclosed), IdxMax/IdxMin boundary fixtures vs the qlib-verbatim
            rolling reference (bitwise), truncate-and-compare causality check
  gates     s2 data-completeness gates (frozen P-1c census T/N, ok-universe
            5129+/-1, pct_chg-vs-close agreement >=99% on 500 sampled stocks,
            high/low finite >=95% on close-finite cells, cutoff lockbox)
            -> results/shortline/a158_gates.json
  run       full batch: in-run gates re-check -> K=50 nulls (seeds
            science_gates.SEED_REGISTRY['a158_truegap_ic']+i, P-1c same-mask
            caliber, parallel RAM-clamped workers, checkpointed) -> 7
            features (5 primary + 2 affine-clone disclosure cols, per-factor
            checkpoints) -> h10 primary judgement + h5 report col for all +
            h20 report col only for h10 V1 passers (s3) -> authoritative
            V1/V2/V3/A3 via p1c gates_v123 import (no hand-copied lines) ->
            results JSON (evidence_cutoff top-level via science_gates.cutoff_meta,
            prereg_sha256 from the freeze commit) + cells CSV + unified ledger
            (science_gates.append_ledger, delta-idempotent P-1c r61 pattern).

Conventions (A158_TRUEGAP_IC.md s2/s3, P-1c lineage, no rewrite):
  panel = P-1c Stage-A cache (Money02/data/cache/p1c_stock, OHLC ffilled),
  IS <= 2024-12-31 (composite_ic.IS_END), fwd = close.shift(-h)/close-1,
  IC = shortline_p1_ic._ic_series_fast (rank-after-pairing spearman),
  tradability mask for nulls = ffilled close finite, cutoff = 2026-09-22.
Factor formulas = vendored loader strings, qlib ops.py semantics verbatim
(fetched from microsoft/qlib main 2026-09-24; IdxMax/IdxMin =
rolling(N, min_periods=1).apply(x.argmax()/argmin()+1, raw=True), window
chronological, position counts from window START). The vendored loader files
are NEVER imported (prereg s6).
"""
import argparse
import ctypes
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates
from composite_ic import xs_zscore, stats_block, IS_END
from shortline_p1_ic import _ic_series_fast
import p1c_stock_ic_batch as P1C   # harness: load_universe/load_panels/fwd_rets/gates_v123/_chain_head_total

# ------------------------------------------------------------------ frozen
WINDOW = 20                                # prereg s3: main window, frozen
HORIZONS = P1C.HORIZONS                    # [5, 10, 20] shared, not redefined
N_NULLS = P1C.N_NULLS                      # 50 shared
NULL_Q = P1C.NULL_Q                        # 0.95 shared
SEED0 = science_gates.SEED_REGISTRY["a158_truegap_ic"]   # 55_000, no hand-copy
SEED_KEY = "a158_truegap_ic"
CUTOFF = "2026-09-22"                      # prereg s2 forward lockbox
EPS = 1e-12                                # vendored loader denominators, verbatim
PREREG_REL = "research/shortline/A158_TRUEGAP_IC.md"
PREREG_FREEZE_COMMIT = "d958a1a"           # r119 freeze commit (git log --follow)
CACHE_DIR = P1C.CACHE_DIR
OUT_DIR = os.path.join(ROOT, "results", "shortline")
PARTIAL_DIR = os.path.join(OUT_DIR, "a158_partial")
GATES_JSON = os.path.join(OUT_DIR, "a158_gates.json")
NULLS_JSON = os.path.join(OUT_DIR, "a158_nulls.json")
RESULT_JSON = os.path.join(OUT_DIR, "a158_truegap_ic.json")
RESULT_CSV = os.path.join(ROOT, "research", "shortline",
                          "a158_truegap_ic_cells.csv")
# frozen P-1c Stage-A census (r105 census-drift law: refuse on regenerated cache)
CENSUS_T, CENSUS_N, CENSUS_OK_UNIVERSE = 8792, 5222, 5129

PRIMARY = ["IMAX20", "IMIN20", "IMXD20", "WVMA20", "VSUMP20"]
DISCLOSURE = ["VSUMN20", "VSUMD20"]
FAMILY = {"IMAX20": "aroon", "IMIN20": "aroon", "IMXD20": "aroon",
          "WVMA20": "vol_volume", "VSUMP20": "vol_rsi"}
FORMULA = {
    "IMAX20": "IdxMax($high, 20)/20",
    "IMIN20": "IdxMin($low, 20)/20",
    "IMXD20": "(IdxMax($high, 20)-IdxMin($low, 20))/20",
    "WVMA20": "Std(Abs($close/Ref($close,1)-1)*$volume,20)"
              "/(Mean(Abs($close/Ref($close,1)-1)*$volume,20)+1e-12)",
    "VSUMP20": "Sum(Greater($volume-Ref($volume,1),0),20)"
               "/(Sum(Abs($volume-Ref($volume,1)),20)+1e-12)",
    "VSUMN20": "1-VSUMP20 (affine clone, prereg s1)",
    "VSUMD20": "2*VSUMP20-1 (affine clone, prereg s1)",
}

_NULL_CTX = {}     # worker mmap paths, set by _worker_init


# ------------------------------------------------------------ utils
def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def set_priority_below_normal():
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass


def _free_ram_gb():
    try:
        class _MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        ms = _MS()
        ms.dwLength = ctypes.sizeof(_MS)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms)):
            avail = float(ms.ullAvailPhys) / 2 ** 30
            if avail > 0:
                return round(avail, 2)
    except Exception:
        pass
    return None


def _prereg_sha256():
    """sha256 of the prereg file content AT the freeze commit (s6 product)."""
    r = subprocess.run(["git", "show", f"{PREREG_FREEZE_COMMIT}:{PREREG_REL}"],
                       capture_output=True, cwd=ROOT)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError("prereg freeze-commit read failed: "
                           f"{r.stderr.decode('utf-8', 'replace')[:200]}")
    return hashlib.sha256(r.stdout).hexdigest()


# ---------------------------------------------------------- idx ops (qlib verbatim)
def _idx_qlib(values, n, kind):
    """Vectorized qlib ops.py IdxMax/IdxMin:
    rolling(n, min_periods=1).apply(lambda x: x.argmax()+1 / argmin()+1, raw=True)
    -- window chronological, position counts from window START (1..n).
    pandas min_periods counts NON-NaN values: an all-NaN window yields NaN
    (apply not called); a window with >=1 valid value gets argmax/argmin over
    the RAW window (NaN positions win argmax/argmin, numpy semantics).
    Full windows via sliding_window_view; head rows k<n via partial windows."""
    arr = np.asarray(values, dtype=np.float64)
    T = arr.shape[0]
    out = np.full(arr.shape, np.nan, dtype=np.float64)
    op = np.argmax if kind == "max" else np.argmin
    valid = ~np.isnan(arr)
    for k in range(1, min(n, T) + 1):
        v = op(arr[:k], axis=0) + 1.0
        out[k - 1] = np.where(valid[:k].any(axis=0), v, np.nan)
    if T >= n:
        sl = np.lib.stride_tricks.sliding_window_view(arr, n, axis=0)
        v = op(sl, axis=2) + 1.0
        cnt = np.lib.stride_tricks.sliding_window_view(valid, n,
                                                      axis=0).sum(axis=2)
        out[n - 1:] = np.where(cnt > 0, v, np.nan)
    return out


def _idx_reference(df, n, kind):
    """qlib ops.py reference implementation, verbatim (fetch-verified
    2026-09-24)."""
    if kind == "max":
        return df.rolling(n, min_periods=1).apply(
            lambda x: x.argmax() + 1, raw=True)
    return df.rolling(n, min_periods=1).apply(
        lambda x: x.argmin() + 1, raw=True)


# ---------------------------------------------------------- factor bodies
def _imx_raw(panels, kind):
    key, other = ("high", "low")
    if kind == "min":
        key, other = "low", "high"
    base = panels[key]
    raw = _idx_qlib(base.values, WINDOW, "max" if kind == "max" else "min")
    return raw, base.index, base.columns


def f_imax(panels):
    raw, idx, cols = _imx_raw(panels, "max")
    return pd.DataFrame(raw / WINDOW, index=idx, columns=cols)


def f_imin(panels):
    raw, idx, cols = _imx_raw(panels, "min")
    return pd.DataFrame(raw / WINDOW, index=idx, columns=cols)


def f_imxd(panels):
    raw_max, idx, cols = _imx_raw(panels, "max")
    raw_min, _, _ = _imx_raw(panels, "min")
    return pd.DataFrame((raw_max - raw_min) / WINDOW, index=idx, columns=cols)


def _wvma_base(panels):
    close, vol = panels["close"], panels["volume"]
    return (close / close.shift(1) - 1.0).abs() * vol


def f_wvma(panels):
    b = _wvma_base(panels)
    std20 = b.rolling(WINDOW, min_periods=1).std()
    mean20 = b.rolling(WINDOW, min_periods=1).mean()
    return std20 / (mean20 + EPS)


def _dv(panels):
    vol = panels["volume"]
    dv = vol - vol.shift(1)
    up = pd.DataFrame(np.maximum(dv.values, 0.0), index=dv.index,
                      columns=dv.columns)
    ab = pd.DataFrame(np.abs(dv.values), index=dv.index, columns=dv.columns)
    return up, ab


def f_vsump(panels):
    up, ab = _dv(panels)
    num = up.rolling(WINDOW, min_periods=1).sum()
    den = ab.rolling(WINDOW, min_periods=1).sum()
    return num / (den + EPS)


def f_vsumn(panels):
    """Disclosure col, affine clone law (prereg s1): VSUMN = 1 - VSUMP."""
    v = f_vsump(panels)
    return 1.0 - v


def f_vsumd(panels):
    """Disclosure col, affine clone law (prereg s1): VSUMD = 2*VSUMP - 1."""
    v = f_vsump(panels)
    return 2.0 * v - 1.0


def f_vsumn_from_string(panels):
    """Independent loader-string path (selftest cross-check only, NOT the
    batch definition): Sum(Greater(Ref($v,1)-$v,0),20)/(Sum(Abs($v-Ref($v,1)),20)+1e-12)."""
    vol = panels["volume"]
    dv = vol - vol.shift(1)
    down = pd.DataFrame(np.maximum((-dv).values, 0.0), index=dv.index,
                        columns=dv.columns)
    ab = pd.DataFrame(np.abs(dv.values), index=dv.index, columns=dv.columns)
    den = ab.rolling(WINDOW, min_periods=1).sum()
    return down.rolling(WINDOW, min_periods=1).sum() / (den + EPS)


FACTORS = {"IMAX20": (f_imax, ("high",)),
           "IMIN20": (f_imin, ("low",)),
           "IMXD20": (f_imxd, ("high", "low")),
           "WVMA20": (f_wvma, ("close", "volume")),
           "VSUMP20": (f_vsump, ("volume",)),
           "VSUMN20": (f_vsumn, ("volume",)),
           "VSUMD20": (f_vsumd, ("volume",))}


# ------------------------------------------------------------- nulls (K=50)
def _worker_init(paths):
    set_priority_below_normal()
    _NULL_CTX.clear()
    _NULL_CTX.update(paths)


def _null_task(k):
    """One null seed, all horizons; IS-segment stats (P-1c null-line caliber:
    rng.standard_normal panel masked to ffilled-close-finite cells)."""
    dates = pd.to_datetime(np.load(_NULL_CTX["dates"], mmap_mode="r"))
    mask = np.asarray(np.load(_NULL_CTX["mask"], mmap_mode="r"), dtype=bool)
    T, N = mask.shape
    rng = np.random.default_rng(SEED0 + k)
    vals = rng.standard_normal((T, N))
    vals[~mask] = np.nan
    fdf = pd.DataFrame(vals, index=dates)
    del vals
    res = {"k": k}
    for h in HORIZONS:
        fwd = np.asarray(np.load(_NULL_CTX["fwd"][h], mmap_mode="r"))
        rdf = pd.DataFrame(fwd, index=dates)
        s = _ic_series_fast(fdf, rdf)
        blk = stats_block(s[s.index <= IS_END])
        res[f"h{h}"] = {"is_ic_mean": blk.get("ic_mean", ""),
                        "is_ic_ir": blk.get("ic_ir", "")}
        del fwd, rdf, s
    return res


def run_nulls(tmp_paths):
    t0 = time.time()
    avail = _free_ram_gb()
    if avail is not None and avail < 4.0:
        print(f"REFUSED: free RAM {avail}GB < 4GB (shared-machine guard)",
              flush=True)
        return None
    if avail is None:
        workers = 2
    elif avail >= 9.0:
        workers = 3
    elif avail >= 6.0:
        workers = 2
    else:
        workers = 1
    print(f"nulls: K={N_NULLS} seed0={SEED0} workers={workers} "
          f"(free_ram={avail}GB, BelowNormal)", flush=True)
    results = {}
    ck_path = os.path.join(OUT_DIR, "a158_nulls_runs.jsonl")
    if os.path.exists(ck_path):
        with open(ck_path, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    r = json.loads(ln)
                    results[r["k"]] = r
        print(f"nulls checkpoint: {len(results)}/{N_NULLS} done, resume",
              flush=True)
    todo = [k for k in range(N_NULLS) if k not in results]
    from concurrent.futures import ProcessPoolExecutor
    with open(ck_path, "a", encoding="utf-8") as ckf, \
            ProcessPoolExecutor(max_workers=workers,
                                initializer=_worker_init,
                                initargs=(tmp_paths,)) as ex:
        for res in ex.map(_null_task, todo, chunksize=1):
            results[res["k"]] = res
            ckf.write(json.dumps(res) + "\n")   # incremental R41 checkpoint
            ckf.flush()
            if len(results) % 10 == 0:
                print(f"  nulls {len(results)}/{N_NULLS} "
                      f"({time.time() - t0:.0f}s)", flush=True)
    if len(results) < N_NULLS:
        print(f"REFUSED: nulls incomplete {len(results)}/{N_NULLS}",
              flush=True)
        return None
    abs_means = {h: [] for h in HORIZONS}
    abs_irs = {h: [] for h in HORIZONS}
    for r in results.values():
        for h in HORIZONS:
            m, ir = r[f"h{h}"]["is_ic_mean"], r[f"h{h}"]["is_ic_ir"]
            if m != "" and m is not None:
                abs_means[h].append(abs(m))
                abs_irs[h].append(abs(ir))
    thr = {f"h{h}": {
        "p95_abs_ic": round(float(np.quantile(abs_means[h], NULL_Q)), 4),
        "p95_abs_ir": round(float(np.quantile(abs_irs[h], NULL_Q)), 4),
        "n_nulls": len(abs_means[h]),
    } for h in HORIZONS}
    thr["meta"] = {"n_nulls": N_NULLS, "seed0": int(SEED0),
                   "seed_registry_key": SEED_KEY,
                   "mask": "white noise where ffilled close finite (P-1c "
                           "run_nulls caliber, same-mask law)",
                   "workers": workers, "elapsed_s": round(time.time() - t0, 1),
                   "runner": "scripts/a158_truegap_ic.py"}
    with open(NULLS_JSON, "w", encoding="utf-8") as f:
        json.dump(thr, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in thr.items() if k != "meta"}),
          flush=True)
    return thr


# ---------------------------------------------------------------- gates (s2)
def run_gates(write=True):
    t0 = time.time()
    idx, syms, meta = P1C.load_universe()
    T, N = int(meta["shape"]["T"]), int(meta["shape"]["N"])
    census_ok = (T == CENSUS_T and N == CENSUS_N)
    ok_universe = int(meta.get("ok_universe", -1))
    ok_gate = abs(ok_universe - CENSUS_OK_UNIVERSE) <= 1
    last_date = str(idx[-1].date())
    lockbox_ok = last_date <= CUTOFF

    # pct_chg vs close-derived agreement, 500 sampled stocks (prereg s2)
    rng = np.random.default_rng(0)
    sel = np.sort(rng.choice(N, size=min(500, N), replace=False))
    close_s = pd.DataFrame(
        np.asarray(np.load(os.path.join(CACHE_DIR, "close.npy"),
                           mmap_mode="r")[:, sel], dtype=np.float64)).ffill()
    pct_s = np.asarray(np.load(os.path.join(CACHE_DIR, "pct_chg.npy"),
                               mmap_mode="r")[:, sel], dtype=np.float64)
    derived = close_s / close_s.shift(1) - 1.0
    p = pct_s[1:]
    d = derived.values[1:]
    both = np.isfinite(p) & np.isfinite(d)
    agree_raw = float((np.abs(p - d)[both] <= 1e-4).mean()) if both.any() else 0.0
    agree_pct = float((np.abs(p / 100.0 - d)[both] <= 1e-4).mean()) \
        if both.any() else 0.0
    unit = "raw" if agree_raw >= agree_pct else "percent"
    agreement = max(agree_raw, agree_pct)
    pct_gate = agreement >= 0.99

    # high/low finite fraction on close-finite cells (prereg s2: >=95%)
    cdf = pd.DataFrame(np.asarray(np.load(os.path.join(CACHE_DIR, "close.npy"),
                                          mmap_mode="r"),
                                  dtype=np.float64)).ffill()
    cfin = np.isfinite(cdf.values)
    del cdf
    tot_finite = hfin = lfin = 0
    for i0 in range(0, T, 512):
        i1 = min(i0 + 512, T)
        m = cfin[i0:i1]
        tot_finite += int(m.sum())
        hfin += int(np.isfinite(np.asarray(
            np.load(os.path.join(CACHE_DIR, "high.npy"),
                    mmap_mode="r")[i0:i1], dtype=np.float64))[m].sum())
        lfin += int(np.isfinite(np.asarray(
            np.load(os.path.join(CACHE_DIR, "low.npy"),
                    mmap_mode="r")[i0:i1], dtype=np.float64))[m].sum())
    del cfin
    hl_frac = (min(hfin, lfin) / tot_finite) if tot_finite else 0.0
    hl_gate = hl_frac >= 0.95

    is_days = int((idx <= pd.Timestamp(IS_END)).sum())
    report = {
        "meta": {"batch": "A158_TRUEGAP_IC data gates (prereg s2)",
                 "date": _now(), "elapsed_s": round(time.time() - t0, 1)},
        "census": {"T": T, "N": N, "expect_T": CENSUS_T, "expect_N": CENSUS_N,
                   "ok": bool(census_ok),
                   "law": "r105 census-drift: refuse regenerated P-1c cache"},
        "universe": {"ok_universe": ok_universe, "expect": CENSUS_OK_UNIVERSE,
                     "tolerance": 1, "ok": bool(ok_gate)},
        "cutoff_lockbox": {"panel_last_date": last_date, "cutoff": CUTOFF,
                           "ok": bool(lockbox_ok)},
        "pct_chg_check": {"n_sampled": int(len(sel)), "seed": 0,
                          "n_cells": int(both.sum()), "unit_detected": unit,
                          "agreement": round(agreement, 6), "ok": bool(pct_gate)},
        "high_low_finite": {"frac": round(hl_frac, 6), "ok": bool(hl_gate)},
        "is_days_report": is_days,
        "pass": bool(census_ok and ok_gate and lockbox_ok and pct_gate
                     and hl_gate),
    }
    if write:
        with open(GATES_JSON, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"gates saved: {GATES_JSON}", flush=True)
    print(json.dumps({k: v for k, v in report.items()
                     if k in ("census", "universe", "cutoff_lockbox",
                              "pct_chg_check", "high_low_finite", "pass")},
                     indent=1), flush=True)
    return report["pass"], report


# ------------------------------------------------------------- factor leg
def _ic_stats(frame, fwd_frame):
    out = {}
    for h, ff in fwd_frame.items():
        s = _ic_series_fast(frame, ff)
        blk_full = stats_block(s)
        blk_is = stats_block(s[s.index <= IS_END])
        blk_oos = stats_block(s[s.index > IS_END])
        p = f"h{h}_"
        for seg, blk in (("full", blk_full), ("is", blk_is), ("oos", blk_oos)):
            out[p + seg + "_ic"] = blk.get("ic_mean", "")
            out[p + seg + "_ir"] = blk.get("ic_ir", "")
            out[p + seg + "_n"] = blk.get("n_periods", 0)
        del s
    return out


def run_factors(panels, fwd_frames, thr):
    os.makedirs(PARTIAL_DIR, exist_ok=True)
    rows = []
    for name in PRIMARY + DISCLOSURE:
        ck = os.path.join(PARTIAL_DIR, name + ".json")
        if os.path.exists(ck):
            with open(ck, encoding="utf-8") as f:
                rows.append(json.load(f))
            print(f"  {name}: checkpoint exists, skip", flush=True)
            continue
        t0 = time.time()
        fn, fields = FACTORS[name]
        rec = {"factor": name, "family": FAMILY.get(name, "disclosure"),
               "disclosure": name in DISCLOSURE, "status": "ok",
               "formula": FORMULA[name], "compute_s": 0.0}
        try:
            frame = fn(panels)
            rec["compute_s"] = round(time.time() - t0, 2)
            # h5 report col (all) + h10 primary judgement
            stats = _ic_stats(frame, {h: fwd_frames[h] for h in (5, 10)})
            rec.update(stats)
            blk_is = {"ic_mean": rec["h10_is_ic"], "ic_ir": rec["h10_is_ir"],
                      "n_periods": rec["h10_is_n"]}
            blk_oos = {"ic_mean": rec["h10_oos_ic"]}
            g10 = P1C.gates_v123(blk_is, blk_oos, thr["h10"])
            rec["gates"] = g10
            rec["in_pool"] = bool(g10["pass"] and not rec["disclosure"])
            if g10["v1"]:      # s3: h20 report col only for h10 V1 passers
                rec.update(_ic_stats(frame, {20: fwd_frames[20]}))
                rec["h20_computed"] = True
            else:
                rec["h20_computed"] = False
            if not rec["disclosure"]:
                z = xs_zscore(frame)
                rec["daily_mean_z"] = [round(float(x), 6) if np.isfinite(x)
                                       else None for x in z.mean(axis=1)]
            del frame
        except Exception as e:
            rec["status"] = "error"
            rec["error"] = f"{type(e).__name__}: {str(e)[:200]}"
        with open(ck, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2, ensure_ascii=False)
        rows.append(rec)
        print(f"  {name}: {rec['status']} compute={rec['compute_s']}s "
              f"h10_pass={rec.get('gates', {}).get('pass')}", flush=True)
    return rows


# ------------------------------------------------------------- corr gate (s1)
def corr_table(rows):
    series = {r["factor"]: pd.Series(
        [np.nan if v is None else v for v in r["daily_mean_z"]])
        for r in rows if not r.get("disclosure") and r["status"] == "ok"
        and "daily_mean_z" in r}
    pairs, cross = [], []
    names = [n for n in PRIMARY if n in series]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = series[names[i]], series[names[j]]
            m = a.notna() & b.notna()
            n_days = int(m.sum())
            same = FAMILY[names[i]] == FAMILY[names[j]]
            entry = {"pair": f"{names[i]}|{names[j]}", "same_mechanism": same,
                     "n_days": n_days}
            if n_days >= 200:
                c = float(np.corrcoef(a[m], b[m])[0, 1])
                entry["corr"] = round(c, 4)
                if not same:
                    cross.append((f"{names[i]}|{names[j]}", c))
            else:
                entry["corr"] = None
                entry["note"] = "overlap < 200 trading days, NA per s1"
            pairs.append(entry)
    valid = [abs(p["corr"]) for p in pairs if p.get("corr") is not None]
    cross_valid = [abs(c) for _, c in cross]
    return {"estimator": "pearson on daily cross-sectional mean-z series, "
                         "pairwise-complete days (>=200 required)",
            "pairs": pairs,
            "max_abs_corr": round(max(valid), 4) if valid else None,
            "max_abs_cross_mechanism": round(max(cross_valid), 4)
            if cross_valid else None,
            "cross_unexpected_ge_0.7": [p for p, c in cross if abs(c) >= 0.7]}


# ------------------------------------------------------------- assembly
def assemble(rows, thr, gates_report, prereg_sha, elapsed_s, workers_note):
    # authoritative gate recompute from stored stats + null lines
    # (P-1c finalize pattern: checkpoint flags advisory, nulls are own)
    for r in rows:
        if r["status"] != "ok":
            continue
        for h in HORIZONS:
            if f"h{h}_is_ic" not in r:
                r[f"h{h}_pass"] = None
                continue
            blk_is = {"ic_mean": r.get(f"h{h}_is_ic"),
                      "ic_ir": r.get(f"h{h}_is_ir"),
                      "n_periods": r.get(f"h{h}_is_n", 0)}
            blk_oos = {"ic_mean": r.get(f"h{h}_oos_ic")}
            g = P1C.gates_v123(blk_is, blk_oos, thr[f"h{h}"])
            r[f"h{h}_pass"] = g["pass"]
            if h == 10:
                r["gates"] = g
                r["in_pool"] = bool(g["pass"] and not r["disclosure"])
    prim = [r for r in rows if not r["disclosure"] and r["status"] == "ok"]
    pool_h10 = [r["factor"] for r in prim if r.get("in_pool")]
    per_h = {f"h{h}": sum(1 for r in prim if r.get(f"h{h}_pass"))
             for h in HORIZONS}
    fams = {}
    for fam in ("aroon", "vol_volume", "vol_rsi"):
        members = [r for r in prim if r["family"] == fam]
        fams[fam] = {"members": [r["factor"] for r in members],
                     "pass_members": [r["factor"] for r in members
                                      if r.get("in_pool")],
                     "any_pass": bool(any(r.get("in_pool") for r in members))}
    corr = corr_table(rows)

    # delta-idempotent unified ledger (P-1c r61 pattern; s0 itemization:
    # cells + nulls(once) + h5 cols + h20 cols produced)
    old = None
    if os.path.exists(RESULT_JSON):
        try:
            with open(RESULT_JSON, encoding="utf-8") as f:
                old = json.load(f)
        except Exception:
            old = None
    old_factors = {r.get("factor") for r in (old or {}).get("rows", [])}
    new_cells = [r for r in rows if r["factor"] not in old_factors
                 and r["status"] in ("ok", "error")]
    if old is not None and not new_cells:
        ledger = (old or {}).get("trials_ledger") or science_gates.append_ledger(
            "a158_truegap_ic", 0, file_name=RESULT_JSON,
            prev_total=P1C._chain_head_total(), evidence_cutoff=CUTOFF,
            note="zero-delta re-finalize keeps frozen ledger block (P-1c r61)")
    else:
        n_h20 = sum(1 for r in new_cells if r.get("h20_computed"))
        trials = (len(new_cells)                   # 5 primary + 2 disclosure cells
                  + (N_NULLS if old is None else 0)  # nulls, exactly once
                  + len(new_cells)                  # h5 report cols (all cells)
                  + n_h20)                           # h20 report cols (V1 passers)
        ledger = science_gates.append_ledger(
            "a158_truegap_ic", trials, file_name=RESULT_JSON,
            prev_total=P1C._chain_head_total(), evidence_cutoff=CUTOFF,
            note="s0 itemization: 5 primary + 2 affine-clone disclosure cells "
                 f"+ {N_NULLS} nulls (once) + {len(new_cells)} h5 report cols + "
                 f"{n_h20} h20 report cols (h10 V1 passers only, s3)")

    n_ok = sum(1 for r in rows if r["status"] == "ok")
    n_err = sum(1 for r in rows if r["status"] == "error")
    out = {
        "meta": {
            "batch": "A158_TRUEGAP_IC Alpha158 true-gap 7-family stock-pool "
                     "small-K IC reference batch (daily, h10 primary)",
            "pre_reg": PREREG_REL,
            "prereg_sha256": prereg_sha,
            "prereg_freeze_commit": PREREG_FREEZE_COMMIT,
            "date": _now(),
            "is_end": str(IS_END),
            "cutoff": CUTOFF,
            "universe": f"P-1c Stage-A cache ok set {gates_report['universe']['ok_universe']}"
                        f" (+{gates_report['census']['N'] - gates_report['universe']['ok_universe']}"
                        f" cache cols), T={gates_report['census']['T']}",
            "window": WINDOW,
            "horizons": HORIZONS,
            "h_policy": "h10 primary judgement; h5 report col all; h20 report "
                        "col only h10 V1 passers (prereg s3)",
            "elapsed_s": round(elapsed_s, 1),
            "workers": workers_note,
            "n_checkpoints": len(rows),
            "gates_file": "results/shortline/a158_gates.json",
        },
        "evidence_cutoff": CUTOFF,      # science_gates.cutoff_meta value, top level
        "thresholds": thr,
        "corr_disclosure": corr,
        "counts": {"ok": n_ok, "error": n_err,
                   "primary_total": len(PRIMARY), "primary_pass_h10": len(pool_h10),
                   "per_h_primary_pass": per_h,
                   "disclosure_cols": len(rows) - len(prim)},
        "pool_h10": pool_h10,
        "families": fams,
        "trials_ledger": ledger,
        "rows": rows,
    }
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    csv_rows = [{k: v for k, v in r.items() if k != "daily_mean_z"}
                for r in rows]
    pd.DataFrame(csv_rows).to_csv(RESULT_CSV, index=False)
    print(f"assemble: ok={n_ok} err={n_err} primary_pass_h10={len(pool_h10)} "
          f"per_h={per_h}", flush=True)
    print(f"ledger: {json.dumps(ledger)}", flush=True)
    print(f"corr max|corr|={corr['max_abs_corr']} "
          f"cross={corr['max_abs_cross_mechanism']}", flush=True)
    print(f"saved: {RESULT_JSON}", flush=True)
    print(f"saved: {RESULT_CSV}", flush=True)
    return 0


# ------------------------------------------------------------------- run
def run():
    t0 = time.time()
    set_priority_below_normal()      # O-1136: batch legs BelowNormal self-set
    ok, gates_report = run_gates(write=True)
    if not ok:
        print("REFUSED: s2 data gates FAIL (see above)", flush=True)
        return 2
    prereg_sha = _prereg_sha256()
    idx_full, syms, meta = P1C.load_universe()
    cutoff_ts = pd.Timestamp(CUTOFF)

    # temp memmaps shared with null workers (%TEMP%, never in git)
    tmp = tempfile.mkdtemp(prefix="a158_tmp_", dir=tempfile.gettempdir())
    try:
        if shutil.disk_usage(tmp).free < 2 * 2 ** 30:
            print("REFUSED: <2GB free in TEMP for shared memmaps", flush=True)
            return 2
        panels = P1C.load_panels(idx_full, syms)
        for f in ("open", "amount", "vwap", "turnover", "pct_chg"):
            panels.pop(f)
        if idx_full[-1] > cutoff_ts:
            n_drop = int((idx_full > cutoff_ts).sum())
            print(f"lockbox: dropping {n_drop} bars after {CUTOFF} "
                  f"(no post-cutoff data enters this batch)", flush=True)
            panels = {k: df.loc[:cutoff_ts] for k, df in panels.items()}
        idx = panels["close"].index
        fwd = P1C.fwd_rets(panels)
        mask_path = os.path.join(tmp, "mask.npy")
        np.save(mask_path, np.isfinite(panels["close"].values))
        dates_path = os.path.join(tmp, "dates.npy")
        np.save(dates_path, idx.values)
        fwd_paths = {}
        for h in HORIZONS:
            fp = os.path.join(tmp, f"fwd{h}.npy")
            np.save(fp, np.ascontiguousarray(fwd[h].values))
            fwd_paths[h] = fp
        paths = {"mask": mask_path, "dates": dates_path, "fwd": fwd_paths}
        fwd = None

        thr = None
        if os.path.exists(NULLS_JSON):
            print("nulls checkpoint exists, skip", flush=True)
            with open(NULLS_JSON, encoding="utf-8") as f:
                thr = json.load(f)
        else:
            thr = run_nulls(paths)
            if thr is None:
                return 2

        # zero-copy fwd frames over the temp memmaps (factor IC legs).
        # r121 P0 fix: re-attach the symbol columns -- the memmap round-trip
        # dropped them (RangeIndex), and _ic_series_fast aligns on BOTH index
        # and columns, so symbol-keyed factor frames vs RangeIndex fwd frames
        # produced an empty column intersection -> empty IC series ->
        # stats_block skip-block (no ic_mean) -> "" string into gates_v123
        # abs() TypeError. Nulls leg was RangeIndex-vs-RangeIndex (unaffected).
        fwd_frames = {h: pd.DataFrame(
            np.asarray(np.load(paths["fwd"][h], mmap_mode="r")), index=idx,
            columns=panels["close"].columns)
            for h in HORIZONS}
        rows = run_factors(panels, fwd_frames, thr)
        workers_note = thr.get("meta", {}).get("workers", "checkpointed-skip")
        return assemble(rows, thr, gates_report, prereg_sha,
                        time.time() - t0, workers_note)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------- selftest
def selftest():
    t0 = time.time()
    print("[1/3] affine-clone law (prereg s1: VSUMN=1-VSUMP, VSUMD=2*VSUMP-1)...",
          flush=True)
    rng = np.random.default_rng(7)
    T, N = 120, 40
    vol = pd.DataFrame(np.abs(rng.standard_normal((T, N)) * 1e7) + 1e4)
    vol.iloc[3, 5] = np.nan
    vol.iloc[10:14, 20] = np.nan
    pans = {"volume": vol}
    vsump = f_vsump(pans)
    vsumn, vsumd = f_vsumn(pans), f_vsumd(pans)
    zp, zn, zd = xs_zscore(vsump), xs_zscore(vsumn), xs_zscore(vsumd)
    m = zp.notna()
    d1 = float((zn[m] + zp[m]).abs().max().max())
    d2 = float((zd[m] - zp[m]).abs().max().max())
    # frozen "bitwise" identity holds in exact arithmetic; FP rounding on the
    # z faces is bounded and disclosed here (rank faces mirror exactly)
    ok_aff = d1 <= 1e-9 and d2 <= 1e-9
    vsumn_str = f_vsumn_from_string(pans)
    ok_str = bool(np.allclose(vsumn_str.values[m.values], vsumn.values[m.values],
                              rtol=1e-12, atol=0.0))
    print(f"  max|z(VSUMN)+z(VSUMP)|={d1:.2e} max|z(VSUMD)-z(VSUMP)|={d2:.2e} "
          f"{'PASS' if ok_aff else 'FAIL'}; loader-string cross-check "
          f"{'PASS' if ok_str else 'FAIL'}", flush=True)

    print("[2/3] IdxMax/IdxMin boundary fixtures vs qlib-verbatim reference...",
          flush=True)
    idx = pd.date_range("2020-01-01", periods=40, freq="D")
    highs = pd.DataFrame({
        "fresh_today": [50 - i for i in range(39)] + [50.0],      # max at end
        "stale_head": [99.0] + list(range(40, 79)),          # max at head
        "ties": [10.0] * 20 + [5.0] * 20,                         # tie block
        "nan_block": [np.nan] * 10 + list(np.arange(29.0)) + [7.0],
    }, index=idx)
    ok_idx = True
    for kind in ("max", "min"):
        mine = pd.DataFrame(_idx_qlib(highs.values, 20, kind), index=idx,
                            columns=highs.columns)
        ref = _idx_reference(highs, 20, kind)
        same = bool(np.array_equal(mine.values, ref.values, equal_nan=True))
        ok_idx &= same
        print(f"  Idx{kind}: vectorized vs qlib reference "
              f"{'BITWISE PASS' if same else 'FAIL'}", flush=True)
    if 20 > 1:   # partial-head invariance on a T<n slice
        short = pd.DataFrame(highs.values[:12], index=idx[:12])
        s_mine = _idx_qlib(short.values, 20, "max")
        s_ref = _idx_reference(short, 20, "max").values
        ok_idx &= bool(np.array_equal(s_mine, s_ref, equal_nan=True))

    print("[3/3] truncate-and-compare causality (real cache slice)...",
          flush=True)
    idxc, syms, _ = P1C.load_universe()
    sl_c, sl_n = idxc[-600:], 30
    hi = pd.DataFrame(np.asarray(
        np.load(os.path.join(CACHE_DIR, "high.npy"), mmap_mode="r")[-600:, :30],
        dtype=np.float64), index=sl_c, columns=syms[:30]).ffill()
    lo = pd.DataFrame(np.asarray(
        np.load(os.path.join(CACHE_DIR, "low.npy"), mmap_mode="r")[-600:, :30],
        dtype=np.float64), index=sl_c, columns=syms[:30]).ffill()
    cl = pd.DataFrame(np.asarray(
        np.load(os.path.join(CACHE_DIR, "close.npy"), mmap_mode="r")[-600:, :30],
        dtype=np.float64), index=sl_c, columns=syms[:30]).ffill()
    vo = pd.DataFrame(np.asarray(
        np.load(os.path.join(CACHE_DIR, "volume.npy"), mmap_mode="r")[-600:, :30],
        dtype=np.float64), index=sl_c, columns=syms[:30])
    cut = 400
    ok_caus = True
    full_max = _idx_qlib(hi.values, 20, "max")
    trunc_max = _idx_qlib(hi.values[:cut], 20, "max")
    ok_caus &= bool(np.array_equal(full_max[20:cut], trunc_max[20:cut],
                                   equal_nan=True))
    pans_full = {"close": cl, "volume": vo}
    pans_trunc = {"close": cl.iloc[:cut], "volume": vo.iloc[:cut]}
    for nm, fn in (("WVMA20", f_wvma), ("VSUMP20", f_vsump)):
        a, b = fn(pans_full).values, fn(pans_trunc).values
        ok_caus &= bool(np.array_equal(a[25:cut], b[25:cut], equal_nan=True))
    print(f"  IMAX/WVMA/VSUMP truncation-invariance rows<{cut}: "
          f"{'PASS' if ok_caus else 'FAIL'}", flush=True)
    all_ok = bool(ok_aff and ok_str and ok_idx and ok_caus)
    print(f"SELFTEST {'PASS' if all_ok else 'FAIL'} "
          f"({time.time() - t0:.0f}s)", flush=True)
    return 0 if all_ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["selftest", "gates", "run"])
    args = ap.parse_args()
    if args.mode == "selftest":
        sys.exit(selftest())
    if args.mode == "gates":
        ok, _ = run_gates(write=True)
        sys.exit(0 if ok else 1)
    sys.exit(run())


if __name__ == "__main__":
    main()
