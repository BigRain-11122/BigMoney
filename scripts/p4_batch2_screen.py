"""P-4 batch 2 stock-pool screen -- R38 of research/shortline/P4_BATCH2.md s7.

R38 is split by the O-1820 CEO red-line gate (MSG-1845 sequencing):
  R38-a  `panel`   build-once float32 price panel + validation gates.
                   This is DATA ENGINEERING ONLY -- no batch run, no signal
                   ranking, no allocation semantics; eligibility masks
                   (incl. ST-regime proxy, loss-dimension when bm-a's
                   financial source lands) are computed at screen time,
                   so the panel is robust to either gate outcome.
  R38-b  (next round) 7-family signal builders + fill_guard board-truth
                   table + null machinery + probe timing.
  run    `run`     REFUSES with exit 2 until research/shortline/
                   R38_RUN_CLEARANCE.md exists (bm-a financial source
                   connected, or explicit GM/CEO ruling on the compromise
                   reading) -- conservative clause R-pei1 is otherwise
                   unenforceable pool-wide -> zero-output batch. Exit 3
                   once clearance exists but R38-b is not yet built.

Panel spec (frozen P4_BATCH2.md s2/s3):
  window 2015-01-01 -> 2026-09-22 (evidence_cutoff, J16 anchor pattern)
  include symbol iff >=20 in-window bars (min listing; spec s2)
  columns [open, high, low, close, volume, amount, pct_chg] float32
  layout (T, N, 7) -- cross-sectional ops get contiguous day rows
  cache: Money02/data/cache/p4_batch2_panel/ (gitignored, regenerable)
  bars parquet prices are ALREADY forward-adjusted -- factor.json sidecars
  are reference metadata, never applied again (P-1c Stage-A lesson).
  pct_chg column = official exchange daily change (raw, ex-div aware) --
  the ONLY valid input for limit-up/down board detection (spec s3.1).

Validation gates (all must PASS; products -> results/
shortline_p4_batch2_panel.json):
  P1 window edges: first date >= 2015-01-01, last date == 2026-09-22
  P2 counts: N symbols (>=20 bars), board mix = stock prefixes
             60/00/30/68 only (no fund/ETF leak), excluded tally
  P3 dtype float32 + NaN density report per column (gaps = suspensions)
  P4 spot check: 3 symbols full 7-col in-window slice bitwise-equal to a
     fresh parquet read cast to float32 (equal_nan=True)
  P5 determinism spot check: 50 deterministic-picked symbols re-read
     through the same worker path -> slices bitwise identical
  P6 sha256 of panel_prices.npy recorded; meta carries build params

Usage:
  python scripts/p4_batch2_screen.py panel
  python scripts/p4_batch2_screen.py run      (gated, exit 2 until clearance)
"""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS_DIR = os.path.join(ROOT, "Money02", "data", "bars")
CACHE_DIR = os.path.join(ROOT, "Money02", "data", "cache", "p4_batch2_panel")
OUT_JSON = os.path.join(ROOT, "results", "shortline_p4_batch2_panel.json")
CLEARANCE = os.path.join(ROOT, "research", "shortline", "R38_RUN_CLEARANCE.md")

WINDOW_START = np.datetime64("2015-01-01")
CUTOFF = np.datetime64("2026-09-22")
MIN_BARS = 20
COLS = ["open", "high", "low", "close", "volume", "amount", "pct_chg"]
WORKERS = 12          # O-1738 policy: bm-b 16 cores -> <= 12 workers
SPOT_SYMS = ["000001", "300750", "688981"]
DET_PICK_STRIDE = 97  # deterministic G5 re-read sample (50 of ~4900)

_BARS_DIR = None


def _init_worker(bars_dir):
    global _BARS_DIR
    _BARS_DIR = bars_dir


def _load_one(args):
    """Read one parquet, slice to frozen window, drop <MIN_BARS.

    Returns (sym, dates64[D] ndarray, arr float32 (n,7)) or (sym, None, None).
    """
    sym, = args
    import pandas as pd
    try:
        df = pd.read_parquet(os.path.join(_BARS_DIR, sym + ".parquet"))
    except Exception:
        return (sym, None, None)
    d = df["date"].to_numpy().astype("datetime64[D]")
    m = (d >= WINDOW_START) & (d <= CUTOFF)
    if int(m.sum()) < MIN_BARS:
        return (sym, None, None)
    arr = df.loc[m, COLS].to_numpy(dtype=np.float32)
    return (sym, d[m], np.ascontiguousarray(arr))


def _jsonable(x):
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, np.ndarray):
        return [_jsonable(v) for v in x.tolist()]
    return x


def build_panel():
    t0 = time.time()
    syms = sorted(f[:-8] for f in os.listdir(BARS_DIR) if f.endswith(".parquet"))
    kept, excluded_short = {}, 0
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=_init_worker,
                             initargs=(BARS_DIR,)) as ex:
        for sym, d, arr in ex.map(_load_one, [(s,) for s in syms], chunksize=32):
            if d is None:
                excluded_short += 1
            else:
                kept[sym] = (d, arr)
    codes = sorted(kept)
    dates = np.unique(np.concatenate([kept[c][0] for c in codes]))
    T, N = len(dates), len(codes)
    panel = np.full((T, N, 7), np.nan, dtype=np.float32)
    for j, c in enumerate(codes):
        d, arr = kept[c]
        panel[np.searchsorted(dates, d), j, :] = arr
    return dates, np.array(codes), panel, time.time() - t0, excluded_short, len(syms)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(dates, codes, panel):
    global _BARS_DIR
    _BARS_DIR = BARS_DIR  # P4/P5 re-reads happen in the main process too
    gates, detail = {}, {}
    # P1 window edges
    gates["P1_window"] = bool(dates[0] >= WINDOW_START and dates[-1] == CUTOFF)
    # P2 counts + board mix (stock prefixes only, no fund/ETF leak)
    pref = {p: int(sum(1 for c in codes if c.startswith(p)))
            for p in ("60", "00", "30", "68")}
    gates["P2_counts"] = bool(all(pref[p] > 0 for p in pref)
                              and sum(pref.values()) == len(codes)
                              and not any(c.startswith(("51", "15", "58"))
                                          for c in codes))
    # P3 dtype + NaN density per column
    nan_frac = {col: float(np.isnan(panel[:, :, k]).mean())
                for k, col in enumerate(COLS)}
    gates["P3_dtype_nan"] = bool(panel.dtype == np.float32
                                  and all(v < 0.9 for v in nan_frac.values()))
    # P4 spot check vs fresh parquet read (bitwise after float32 cast)
    code_idx = {c: j for j, c in enumerate(codes)}
    p4_ok, p4_detail = True, {}
    for s in SPOT_SYMS:
        if s not in code_idx:
            p4_detail[s] = "missing_from_panel"
            p4_ok = False
            continue
        _, sym_d, sym_arr = _load_one((s,))
        got = panel[np.isin(dates, sym_d), code_idx[s], :]
        ok = bool(np.array_equal(got, sym_arr, equal_nan=True))
        p4_detail[s] = ok
        p4_ok = p4_ok and ok
    gates["P4_spot_bitwise"] = p4_ok
    # P5 determinism spot: re-read 50 deterministic symbols, compare slices
    picks = codes[::DET_PICK_STRIDE][:50]
    p5_fail = 0
    for s in picks:
        _, sym_d, sym_arr = _load_one((s,))
        if sym_d is None:
            continue
        got = panel[np.isin(dates, sym_d), code_idx[s], :]
        if not np.array_equal(got, sym_arr, equal_nan=True):
            p5_fail += 1
    gates["P5_determinism_50"] = bool(p5_fail == 0)
    detail["nan_frac_by_col"] = nan_frac
    detail["p4_detail"] = p4_detail
    detail["det_picks"] = len(picks)
    detail["board_mix"] = pref
    return gates, detail


def cmd_panel():
    os.makedirs(CACHE_DIR, exist_ok=True)
    dates, codes, panel, elapsed, excluded_short, scanned = build_panel()
    gates, detail = validate(dates, codes, panel)
    p_path = os.path.join(CACHE_DIR, "panel_prices.npy")
    np.save(p_path, panel)
    np.save(os.path.join(CACHE_DIR, "panel_dates.npy"), dates)
    np.save(os.path.join(CACHE_DIR, "panel_symbols.npy"), codes)
    T, N = panel.shape[0], panel.shape[1]
    payload = {
        "stage": "R38-a panel build (data engineering only, zero engine runs)",
        "gate_context": ("batch runs deferred per O-1820/MSG-1845: bars lack "
                         "fundamentals -> R-pei1 unverifiable pool-wide -> "
                         "conservative literal execution = zero output; run "
                         "subcommand gated on research/shortline/"
                         "R38_RUN_CLEARANCE.md"),
        "window": {"start": "2015-01-01", "end": "2026-09-22", "days": int(T)},
        "symbols": {"included": int(N),
                    "excluded_under_20_bars": int(excluded_short),
                    "scanned_parquet": int(scanned),
                    "board_mix": pref_detail(detail)},
        "dtype": "float32", "layout": "(T,N,7)", "columns": COLS,
        "workers": WORKERS, "build_seconds": round(elapsed, 2),
        "cache": {"dir": os.path.relpath(CACHE_DIR, ROOT),
                  "panel_prices_sha256": sha256_file(p_path),
                  "panel_bytes": int(os.path.getsize(p_path))},
        "nan_frac_by_col": detail["nan_frac_by_col"],
        "gates": gates, "all_pass": all(gates.values()),
        "trials_n_delta": 0, "engine_runs": 0,
        "meta_note": ("prices already forward-adjusted in bars parquet "
                      "(P-1c lesson: sidecar factors never applied); pct_chg "
                      "= official raw daily change, sole limit-detection "
                      "input per spec s3.1"),
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(_jsonable(payload), f, ensure_ascii=False, indent=2)
    print(_jsonable({"T": T, "N": N, "workers": WORKERS,
                     "build_seconds": payload["build_seconds"],
                     "gates": gates, "all_pass": payload["all_pass"]}))
    return 0 if payload["all_pass"] else 1


def pref_detail(detail):
    return detail["board_mix"]


def cmd_run():
    if not os.path.exists(CLEARANCE):
        print("EXIT 2: batch runs deferred per O-1820 (MSG-1845 sequencing) -- "
              "awaiting bm-a financial source (akshare fundamentals+ST) or an "
              "explicit GM/CEO ruling on the compromise pre-filter reading. "
              "Create research/shortline/R38_RUN_CLEARANCE.md with the "
              "signoff to unlock.")
        return 2
    print("EXIT 3: clearance found, but R38-b (builders + null machinery + "
          "probe) not implemented yet -- next round.")
    return 3


def main(argv):
    if len(argv) != 2 or argv[1] not in ("panel", "run"):
        print(__doc__)
        return 1
    return {"panel": cmd_panel, "run": cmd_run}[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
