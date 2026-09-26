# -*- coding: utf-8 -*-
"""CN_TREND_ETF_P1 batch pre-freeze probe (R99 law: prereg §2 facts must be
real probe values). Saves compact JSON to results/cn_trend_probe.json.

Universe filter under test (to be frozen in prereg):
  rows >= 2600 AND first <= 2016-06-30 AND last == 2026-09-22 (cutoff)
  AND OHLCV zero-NaN AND median amount20 >= 50_000_000 CNY
"""
import pandas as pd, glob, json, os

rows_total = 0
cands = []
for f in sorted(glob.glob('data/daily/*.csv')):
    rows_total += 1
    sym = os.path.basename(f)[:-4]
    d = pd.read_csv(f)
    cols = {c.lower(): c for c in d.columns}
    dtcol = cols.get('date', d.columns[0])
    first = str(d[dtcol].iloc[0])[:10]; last = str(d[dtcol].iloc[-1])[:10]
    if len(d) < 2600 or first > '2016-06-30' or last != '2026-09-22':
        continue
    if int(d.isna().sum().sum()) != 0:
        continue
    close = d[cols['close']]; vol = d[cols['volume']]
    amt20 = (vol * close).rolling(20).median().dropna()
    med20 = float(amt20.median()) if len(amt20) else 0.0
    if med20 < 50_000_000:
        continue
    ret = close.pct_change().dropna()
    ann_std = float(ret.std() * (252 ** 0.5))
    if ann_std < 0.03:  # cash-like/monetary face: trend signal structurally undefined
        continue
    cands.append({'sym': sym, 'rows': int(len(d)), 'first': first,
                  'med_amount20_cny': round(med20, 0),
                  'ann_std': round(ann_std, 4)})
probe = {
    'probe': 'cn_trend_ETF_universe',
    'ts': '2026-09-27T00:2x+08:00 (bm-a R280 pre-freeze)',
    'source': 'data/daily/*.csv (ETF board, OHLCV close-px face)',
    'total_files': rows_total,
    'filter': 'rows>=2600 & first<=2016-06-30 & last==2026-09-22 & zero-NaN & med_amount20>=50e6 & ann_std>=0.03',
    'universe_n': len(cands),
    'universe': cands,
}
with open('results/cn_trend_probe.json', 'w', encoding='utf-8') as fh:
    json.dump(probe, fh, ensure_ascii=False, indent=1)
print('universe_n', len(cands), 'of', rows_total)
print('median rows', sorted(c['rows'] for c in cands)[len(cands)//2] if cands else '-')
print('min med_amount20', min((c['med_amount20_cny'] for c in cands), default='-'))
for c in cands[:40]: print(c['sym'], c['rows'], c['first'], round(c['med_amount20_cny']/1e6,1),'M')
