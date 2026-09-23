import pandas as pd, numpy as np, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "Money02", "data", "bars")
out = {}
for sym in ["688001", "688008", "688981"]:
    p = os.path.join(BARS, sym + ".parquet")
    if not os.path.exists(p):
        out[sym] = "missing"
        continue
    df = pd.read_parquet(p).sort_values("date").reset_index(drop=True)
    v = df["volume"].to_numpy(float); a = df["amount"].to_numpy(float); c = df["close"].to_numpy(float)
    yr = df["date"].dt.year.to_numpy()
    m = (v > 0) & np.isfinite(v) & np.isfinite(a) & (c > 0)
    rows = {}
    for y in sorted(set(yr[m])):
        k = m & (yr == y)
        if k.sum() > 10:
            rows[int(y)] = round(float(np.median(a[k] / v[k] / c[k])), 5)
    out[sym] = rows
print(json.dumps(out, indent=2))
