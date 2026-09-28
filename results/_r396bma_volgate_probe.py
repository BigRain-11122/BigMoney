# r396 bm-a: VOL-gate probe face (pre-run fact anchor for TRIAL_LABOR_W4_PREREG sec.2)
# Deterministic, zero-network, point-in-time. Facts -> DIGEST-20260928-w4-volgate-supply-scan.md sec.3.
import pandas as pd
import numpy as np

df = pd.read_csv("data/daily/sh510300.csv")
df.columns = [c.strip() for c in df.columns]
dc = df[df.columns[0]]
cl = df[[c for c in df.columns if c.lower() in ("close", "收盘", "收盘价")][0]].astype(float)
ret = cl / cl.shift(1) - 1
vol20 = ret.rolling(20, min_periods=20).std(ddof=1)
med500 = vol20.rolling(500, min_periods=500).median()
state = pd.Series("closed", index=df.index, dtype=object)
ok = vol20.notna() & med500.notna()
state[ok & (vol20 <= med500)] = "calm"
state[ok & (vol20 > med500)] = "wild"

i0 = med500.first_valid_index()
print("rows", len(df), dc.iloc[0], "->", dc.iloc[-1])
print("med500 first valid bar-idx", i0, "date", dc.iloc[i0], "closed-NaN bars", int((~ok).sum()))
print("calm", int((state == "calm").sum()), "wild", int((state == "wild").sum()))
for d in ["2015-07-27", "2016-01-04", "2024-02-28", "2024-09-24", "2024-09-30",
          "2025-04-07", "2026-01-19", "2014-12-31", "2020-03-10"]:
    m = dc.astype(str).str.startswith(d)
    if m.any():
        i = m[m].index[0]
        v, md = vol20.iloc[i], med500.iloc[i]
        print(d, state.iloc[i],
              "vol20=%.5f" % v if not pd.isna(v) else "nan",
              "med500=%.5f" % md if not pd.isna(md) else "nan")
