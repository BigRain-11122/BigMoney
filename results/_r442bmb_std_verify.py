import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), 'scripts'))
import pandas as pd, numpy as np
import importlib.util
spec = importlib.util.spec_from_file_location('tl1', 'scripts/trial_labor_w1.py')
tl1 = importlib.util.module_from_spec(spec); spec.loader.exec_module(tl1)
face = tl8 = None
spec8 = importlib.util.spec_from_file_location('tl8', 'scripts/trial_labor_w8.py')
tl8 = importlib.util.module_from_spec(spec8); spec8.loader.exec_module(tl8)
face = tl8._tstate_face_full()
df = face['510300']
close = df['close'].astype(float).sort_index()
std20 = close.rolling(20, min_periods=1).std(ddof=1)/close
q90 = std20.rolling(252, min_periods=120).quantile(0.90)
dec = q90.notna() & std20.notna()
op = std20 > q90
print('n_bars', len(close), 'nan_std20', int(std20.isna().sum()))
fd = np.flatnonzero(dec.fillna(False).values)
print('first_decidable', int(fd[0]) if len(fd) else None, 'decidable', int(dec.sum()), 'open', int((op&dec).sum()), 'closed', int(((~op)&dec).sum()))
std10 = close.rolling(10, min_periods=1).std(ddof=1)/close
q9010 = std10.rolling(252, min_periods=120).quantile(0.90)
dec10 = q9010.notna() & std10.notna(); op10 = std10 > q9010
print('std10 decidable', int(dec10.sum()), 'open', int((op10&dec10).sum()))
# core48 spread, two calibers
prices_c = tl1.load_core()
cut = pd.Timestamp('2026-09-22')
r_full, r_dec = {}, {}
for sym, d2 in sorted(prices_c.items()):
    d2 = d2[d2.index <= cut]
    if len(d2) >= 260:
        c2 = d2['close'].astype(float).sort_index()
        s2 = c2.rolling(20, min_periods=1).std(ddof=1)/c2
        q2 = s2.rolling(252, min_periods=120).quantile(0.90)
        dcd = q2.notna() & s2.notna()
        opp = s2 > q2
        if dcd.any():
            r_full[str(sym)] = round(float((opp & dcd).mean()), 4)
            r_dec[str(sym)] = round(float((opp & dcd)[dcd].mean()), 4)
v = sorted(r_full.values()); v2 = sorted(r_dec.values())
print('full-caliber n', len(v), 'min', v[0], 'median', v[len(v)//2], 'max', v[-1])
print('dec-caliber  n', len(v2), 'min', v2[0], 'median', v2[len(v2)//2], 'max', v2[-1])
