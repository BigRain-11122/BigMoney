import json
import numpy as np

# regime counts from regime_series.json
rs = json.load(open('results/fusion_grid_p1/regime_series.json', encoding='utf-8'))
states = rs.get('states') or rs.get('series') or []
if isinstance(states, list) and states and isinstance(states[0], dict):
    vals = [s.get('state') for s in states]
else:
    vals = states
import collections
cnt = collections.Counter(vals)
print('REGIME COUNTS:', dict(cnt), 'total', len(vals))

# nulls summary
ns = json.load(open('results/fusion_grid_p1/nulls_summary.json', encoding='utf-8'))
print('NULLS:', json.dumps(ns, ensure_ascii=False)[:400])

# 45x45 pairwise corr of cell daily returns (report-face dedup disclosure)
d = json.load(open('results/fusion_grid_p1/p1_results.json', encoding='utf-8'))
names = list(d['cells'].keys())
rets = []
for n in names:
    c = json.load(open('results/fusion_grid_p1/cells/%s.json' % n, encoding='utf-8'))
    rets.append(np.asarray(c['returns'], dtype=float))
M = np.vstack(rets)
C = np.corrcoef(M)
iu = np.triu_indices(len(names), k=1)
pairs = np.abs(C[iu])
print('PAIRS n=', len(pairs), '| >=0.999:', int((pairs >= 0.999).sum()),
      '| >=0.99:', int((pairs >= 0.99).sum()), '| max:', round(float(pairs.max()), 6))
hi = [(names[i], names[j], round(float(C[i, j]), 6)) for i, j in zip(*iu) if abs(C[i, j]) >= 0.999]
print('>=0.999 examples (first 5):', hi[:5])

# descriptive lines across all cells: maxdd_line_pass / crash_year / oos_dual
fails = {'maxdd_line': 0, 'crash_year': 0, 'oos_dual_neg': 0}
for n in names:
    c = json.load(open('results/fusion_grid_p1/cells/%s.json' % n, encoding='utf-8'))
    st = c['stats']
    fails['maxdd_line'] += 0 if st.get('maxdd_line_pass') else 1
    fails['crash_year'] += 1 if st.get('crash_year') else 0
    fails['oos_dual_neg'] += 0 if st.get('oos_dual_positive') else 1
print('DESCRIPTIVE fails across 45:', fails)

# x2 face summary: worst/best degradation
degs = []
for n in names:
    c = json.load(open('results/fusion_grid_p1/cells/%s.json' % n, encoding='utf-8'))
    degs.append((n, c['x2']['sharpe_full'], c['x2']['sharpe_degradation']))
degs.sort(key=lambda t: t[2])
print('x2 best degradation:', degs[0], '| x2 worst:', degs[-1])
