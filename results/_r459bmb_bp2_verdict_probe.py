import json

w = json.load(open('results/etf_ops/bp2_windows.json', encoding='utf-8'))
for name, c in w['cells'].items():
    p = c['primary_x2']
    print(name, 'n_win=', p['n_windows'], 'median=', p['median_paired'],
          'ci=', p['ci95'], 'pass=', p['pass'])
g = json.load(open('results/etf_ops/bp2_grid.json', encoding='utf-8'))
print('pbo:', g['pbo']['pbo'])
for name, gg in list(g['gates'].items()):
    g1 = gg['g1_prime_v2']
    dsr = gg['dsr']
    print(name, 'g1_pass:', (g1 or {}).get('pass_v2'),
          'dsr:', round(dsr['dsr'], 4) if dsr else None,
          'x1_median:', gg['primary_gate_x1']['median_paired'])
print('d6:', {k: (v['max_abs_corr'], v['reject'])
              for k, v in g['d6']['cells'].items()})
print('beat_pure_dca:', {k: v['beat_pure_dca_x2']
                         for k, v in g['descriptive']['per_cell'].items()})
print('vt_6m_x2:', {k: v['virtual_timepoints']['6m_x2']['beat_rate']
                    for k, v in g['cells'].items()})
