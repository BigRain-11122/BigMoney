import sys
sys.path.insert(0, 'scripts')
import pandas as pd, numpy as np
import etf_book_cash_vehicle as CV

def ann(rets):
    rets = rets.dropna()
    if len(rets) < 50:
        return None
    lvl = float(np.cumprod(1 + rets.to_numpy())[-1])
    return (lvl ** (252.0 / len(rets)) - 1) * 100, len(rets), lvl

for code in ['511950', '511930', '511770', '511670', '511970', '511920', '511960', '511910', '511620', '511880', '511360', '511600', '511800', '511660', '159001', '511990', '511810']:
    base = CV.load_etf(code)
    base = base.dropna()
    raw = base.pct_change()
    fix, resets = CV.consolidation_returns(base)
    a1 = ann(raw); a2 = ann(fix)
    print('%-7s bars=%4d first=%9.3f last=%9.3f min=%9.3f max=%9.3f rst=%2d  raw_ann=%8s fix_ann=%8s' % (
        code, len(base), base.iloc[0], base.iloc[-1], base.min(), base.max(), len(resets),
        ('%.2f' % a1[0]) if a1 else '-', ('%.2f' % a2[0]) if a2 else '-'))
    # biggest raw daily moves
    r = raw.dropna()
    big = r.abs().sort_values(ascending=False).head(3)
    print('     biggest raw moves:', ', '.join('%s %+.2f%%' % (d.date(), v * 100) for d, v in big.items()))
