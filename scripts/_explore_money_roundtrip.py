import sys
sys.path.insert(0, 'scripts')
import pandas as pd, numpy as np
import etf_book_cash_vehicle as CV

def jumps(ser, thr=-0.005, look=3, tol=0.0005):
    ser = ser.dropna().astype(float)
    ret = ser.pct_change().fillna(0.0)
    out = []
    for i, (d, r) in enumerate(ret.items()):
        if r < thr:
            prev = ser.shift(1).loc[d]
            after = ser.iloc[i:i + 1 + look]
            back = after[(after >= prev * (1 - tol)) & (after <= prev * (1 + tol))]
            # also check whether price before the jump was itself a spike (came from far below)
            out.append((str(d.date()), round(r * 100, 3), round(float(prev), 3),
                        round(float(ser.loc[d]), 3), bool(len(back)), len(back)))
    return out

for code in ['511880', '511950', '511930', '511770', '511360', '511660', '511800']:
    ser = CV.load_etf(code)
    js = jumps(ser)
    n = len(js)
    back = sum(1 for j in js if j[4])
    print('%-7s jumps=%3d  returns_within_3bars=%3d  stays_down=%3d' % (code, n, back, n - back))
    for j in js[:6]:
        print('     ', j)
