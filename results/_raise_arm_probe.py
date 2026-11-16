"""timing probe: one panel build, two real arms, two random-score arms."""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "scripts"))

import etf_book_entry_gate as G      # noqa: E402
import etf_book_production as P      # noqa: E402
import etf_composite_pf as E         # noqa: E402

t0 = time.time()
close, openp, amt, feats, n_flip = G.build_universe()
print("panel %.1fs shapes=%s flips=%d" % (time.time() - t0, close.shape, n_flip), flush=True)

cfg = {"cost_bp_per_side": 10.0, "rebal": 20, "vol_target": 0.08}
rng = np.random.default_rng(20261116)

for gate in (20e6, 100e6):
    score = E.build_score(close, amt, feats, min_amt=gate)
    t = time.time()
    bt, ser = P.backtest(close, openp, amt, score.shift(1), 5, 20,
                         cost=1e-3, vol_target=0.08)
    print("gate %gM real cagr=%.4f  %.1fs bars=%d"
          % (gate / 1e6, bt["full"]["cagr"], time.time() - t, len(ser)), flush=True)
    t = time.time()
    rnd = score.copy()
    vals = score.values.copy()
    shape = vals.shape
    rnd_vals = rng.standard_normal(shape)
    rnd_vals[np.isnan(vals)] = np.nan
    import pandas as pd
    rnd = pd.DataFrame(rnd_vals, index=score.index, columns=score.columns)
    bt2, ser2 = P.backtest(close, openp, amt, rnd.shift(1), 5, 20,
                           cost=1e-3, vol_target=0.08)
    print("gate %gM random1 cagr=%.4f  %.1fs"
          % (gate / 1e6, bt2["full"]["cagr"], time.time() - t), flush=True)
