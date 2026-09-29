# r441 bm-a: extract FV backfill numbers for prereg sec.7/8
import json

d = json.load(open('results/t101_v4_a158_fv.json', encoding='utf-8'))
print('ledger:', d['trials_ledger'])
print('dsr_n_trials:', d['dsr_n_trials'])
print('E[FP]:', d['e_fp_nominal_5pct'])
print('null_pool coverage:', {k: round(v, 4) if isinstance(v, float) else v
                              for k, v in d['null_pool_batch_own']['coverage'].items()})
print('collapsed_out:', d['collapsed_out'])
print()
for m, g in d['pbo_face']['grids'].items():
    print('PBO %s: pbo=%.4f n_trials=%d n_rows=%d verdict=%s' % (
        m, g['pbo'], g['n_trials'], g['n_rows'], g['verdict']))
print()
for cell, c in d['cells'].items():
    g1 = c['g1_prime_v2']
    print('%s:' % cell)
    print('  line=%.4f (passive_term=%.4f null_term=%.4f mu_null=%.4f sigma_null=%.4f n_eff=%d) line_ok=%s ci_low_pos=%s trade_gate=%s'
          % (g1['skill_line']['line'], g1['skill_line']['passive_term'],
             g1['skill_line']['null_term'], g1['skill_line']['mu_null'],
             g1['skill_line']['sigma_null'], g1['skill_line']['n_eff'],
             g1['line_ok'], g1['bootstrap_ci']['ci_lower_bound_positive'] if 'ci_lower_bound_positive' in g1['bootstrap_ci'] else g1['ci_lower_bound_positive'],
             g1.get('trade_gate', {})))
    print('  dsr=%.6f sr_star=%.6f T=%d | d6_recheck=%s %.4f | beat6m=%.3f beat12m=%.3f beat24m=%.3f n_eff=%d suff=%s'
          % (c['dsr']['dsr'], c['dsr']['sr_star'], c['dsr']['T'],
             c['d6_recheck']['verdict'], c['d6_recheck']['max_abs'],
             c['window_grid']['beat']['6m']['rate'],
             c['window_grid']['beat']['12m']['rate'],
             c['window_grid']['beat']['24m']['rate'],
             c['window_grid']['n_eff_start_windows'],
             c['window_grid']['sample_sufficient']))
    print('  segs:', {k: round(v['oos_ann_ret'], 4) for k, v in c['segments_oos'].items()})
