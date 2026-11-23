"""Throwaway probe (r2012 bm-c): is the negative lot drag a price tilt, or an
arithmetic artifact?  Re-derives the same grid and prints, per rebalance, the
mean forward return of names that *can* buy a lot versus those that cannot."""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from astock_resid_veto_layer import (  # noqa: E402
    FIRST_DATE, HOLD, LOOKBACK_BETA, daily_returns, load_panel, market_return, score_slice,
)

LOT = 100
CAPS = (1_000_000, 10_000_000)

dates, symbols, close, amount, shares = load_panel()
rets = daily_returns(close)
mkt = market_return(rets)
start = max(max([i for i, d in enumerate(dates) if d < FIRST_DATE] + [0]), LOOKBACK_BETA)

agg = {c: {"in": [], "out": [], "n_in": [], "n_out": [], "max_abs_fwd": [],
           "in_price": [], "out_price": []} for c in CAPS}
t = start
while t + HOLD < len(dates):
    idx, resid, q, fwd = score_slice(t, close, amount, shares, rets, mkt)
    if resid is None:
        t += HOLD
        continue
    cols = idx[q < 4]
    px = close[t][cols]
    f = fwd[q < 4]
    n = len(cols)
    for c in CAPS:
        slot = c / n
        lots = np.floor(slot / (LOT * px))
        good = np.isfinite(lots) & (lots > 0)
        a = agg[c]
        a["in"].append(float(np.mean(f[good])) if good.any() else float("nan"))
        a["out"].append(float(np.mean(f[~good])) if (~good).any() else float("nan"))
        a["n_in"].append(int(good.sum()))
        a["n_out"].append(int((~good).sum()))
        a["max_abs_fwd"].append(float(np.nanmax(np.abs(f))))
        a["in_price"].append(float(np.median(px[good])) if good.any() else float("nan"))
        a["out_price"].append(float(np.median(px[~good])) if (~good).any() else float("nan"))
    t += HOLD

for c in CAPS:
    a = agg[c]
    print("C=%s  periods=%d" % (format(c, ","), len(a["in"])))
    print("  mean n_in=%.1f n_out=%.1f" % (np.mean(a["n_in"]), np.mean(a["n_out"])))
    print("  mean fwd in =%+.4f%%  out=%+.4f%%  gap=%+.4f%%"
          % (np.nanmean(a["in"]) * 100, np.nanmean(a["out"]) * 100,
             (np.nanmean(a["in"]) - np.nanmean(a["out"])) * 100))
    print("  median price in=%.2f out=%.2f  max|fwd| median=%.1f%%"
          % (np.nanmedian(a["in_price"]), np.nanmedian(a["out_price"]),
             np.nanmedian(a["max_abs_fwd"]) * 100))
