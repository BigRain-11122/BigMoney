# r219 debug: zoo85_stv / zoo93_arc all-NaN on production panel, PASS on synthetic.
# Real-slice stepwise repr probe (r125 repr-first discipline).
import os, sys
import numpy as np
import pandas as pd

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
CACHE = os.path.join(ROOT, "Money02", "data", "cache", "p1c_stock")

idx_all = np.load(os.path.join(CACHE, "dates.npy"))
idx = pd.to_datetime(idx_all[-1200:], unit="us")   # last ~1200 days
sl = slice(-1200, None)


def load(f, ffill=False):
    arr = np.asarray(np.load(os.path.join(CACHE, f + ".npy"), mmap_mode="r")[sl, :40],
                     dtype=np.float64)
    df = pd.DataFrame(arr, index=idx)
    if ffill:
        df = df.ffill()
    return df


close = load("close", True)
open_ = load("open", True)
tr = load("turnover")
vwap = load("vwap")
print("close notna share:", round(close.notna().mean().mean(), 3))
print("tr notna share:", round(tr.notna().mean().mean(), 3))
print("vwap notna share:", round(vwap.notna().mean().mean(), 3))
print("tr finite sample:", tr.iloc[-1].dropna().head(5).round(4).to_dict())
print("vwap finite sample:", vwap.iloc[-1].dropna().head(3).round(3).to_dict())

# ---- ARC stepwise
valid = close.notna() & tr.notna() & vwap.notna()
V = valid.values.astype(np.float64)
print("valid share:", round(valid.mean().mean(), 3))
TRc = np.clip(tr.values, 0.0, 0.99)
dC = np.where(V > 0, np.log1p(-TRc), 0.0)
print("dC finite share:", round(np.isfinite(dC).mean(), 4),
      "dC range:", float(np.nanmin(dC)), float(np.nanmax(dC)))
C = np.cumsum(dC, axis=0)
print("C end range:", C[-1].min(), C[-1].max())
X0 = np.where(V > 0, TRc, 0.0) * np.exp(-C)
print("X0 finite:", np.isfinite(X0).all(), "X0 max:", X0.max())
cs0 = np.cumsum(X0, axis=0)
rs0 = np.full_like(cs0, np.nan)
rs0[61:] = cs0[60:-1] - cs0[:-(61)]
print("rs0 finite share (t>=61):", round(np.isfinite(rs0[61:]).mean(), 4),
      "rs0 >0 share:", round((np.nan_to_num(rs0[61:], nan=-1) > 0).mean(), 4))
cs_v = np.cumsum(V, axis=0)
vc = np.full_like(cs_v, np.nan)
vc[61:] = cs_v[60:-1] - cs_v[:-(61)]
print("vc==60 share (t>=61):", round((vc[61:] == 60).mean(), 4))
ok = (vc == 60) & np.isfinite(rs0) & (rs0 > 0)
print("ok share (t>=61):", round(ok[61:].mean(), 4))

# ---- STV stepwise
rets = close / close.shift(1) - 1.0
absr = rets.abs()
cond_hi = absr.values >= 0.1
vals = np.where(cond_hi, absr.values * 100.0, tr.values)
vals[~np.isfinite(absr.values)] = np.nan
sigma_stv = pd.DataFrame(vals, index=rets.index)
rank = sigma_stv.rank(axis=1, ascending=False)
a = 0.7 ** rank
print("a nonzero share:", round((a.values > 0).mean(), 4),
      "a nan share:", round(np.isnan(a.values).mean(), 4))
b = a.mean(axis=1)
print("b finite:", b.notna().all(), "b range:", b.min(), b.max())
w = a.div(b, axis=0)
print("w nonzero share:", round((w.values > 0).mean(), 4))
stv = w.rolling(20).cov(rets)
print("stv notna share:", round(stv.notna().mean().mean(), 4))
# small-scale control: same math on 40 cols
print("stv col0 tail:", stv.iloc[:, 0].dropna().tail(3).round(4).to_list())
