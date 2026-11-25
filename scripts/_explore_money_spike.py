import sys
sys.path.insert(0, 'scripts')
import pandas as pd, numpy as np
import etf_book_cash_vehicle as CV

THR = -0.005
LOOK = 10
SHARE = 0.8
FLIP_WINDOW = 3
FLIP_TOL = 0.0005


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
        # recovery inside the r2046 window?
        back_idx = None
        for k in range(i + 1, min(i + 1 + FLIP_WINDOW, len(ser))):
            if abs(float(ser.iloc[k]) / prev - 1.0) <= FLIP_TOL:
                back_idx = k
                break
        if run_up >= abs(drop) * SHARE:
            shape = 'SPIKE'
        elif back_idx is not None:
            shape = 'V_DIP'
        else:
            shape = 'RESET'
        out.append({'date': str(pd.Timestamp(ser.index[i]).date()), 'i': i, 'drop': drop,
                    'run_up': run_up, 'shape': shape, 'low_idx': low_idx, 'back_idx': back_idx})
    return out


def tape(ser, mode):
    ser = ser.dropna().astype(float)
    ret = ser.pct_change().fillna(0.0).copy()
    js = classify(ser)
    for j in js:
        if mode == 'raw':
            break
        if mode == 'cv':
            ret.iloc[j['i']] = 0.0
        elif mode == 'honest':
            if j['shape'] == 'RESET':
                ret.iloc[j['i']] = 0.0
            elif j['shape'] == 'V_DIP':
                ret.iloc[j['i']] = 0.0
                if j['back_idx'] is not None:
                    ret.iloc[j['back_idx']] = 0.0
            else:  # SPIKE: zero the whole excursion from the trough to the recovery (or the drop)
                end = j['back_idx'] if j['back_idx'] is not None else j['i']
                for k in range(j['low_idx'] + 1, end + 1):
                    ret.iloc[k] = 0.0
    r = ret.dropna()
    lvl = float(np.cumprod(1 + r.to_numpy())[-1])
    return (lvl ** (252.0 / len(r)) - 1) * 100


for code in ['511880', '511360', '511660', '511950', '511930', '511770', '511670', '511970', '511920', '511960', '511910', '511620']:
    ser = CV.load_etf(code)
    ser = ser[ser.index >= pd.Timestamp('2020-07-16')]
    js = classify(ser)
    cnt = {k: sum(1 for j in js if j['shape'] == k) for k in ('SPIKE', 'V_DIP', 'RESET')}
    print('%-7s jumps=%3d %s  raw=%7.3f  cv=%7.3f  honest=%7.3f' % (
        code, len(js), str(cnt), tape(ser, 'raw'), tape(ser, 'cv'), tape(ser, 'honest')))
