"""r615 bm-a: 688 volume/amount 100x drift spot-check on local p1c_stock cache.

Read-only probe vs Money02 bars (no writes). Evidence for MSG-0830 action 3:
verify bm-b hypothesis that bm-a cache stores 688xxx/689xxx volume/amount at
raw 100x (fix absent) -> inflated n_base on liquidity floors.
"""
import glob
import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "Money02", "data", "bars")
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")

files = sorted(glob.glob(os.path.join(BARS, "*.parquet")))
syms = [os.path.basename(p)[:-8] for p in files]
dates = np.load(os.path.join(CACHE, "dates.npy"))
vol_c = np.load(os.path.join(CACHE, "volume.npy"), mmap_mode="r")
amt_c = np.load(os.path.join(CACHE, "amount.npy"), mmap_mode="r")
close_c = np.load(os.path.join(CACHE, "close.npy"), mmap_mode="r")

out = {"meta_generated": json.load(open(os.path.join(CACHE, "meta.json"),
                                        encoding="utf-8"))["generated"],
       "spots": []}
for sym in ["688001", "688981", "600519"]:
    if sym not in syms:
        out["spots"].append({"sym": sym, "missing": True})
        continue
    j = syms.index(sym)
    rdf = pd.read_parquet(os.path.join(BARS, sym + ".parquet")
                          ).sort_values("date").reset_index(drop=True)
    dpos = np.searchsorted(dates, rdf["date"].values.astype("int64"))
    raw_v = rdf["volume"].to_numpy(float)
    raw_a = rdf["amount"].to_numpy(float)
    gv = np.asarray(vol_c[dpos, j], float)
    ga = np.asarray(amt_c[dpos, j], float)
    gc = np.asarray(close_c[dpos, j], float)
    ok = np.isfinite(gv) & np.isfinite(raw_v)
    rel_v = float(np.max(np.abs(gv[ok] - raw_v[ok])
                         / np.maximum(np.abs(raw_v[ok]), 1e-9)))
    ok = np.isfinite(ga) & np.isfinite(raw_a)
    rel_a = float(np.max(np.abs(ga[ok] - raw_a[ok])
                         / np.maximum(np.abs(raw_a[ok]), 1e-9)))
    ok = np.isfinite(ga) & np.isfinite(gc) & (gc > 0)
    amt_over_close = float(np.median(ga[ok] / gc[ok]))
    out["spots"].append({
        "sym": sym, "is_688": sym.startswith("688") or sym.startswith("689"),
        "cache_vs_raw_volume_rel": round(rel_v, 6),
        "cache_vs_raw_amount_rel": round(rel_a, 6),
        "median_amount_over_close": round(amt_over_close, 1),
        "verdict_100x_inflated": bool(rel_v > 50 or rel_a > 50),
    })
print(json.dumps(out, indent=1))
