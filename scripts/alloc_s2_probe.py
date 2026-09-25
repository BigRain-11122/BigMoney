# -*- coding: utf-8 -*-
"""ALLOC_LINE_S2 跑前探针（prereg §1/§2 冻结面）· T-2026-09-25-59 s2 · bm-b
口径：静态权重买入持有日收益（零成本零再平衡）——探针事实非回测判据面；
P2 权重=全窗逆波动率近似（回测按冻结规则用滚动 126d 窗，探针仅取形态）；
现金腿=repo_daily.csv 逐日计息（CASH_LEG 承制件只读复用，rate/100/252，缺日 ffill）；
evidence_cutoff=2026-09-22（D2 前向锁盒——探针窗同步截断）。
产物：results/allocation/ALLOC_S2_PROBE.json
"""
import json
import os
import sys

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

CUTOFF = '2026-09-22'
START = '2020-01-02'
DATA = r'data\daily'
REPO = r'Money0923\data\repo_daily.csv'  # CASH_LEG 冻结的只读消费路径
OUT = r'results\allocation\ALLOC_S2_PROBE.json'

RISK = ['510300', '511010', '518880', '513100', '513500']

WEIGHTS = {
    'ALLOC-P1': {'510300': 0.30, '511010': 0.40, '518880': 0.15, 'CASH': 0.15},
    'ALLOC-P2': None,  # inverse-vol proxy, computed below
    'ALLOC-P3': {'510300': 0.60, '511010': 0.40},
    'ALLOC-P3B': {'510300': 0.60, '511010': 0.40},
    'ALLOC-P4': {'511010': 0.80, '510300': 0.20},
    'ALLOC-P6': {'CASH': 0.10, '511010': 0.40, '510300': 0.20, '513100': 0.15, '513500': 0.15},
}
BENCH = {
    'BENCH-STOCK100': {'510300': 1.0},
    'BENCH-BOND100': {'511010': 1.0},
    'BENCH-6040-NOREBAL': {'510300': 0.60, '511010': 0.40},
}

px = {}
for sym in RISK:
    df = pd.read_csv(os.path.join(DATA, f'{sym}.csv'))
    df['date'] = df['date'].astype(str)
    s = df.set_index('date')['close'].loc[:CUTOFF]
    s = s[s.index >= START]
    px[sym] = s
    print(f'{sym}: rows={len(s)} first={s.index[0]} last={s.index[-1]} nulls={int(s.isna().sum())}')

panel = pd.DataFrame(px).sort_index()
# union-calendar alignment: missing asset-day filled with prior close (price-hold, r=0 that day)
ret = panel.ffill().pct_change().fillna(0.0)
miss = {sym: int(panel[sym].isna().sum()) for sym in RISK}

repo = pd.read_csv(REPO)
repo['date'] = repo['date'].astype(str)
rs = repo.set_index('date')['rate'].astype(float).loc[:CUTOFF]
rs = rs[rs.index >= START].ffill()
cash_ret = rs / 100.0 / 252.0
print(f'repo series: rows={len(rs)} last={rs.index[-1]} rate_last={rs.iloc[-1]}')

# align cash to panel index (ffill known rate, zero on pre-first days)
cash_on_panel = cash_ret.reindex(ret.index).ffill().fillna(0.0)

# P2 inverse-vol proxy weights (full-window annualized vol, cap 50% iterative)
vol = (ret.std() * (252 ** 0.5))[['510300', '511010', '518880']]
inv = 1.0 / vol
w = inv / inv.sum()
for _ in range(5):
    over = w[w > 0.50]
    if over.empty:
        break
    w[over.index] = 0.50
    rest = inv[[s for s in inv.index if w[s] < 0.50]]
    w[[s for s in inv.index if w[s] < 0.50]] = rest / rest.sum() * (1.0 - 0.50 * len(over))
w = w / w.sum()
WEIGHTS['ALLOC-P2'] = {k: round(v, 4) for k, v in w.items()}
print('P2 inverse-vol proxy weights:', WEIGHTS['ALLOC-P2'])

series = {}
for name, wt in WEIGHTS.items():
    r = pd.Series(0.0, index=ret.index)
    for sym, ww in wt.items():
        if sym == 'CASH':
            r = r + ww * cash_on_panel
        else:
            r = r + ww * ret[sym]
    series[name] = r
for name, wt in BENCH.items():
    r = pd.Series(0.0, index=ret.index)
    for sym, ww in wt.items():
        r = r + ww * ret[sym]
    series[name] = r

df = pd.DataFrame(series)
corr = df.corr()

rows = []
names = list(WEIGHTS.keys()) + list(BENCH.keys())
for i, a in enumerate(names):
    for b in names[i + 1:]:
        rows.append({'pair': f'{a}|{b}', 'corr': round(float(corr.loc[a, b]), 4)})

# D6 check: max |corr| among the batch itself (P3B vs P3 expected high = declared A/B design pair)
batch_names = list(WEIGHTS.keys())
batch_corr = corr.loc[batch_names, batch_names].abs()
import numpy as np
arr = batch_corr.to_numpy()
mask = ~np.eye(len(batch_names), dtype=bool)
batch_max = float(arr[mask].max())
batch_max_pair = None
for a in batch_names:
    for b in batch_names:
        if a != b and abs(batch_corr.loc[a, b] - batch_max) < 1e-9:
            batch_max_pair = f'{a}|{b}'

# descriptive probe stats (static buy-hold, zero cost -- NOT the judgment face)
stats = {}
for name in names:
    r = df[name]
    eq = (1 + r).cumprod()
    yrs = len(r) / 252
    ann = float(eq.iloc[-1] ** (1 / yrs) - 1)
    dd = float((eq / eq.cummax() - 1).min())
    vola = float(r.std() * (252 ** 0.5))
    stats[name] = {'ann_ret_probe': round(ann, 4), 'maxdd_probe': round(dd, 4),
                   'vol_probe': round(vola, 4), 'months_pos_probe': None}

os.makedirs(r'results\allocation', exist_ok=True)
out = {
    'meta': {
        'batch': 'ALLOC_LINE_S2 probe (prereg s1/s2 frozen-face facts)',
        'ticket': 'T-2026-09-25-59 s2',
        'window': f'{START}..{CUTOFF}',
        'evidence_cutoff': CUTOFF,
        'p2_note': 'inverse-vol proxy = full-window vol, cap50% iterative; backtest uses frozen rolling-126d rule',
        'cost_note': 'probe = static buy-hold zero-cost descriptive; judgment face = s3 rebalanced net-of-cost four-metrics',
        'cash_note': 'CASH leg = repo_daily.csv rate/100/252 daily accrual (CASH_LEG carrier reuse, read-only)',
        'p5_note': 'ALLOC-P5 dividend face EXCLUDED here (510880 not yet pulled) -- pull leg = off-hours fund_etf_hist_em',
        'probe_ts': '2026-09-25 12:1x (bm-b r176)',
    },
    'weights': WEIGHTS,
    'bench': BENCH,
    'data_completeness': {'rows': int(len(ret)), 'missing_asset_days': miss,
                          'completeness_gate': '>=95% non-null per asset (s2 panel audit)'},
    'corr_pairs': rows,
    'd6_batch_max_abs_corr': {'value': round(batch_max, 4), 'pair': batch_max_pair,
                              'verdict_note': 'P3B is the declared rebalance-method A/B twin of P3 (expected ~1.0, declared design-pair not duplication); vs-trader-sleeve corr = s3 pre-run leg (t35 series >=20 trading days)'},
    'probe_stats_static_buyhold': stats,
}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('--- corr matrix ---')
print(corr.round(3).to_string())
print(f'D6 batch max|corr|={batch_max:.3f} pair={batch_max_pair}')
print(f'WROTE {OUT}')
