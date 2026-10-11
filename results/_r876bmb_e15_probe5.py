import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import pandas as pd
from live.paper import load_core, build_panels
import mass_trial_w1 as mt

prices_full = load_core()
print("load_core members:", len(prices_full))
starts = {s: str(df.index[0].date()) for s, df in prices_full.items()}
from collections import Counter
print("member first-bar distribution:", Counter(starts.values()))
cut = pd.Timestamp("2026-09-22")
prices = {s: df[df.index <= cut] for s, df in prices_full.items()}
P = build_panels(prices)
close = P["close"]
print("build_panels close shape:", close.shape)
print("panel index first/last:", close.index[0], close.index[-1])

# leg-L index for comparison
raw, _P, idx, listed, cen = mt._leg_raw("L")
print("leg-L idx:", len(idx), idx[0], idx[-1])
wbase = None
for p, d in enumerate(close.index):
    if pd.Timestamp(d) >= idx[0]:
        wbase = p
        break
print("wbase in trial-labor panel:", wbase)
print("leg start in tl panel date:", close.index[wbase] if wbase is not None else None)
