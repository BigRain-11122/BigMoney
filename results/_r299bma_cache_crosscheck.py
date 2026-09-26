"""R299 bm-a P1C cache vs bars cross-check (facts only).

Resolves the cache-gate question for CN_SECTOR_LEADER_P1: cache meta says
generated=2026-09-23 18:12:59 while scripts/wild_route_lab.py asserts
'2026-09-24 03:42:50' (WILD-S1 closed runner; latent-gate note, not this
batch's lane). This probe validates the cache against the bars source of
truth on a sample so the sector-leader batch can use the (T,N) aligned
panel with an honest own gate.
"""
import glob
import json
import os
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "Money02", "data", "bars")
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")
OUT = os.path.join(ROOT, "results", "_r299bma_cache_crosscheck.json")

t0 = time.time()
idx = pd.to_datetime(np.load(os.path.join(CACHE, "dates.npy")), unit="us")
close = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")
amount = np.load(os.path.join(CACHE, "amount.npy"), mmap_mode="r")
syms = [os.path.basename(p)[:-8] for p in sorted(glob.glob(os.path.join(BARS, "*.parquet")))]
T, N = len(idx), len(syms)

# date alignment probe: cache dates vs a bars file's dates
picks = ["000001", "600519", "300750", "688111", "sh-none"]
res = {"cache_T": T, "cache_N": N, "bars_files": len(syms),
       "cache_last_date": str(idx[-1].date()),
       "sym_alphabet": None}
for sym in ["000001", "600519", "300750", "688111"]:
    p = os.path.join(BARS, sym + ".parquet")
    if not os.path.exists(p):
        continue
    df = pd.read_parquet(p)
    j = syms.index(sym)
    cc = np.asarray(close[:, j], dtype=np.float64)
    # align by date string
    dmap = {str(d)[:10]: i for i, d in enumerate(idx)}
    rows = [i for i, d in enumerate(df["date"].astype(str).str[:10]) if d in dmap]
    cch = cc[[dmap[df["date"].astype(str).str[:10].iloc[i]] for i in rows]]
    cbar = df["close"].values.astype(np.float64)[rows]
    m = np.isfinite(cch) & np.isfinite(cbar)
    both_nan = (~np.isfinite(cch) & ~np.isfinite(cbar)).sum()
    max_dev = float(np.max(np.abs(cch[m] - cbar[m]))) if m.any() else None
    fin_mismatch = int((np.isfinite(cch) != np.isfinite(cbar)).sum())
    res[sym] = {"rows_aligned": len(rows), "finite_match_dev_max": max_dev,
                 "finite_mask_mismatches": fin_mismatch, "both_nan": int(both_nan)}

# full-panel end-date cutoff + all-symbols last-finite-date distribution
fin_last = np.isfinite(np.asarray(close[-1]))
res["last_bar_finite_n"] = int(fin_last.sum())
res["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
