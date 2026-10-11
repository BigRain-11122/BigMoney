import json, csv

d = json.load(open(r'results\regime_style_matrix\P0-SLICE-FUND-TRIO-20261011.json', encoding='utf-8'))
c = d['cells'][0]
print('cell:', c['cell'], 'family:', c['family'], 't0:', c['t0'], 'n_days:', c['n_days'],
      'unlabeled:', c['unlabeled_days'], 'labeled:', c['labeled_days'], 'panic_in:', c['panic_days_in'])
for col in ['BULL', 'CHOP', 'GRIND', 'BEAR', 'SUPPORT', 'PANIC']:
    s = c['by_regime'][col]
    r12 = s.get('roll12', {})
    print('  %-8s n=%5d sharpe=%7s annret=%8s maxdd=%7s r12med=%s pos=%s floor_beat=%s' % (
        col, s.get('n_days', 0), s.get('sharpe', '-'), s.get('ann_ret', '-'),
        s.get('max_dd', '-'), r12.get('median', '-'), r12.get('pos_share', '-'),
        s.get('three_verdicts', {}).get('floor_beat_median', '-')))

print()
print('=== panic-day sanity (VALUE-PB x1, big crash days must be strongly negative) ===')
with open(r'results\regime_thermo\thermo_daily.csv', encoding='utf-8') as f:
    rows = list(csv.reader(f)); dates = [r[0] for r in rows[1:]]
cd = json.load(open(r'results\fund_value_p1\cont_VALUE-PB_x1.json', encoding='utf-8'))
rets = cd['returns']; nd = cd['n_days']; off = len(dates) - nd
for target in ['2015-08-24', '2016-01-04', '2020-02-03', '2024-02-05', '2025-04-07']:
    if target in dates:
        di = dates.index(target)
        i = di - off - 1
        if 0 <= i < len(rets):
            print('  %s: ret=%.6f' % (target, rets[i]))
        else:
            print('  %s: out of range' % target)

print()
print('=== family rollup (median of 12m medians) ===')
fr = d['family_rollup']
for fam, cols in fr.items():
    print(' ', fam)
    for col in ['BULL', 'CHOP', 'GRIND', 'BEAR', 'SUPPORT', 'PANIC']:
        v = cols[col]
        print('    %-8s n_cells=%d med_of_med=%s' % (col, v['n_cells_with_12m'], v['median_of_medians']))
