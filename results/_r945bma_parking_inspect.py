import json

d = json.load(open('results/parking_p1.json', encoding='utf-8'))
print('null pool:', json.dumps(d['null_pool']['coverage'], ensure_ascii=False))
print('passive_511880:', d['passive_override_511880'])
print()
for k, v in d['verdicts'].items():
    print("%-12s n=%4d mean=%+.6f t=%s annSR=%s face1=%s p95=%s p95pass=%s tail=%s cell=%s"
          % (k, v['n_stints'], v['mean_pickup_c2'], v['t'], v['ann_stint_sharpe'],
             v['face1_pass'], v['face3']['p95_maxdd'], v['face3']['p95_pass'],
             v['face3']['tail_pass'], v['cell_pass']))
print()
for code, f2 in d['face2_registration'].items():
    if f2.get('triggered'):
        g1 = f2['g1_prime_v2']
        g2 = f2['g2_registration_v2']
        dsr = f2['dsr']['dsr'] if isinstance(f2['dsr'], dict) else f2['dsr']
        print("%s: best=%s sf=%s line=%s line_ok=%s ci_ok=%s g1=%s dsr=%s pbo_missing=%s g2=%s missing=%s"
              % (code, f2['best_cell'], f2['sharpe_full'], g1['skill_line']['line'],
                 g1['line_ok'], g1['ci_lower_bound_positive'], g1['pass_v2'],
                 dsr, f2['pbo_missing'], g2['eligible_v2'], g2['missing_inputs']))
    else:
        print("%s: not triggered" % code)
print()
print('d6:', {c: (v['max_abs_corr'], v['argmax_member']) for c, v in d['d6']['cells'].items()})
print('d6 cross sample:', list(d['d6']['same_batch_cross'].items())[:2])
print()
print('stress C0 x2 gate (face1_c0_x2_net_mean_pos):')
for k, v in d['verdicts'].items():
    print(' ', k, v['face1_c0_x2_net_mean_pos'], 'x2mean=', v['stress_x2_mean'])
