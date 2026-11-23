"""r2009 bm-c probe: can today's bond-free book be priced into an order ticket
without re-running the whole engine?

The engine's sizing overlay (etf_robust_pf.open_to_open_equity, vol_target=0.08) reads
book_vol(picks_today over the last 60 bars) at the decision bar. That is a TODAY-only
quantity, so the scale can be reproduced without replaying the equity curve. This probe
checks that claim against the published live_picks before anything is written.
"""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import numpy as np
import pandas as pd

import etf_composite_pf as E
import etf_equity_alpha as A

t0 = time.time()
close, openp, amt, feats = E.build_panel()
print("build_panel %.1fs shape=%s" % (time.time() - t0, close.shape), flush=True)

close, openp, n_flip = A.repair_flips(close, openp)
cmap = A.load_class_map()
cls = A.classify(close.columns, cmap, close)
want = ("equity", "commodity", "convertible")
cols = [c for c in close.columns if cls[c] in want]
print("bond-free universe", len(cols), "flips repaired", n_flip, flush=True)

sc = E.build_score(close[cols], amt[cols], feats)
last = sc.index[-1]
s = sc.loc[last].dropna()
picks = list(s.nlargest(5).index)
print("last bar", last.date(), "picks", picks, flush=True)

face = json.load(open(os.path.join(ROOT, "results", "etf_nobond_vt.json"), encoding="utf-8"))
pub = [p["symbol"] for p in face["live_picks"]["picks"]]
print("published as_of", face["live_picks"]["as_of"], "picks", pub, flush=True)
print("MATCH", set(picks) == set(pub), flush=True)

op = openp.reindex(columns=close.columns)
rets = op.pct_change()
w = {p: 1.0 / 5.0 for p in picks}
window = rets.loc[:last].tail(60)[list(w)]
wv = np.array([w[k] for k in window.columns])
cov = window.cov().to_numpy()
est = float(np.sqrt(wv @ cov @ wv) * np.sqrt(252))
scale = float(min(1.0, max(0.0, 0.08 / est))) if est > 0 else 1.0
print("est_vol=%.4f scale=%.4f cash=%.4f  (window %s..%s n=%d)"
      % (est, scale, 1 - scale, window.index[0].date(), window.index[-1].date(),
         len(window)), flush=True)

px = op.loc[last]
for p in picks:
    price = float(px[p])
    print("  %s price=%.3f one_lot=%.1f weight=%.4f budget_at_1m=%.0f lots=%d"
          % (p, price, price * 100, w[p] * scale, w[p] * scale * 1_000_000,
             int(w[p] * scale * 1_000_000 // (price * 100))), flush=True)
print("elapsed %.1fs" % (time.time() - t0), flush=True)
