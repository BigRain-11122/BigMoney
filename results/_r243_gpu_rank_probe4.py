"""r243 debug probe 4: module + manual + numpy ref in ONE process."""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import gpu_factor_matrix as G  # noqa: E402

rng = np.random.default_rng(7)
T, N = 40, 30
x = rng.standard_normal((T, N))
y = rng.standard_normal((T, N))
valid = rng.random((T, N)) < 0.8
x[0, 6:12] = 1.5
x[:, -1] = np.nan
valid &= ~np.isnan(x) & ~np.isnan(y)

torch = G._import_torch()
dev = torch.device("cuda")
xt = torch.from_numpy(x).to(dev, torch.float64)
vt = torch.from_numpy(valid).to(dev)

avg_ranks, rank_ic, zscore = G._t_core(torch)
fr_t = avg_ranks(xt, vt).cpu().numpy()
fr_n = G._avg_rank_rows_np(x, valid)

print("col | valid | x | torch | numpy-ref")
for j in range(4, 15):
    print(f"{j:3d} | {valid[0, j]!s:5} | {x[0, j]:>7.3f} | "
          f"{fr_t[0, j]:>7.3f} | {fr_n[0, j]!r}")
print()
d = np.abs(fr_t - fr_n)
m = ~np.isnan(fr_t) & ~np.isnan(fr_n)
print("worst |d| on valid cells:", d[m].max() if m.any() else "empty")
bad = np.argwhere(m & (d > 1e-9))
print("n bad:", len(bad), bad[:6].tolist())
