import json

d = json.load(open(r'results\regime_style_matrix\P0-SLICE-FUND-TRIO-20261011.json', encoding='utf-8'))
COLS = ['BULL', 'CHOP', 'GRIND', 'BEAR', 'SUPPORT', 'PANIC']
print('cell-level 12m medians (all-start rolling, net):')
hdr = '%-22s' % 'cell'
for col in COLS:
    hdr += ' %10s' % col
print(hdr)
for c in d['cells']:
    row = '%-22s' % c['cell']
    for col in COLS:
        s = c['by_regime'][col]
        r12 = s.get('roll12')
        if r12:
            row += ' %9.4f' % r12['median']
        else:
            row += ' %10s' % ('n=%d' % s['n_days'])
    print(row)
print()
print('cell-level floor-beat / not-negative / gate-off:')
for c in d['cells']:
    row = '%-22s' % c['cell']
    for col in COLS:
        tv = c['by_regime'][col].get('three_verdicts')
        if tv:
            row += ' %s' % ('FB' if tv['floor_beat_median'] else '--')
            row += '/%s' % ('NN' if tv['not_negative_median'] else 'NEG')
            row += '/%s' % ('OFF' if tv['gate_off_advice'] else 'ok')
        else:
            row += ' %8s' % 'short'
    print(' ', row)
print()
print('sharpe by regime:')
for c in d['cells']:
    row = '%-22s' % c['cell']
    for col in COLS:
        s = c['by_regime'][col]
        row += ' %8.2f' % s.get('sharpe', 0.0)
    print(' ', row)
print()
print('regime day counts (from first cell, calendar-level):')
c = d['cells'][0]
for col in COLS:
    print('  %-8s %d days' % (col, c['by_regime'][col]['n_days']))
print('  unlabeled (pre-2013-03-21 or no label):', c['unlabeled_days'])
