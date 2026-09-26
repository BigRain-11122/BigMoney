"""r243 probe 6: real-data z-spot divergence dissection.

Replicates the runner's exact failing comparison (face 0, h=5, full-row
numpy ref vs full-batch torch z on the 200x60 spot window) and dumps the
worst-diff row: validity, finite/inf census, both engines' mu/sd/z values.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import gpu_factor_matrix as G           # noqa: E402
import p1e_ic_batch as P1E              # noqa: E402
import p1c_stock_ic_batch as P1C        # noqa: E402

idx, syms, meta, panels = P1E.load_panels({"close", "open", "tr", "vwap"})
fwd = P1C.fwd_rets({"close": panels["close"]})
faces, n_bad = G._build_faces(panels)
names = list(faces)
fh = fwd[5]
face0 = faces[names[0]]
T, N = len(idx), len(syms)

x = face0.values
valid_np = ~np.isnan(fh.values)
fvalid = ~np.isnan(x) & valid_np

torch = G._import_torch()
avg_ranks, rank_ic, zscore = G._t_core(torch)
dev = torch.device("cuda")

r0, c0 = max(T - 200, 0), max(N - 60, 0)
print(f"face0={names[0]} T={T} N={N} spot rows {r0}.. cols {c0}.. "
      f"n_bad_nonfinite={n_bad}")

# full-batch torch z (exactly like the runner: stack of K, but face 0 only
# suffices for the spot diagnosis)
xt = torch.from_numpy(x).to(dev, torch.float64)
vt = torch.from_numpy(fvalid).to(dev)
zs = zscore(xt, vt).cpu().numpy()

ref_full = G._masked_zscore_np(x, fvalid)          # full-row domain
ref = ref_full[r0:, c0:]
got = zs[r0:, c0:]
m = np.isfinite(ref)
d = np.abs(np.where(m, ref - got, 0.0))
i, j = np.unravel_index(d.argmax(), d.shape)
row, col = r0 + i, c0 + j
print(f"worst |d| = {d.max():.6e} at spot row {i} col {j} "
      f"(abs row {row} {idx[row].date()}, sym {syms[col]})")
print(f"ref={ref[i, j]!r} got={got[i, j]!r} valid={fvalid[row, col]} "
      f"x={x[row, col]!r}")

v = fvalid[row]
vals = x[row][v]
n_inf = int(np.isinf(vals).sum())
print(f"row {row}: n_valid={v.sum()} n_inf_in_valid={n_inf} "
      f"nan_in_valid={int(np.isnan(vals).sum())}")
print("  valid head:", np.round(vals[:8], 4).tolist())
mu_np, sd_np = vals.mean(), vals.std()
z_np = (x[row, col] - mu_np) / sd_np if sd_np > 0 else 0.0
print(f"  numpy mu={mu_np!r} sd={sd_np!r} z_at_col={z_np!r}")
vf = vt[row]
xs = torch.where(vt[row], xt[row], torch.zeros_like(xt[row])).to(dev)
mu_t = (xs * vf.to(xs.dtype)).sum() / vf.to(xs.dtype).sum()
dd = (xs - mu_t) * vf.to(xs.dtype)
sd_t = dd.pow(2).sum().div(vf.to(xs.dtype).sum()).sqrt()
print(f"  torch mu={mu_t.item()!r} sd={sd_t.item()!r} "
      f"z_at_col={got[i, j]!r}")
# also: how many spot-window rows have inf anywhere valid?
win_valid = fvalid[r0:, :]
inf_rows = int(np.isinf(np.where(win_valid, x[r0:, :], 0.0)).any(axis=1).sum())
print(f"spot window rows with inf at valid pos: {inf_rows}/200")
nan_ref_rows = int((~np.isfinite(ref_full[r0:, c0:])).all(axis=1).sum())
print(f"spot window rows all-nan-ref in window: {nan_ref_rows}/200")
