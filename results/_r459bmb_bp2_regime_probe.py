import json

g = json.load(open('results/etf_ops/bp2_grid.json', encoding='utf-8'))
rf = g['regime_face']['per_cell']
for name in ('510300-TP5-10', '510050-TP5-10', '588000-TP5-10'):
    v = rf[name]
    print('==', name)
    for st, d in v['by_route_state'].items():
        print('  route', st, 'n=', d['n'], 'median=', d['median_paired'])
    for sg, d in v['by_t89_segment'].items():
        print('  seg', sg, 'n=', d['n'], 'median=', d['median_paired'])
ba = g['blocked_accounting']
for mem, v in ba.items():
    print(mem, 'blocked_entries=', v['blocked_entries'],
          'open_at_end=', v['open_at_end'],
          'isolated=', v['isolated_days'],
          'crisis_days=', v['crisis_days_gt_threshold'],
          'guard_sig=', v['guard_isolated_signals'],
          'monthly=', v['monthly_signals'],
          'pure_dca_x2=', v['pure_dca']['x2'])
d1 = g['descriptive']['per_cell']['510300-TP5-10']
print('510300 yearly:', {k: round(v, 4) for k, v in d1['yearly_x2'].items()
                         if k in ('2015', '2024', '2025', '2018')})
print('beat_passive_full sample:', d1['beat_passive_full_x2'],
      d1['beat_margin_x2'])
