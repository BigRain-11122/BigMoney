import sys, json
sys.path.insert(0, 'scripts')
import pandas as pd, numpy as np
import etf_composite_pf as E
import etf_equity_alpha as A
import etf_book_cash_vehicle as CV

close, openp, amt, feats = E.build_panel()
close, openp, n35 = A.repair_flips(close, openp)
cmap = A.load_class_map()
cls = A.classify(close.columns, cmap, close)
money = [c for c in close.columns if cls.get(c) == 'money']
print('panel', close.shape, close.index[0].date(), close.index[-1].date(), 'flips35', n35)
print('money n', len(money))

rows = []
for c in money:
    px = close[c].dropna()
    if len(px) < 200:
        continue
    try:
        base = CV.load_etf(c)
        rets, resets = CV.consolidation_returns(base)
    except Exception:
        base = px
        rets, resets = px.pct_change(), []
    rets = rets.dropna()
    if len(rets) < 100:
        continue
    lvl = float(np.cumprod(1 + rets.to_numpy())[-1])
    tape_ann = (lvl ** (252.0 / len(rets)) - 1) * 100
    sig = float(rets.std()) * 1e4
    a = amt[c].dropna() if c in amt.columns else pd.Series(dtype=float)
    a20 = float(a.tail(20).mean()) if len(a) else None
    amed = float(a.median()) if len(a) else None
    nm = cmap.get(c, ('', ''))[1]
    rows.append((c, nm, len(rets), tape_ann, sig, a20, amed, float(base.iloc[-1]) if len(base) else None, len(resets)))

rows.sort(key=lambda r: -(r[3] if r[3] is not None else -9))
print('%-8s %-22s %5s %10s %7s %14s %14s %9s %4s' % ('code', 'name', 'bars', 'tape_ann%', 'sigma', 'amt20d', 'amt_med', 'last', 'rst'))
for r in rows:
    f = lambda v, n=1: ('%.*f' % (n, v)) if v is not None and np.isfinite(v) else '-'
    print('%-8s %-22s %5d %10s %7s %14s %14s %9s %4d' % (
        r[0], r[1], r[2], f(r[3], 3), f(r[4], 2), f(r[5], 0), f(r[6], 0), f(r[7], 3), r[8]))
