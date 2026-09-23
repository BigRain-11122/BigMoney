"""Rigorous validation of the V8-free refresh path: truncate 3 days, refresh,
compare appended bars against the original akshare-fetched REAL data."""
import shutil
import time
from pathlib import Path

import pandas as pd

import config as C
import data as D

SCRATCH = C.BARS_DIR / "_selftest"
SCRATCH.mkdir(exist_ok=True)
ltd = D.last_trade_date()
print("ltd =", ltd)

for code in ["000001", "600519", "300750"]:
    orig = pd.read_parquet(D._bar_path(code))
    dst = SCRATCH / f"{code}.parquet"
    trunc = orig.iloc[:-3].copy()
    trunc.to_parquet(dst, index=False)

    t0 = time.time()
    status = D.refresh_stock(code, dst, ltd)
    took = time.time() - t0
    new = pd.read_parquet(dst).set_index("date")
    o = orig.set_index("date")
    tail_dates = o.index[-3:]

    print(f"\n{code}: status={status} ({took:.1f}s) rows {len(trunc)} -> {len(new)}")
    for d in tail_dates:
        a, b = new.loc[d], o.loc[d]
        # day3 = qt quote (real amount); earlier gap days = TX raw (approx amount)
        rel = abs(float(a["close"]) / float(b["close"]) - 1)
        amt_rel = abs(float(a["amount"]) / float(b["amount"]) - 1)
        print(f"  {d.date()} close_err={rel*100:.3f}% amount_err={amt_rel*100:.2f}% "
              f"vol={a['volume']:.0f}/{b['volume']:.0f} shares={a['outstanding_share']:.3e}/{b['outstanding_share']:.3e}")
shutil.rmtree(SCRATCH, ignore_errors=True)
print("REFRESH TEST DONE")
