# -*- coding: utf-8 -*-
"""R258 bm-a: 688 turnover_derived unit probe (slice-D cap defect forensics).

Hypothesis A: turnover_derived[688] = (volume/100)/osh  (doc-frozen scheme
materialized) -> osh_est = (volume/100)/turnover_derived is correct.
Hypothesis B: turnover_derived[688] = volume/osh (uncorrected 100x face)
-> osh_est must be volume/turnover_derived (no extra /100).
Decisive face: turnover_derived magnitude by board (real daily turnover
~0.1%-10% = 0.001..0.10) + osh/cap plausibility + vwap anchor.
"""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import p1c_stock_ic_batch as P1C

idx, syms, meta = P1C.load_universe()


def load(name):
    return pd.DataFrame(
        np.asarray(np.load(os.path.join(P1C.CACHE_DIR, f"{name}.npy"),
                           mmap_mode="r"), dtype=np.float64),
        index=idx, columns=syms)


to = load("turnover_derived")
vol = load("volume")
close = load("close").ffill()
is688 = np.array([s.startswith("688") for s in syms])

# last trading bar of the cache
last = to.iloc[-1]
m688 = last[is688]
rest = last[~is688]
print("turnover_derived last-bar median: 688=%.6f  non688=%.6f"
      % (np.nanmedian(m688), np.nanmedian(rest)))
print("turnover_derived last-bar p95:    688=%.6f  non688=%.6f"
      % (np.nanpercentile(m688, 95), np.nanpercentile(rest, 95)))
print("turnover_derived last-bar p05:    688=%.6f  non688=%.6f"
      % (np.nanpercentile(m688, 5), np.nanpercentile(rest, 5)))

# osh under both hypotheses, 2025-2026 window (post-2019, 688 exists)
w = to.loc["2025-01-01":]
v = vol.loc["2025-01-01":]
oshA = (v / 100.0) / w          # hypothesis A
oshB = v / w                    # hypothesis B
medA = np.nanmedian(oshA.loc[:, is688].to_numpy())
medB = np.nanmedian(oshB.loc[:, is688].to_numpy())
medR = np.nanmedian(oshB.loc[:, ~is688].to_numpy())  # non-688 identical both hyp
print("2025+ median osh est (688): A(/100)=%.3e  B(no-correction)=%.3e"
      % (medA, medB))
print("2025+ median osh est (non688): %.3e" % medR)

# cap plausibility 2025+ (float cap, CNY)
c = close.loc["2025-01-01":]
capB = (c * oshB.ffill()).loc[:, is688]
capR = (c * oshB.ffill()).loc[:, ~is688]
capA = (c * oshA.ffill()).loc[:, is688]
print("2025+ median float cap (688): A=%.3e B=%.3e | non688=%.3e"
      % (np.nanmedian(capA.to_numpy()), np.nanmedian(capB.to_numpy()),
         np.nanmedian(capR.to_numpy())))

# vwap anchor: amount/volume vs close for 688 (doc: vwap col = price/100
# for 688) -> real notional per share check
amt = load("amount")
vwap_impl = (amt / vol).loc["2025-01-01":]
ratio = (vwap_impl.loc[:, is688] / c.loc[:, is688]).median().median()
print("2025+ median (amount/volume)/close for 688 = %.6f (expect ~0.01 if "
      "volume col = 100x real)" % ratio)
