import sys
sys.path.insert(0, 'scripts')
import pandas as pd, numpy as np
import etf_book_cash_vehicle as CV
sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('ex', 'scripts/_explore_money_spike.py')

THR, LOOK, SHARE, FW, FTOL = -0.005, 10, 0.8, 3, 0.0005


def classify(ser):
    ser = ser.dropna().astype(float)
    ret = ser.pct_change().fillna(0.0)
    out = []
    for i in range(1, len(ser)):
        r = float(ret.iloc[i])
        if not np.isfinite(r) or r >= THR:
            continue
        prev = float(ser.iloc[i - 1])
        j = max(0, i - LOOK)
        win = ser.iloc[j:i]
        low_idx = int(np.argmin(win.to_numpy())) + j
        base = float(ser.iloc[low_idx])
        run_up = prev / base - 1.0 if base > 0 else 0.0
        drop = float(ser.iloc[i]) / prev - 1.0
        back_idx = None
        for k in range(i + 1, min(i + 1 + FW, len(ser))):
            if abs(float(ser.iloc[k]) / prev - 1.0) <= FTOL:
                back_idx = k
                break
        if run_up >= abs(drop) * SHARE:
            shape = 'SPIKE'
        elif back_idx is not None:
            shape = 'V_DIP'
        else:
            shape = 'RESET'
        out.append({'date': str(pd.Timestamp(ser.index[i]).date()), 'i': i, 'drop': drop, 'run_up': run_up,
                    'shape': shape, 'low_idx': low_idx, 'back_idx': back_idx,
                    'prev': prev, 'now': float(ser.iloc[i]), 'base': base})
    return out

for code in ['511930', '511950']:
    ser = CV.load_etf(code)
    ser = ser[ser.index >= pd.Timestamp('2020-07-16')]
    print('=====', code, 'bars', len(ser), 'first', ser.iloc[0], 'last', ser.iloc[-1], 'min', ser.min(), 'max', ser.max())
    for j in classify(ser):
        print('  %s %-7s drop=%7.2f%% runup=%6.2f%% prev=%9.3f now=%9.3f base=%9.3f back=%s' % (
            j['date'], j['shape'], j['drop'] * 100, j['run_up'] * 100, j['prev'], j['now'], j['base'], j['back_idx']))
