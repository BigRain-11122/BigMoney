import json

d = json.load(open('results/g2_slot_mon_p2/g2_slot_mon_p2_verdict.json', encoding='utf-8'))
print('== ledger:', d['trials_ledger'])
for f in ('old_032', 'best_016'):
    g = d['gates'][f]
    v = d['face_verdicts'][f]
    r = d['faces'][f]
    print('=====', f, '->', v['verdict'], 'failed:', v.get('failed_lines'))
    print(' ic:', r['ic']['ic5_mean'], 'x1 sharpe:', r['x1']['sharpe'], 'ann:', r['x1']['ann'],
          'x2 sharpe:', r['x2']['sharpe'], 'ann:', r['x2']['ann'], 'x2 beat:', r['x2']['beat_rate'])
    print(' trades: n_buys=%s n_exits=%s n_rebal=%s' % (r['x1']['n_buys_total'], r['x1']['n_exits_total'], r['x1']['n_rebal']))
    g1 = g['g1_prime_v2']
    print(' g1: sharpe=%s line=%s line_ok=%s ci_low_pos=%s pass=%s n_eff=%s passive_ovr=%s' % (
        g1['sharpe_full'], g1['skill_line']['line'], g1['line_ok'],
        g1['ci_lower_bound_positive'], g1['pass_v2'], g1['skill_line']['n_eff'],
        g['passive_override_ew48_sharpe']))
    print('  trade_gate:', g1.get('trade_gate'))
    print(' m1:', g['m1'])
    print(' dsr:', g['dsr'])
    print(' pbo:', g['family_pbo']['pbo'], 'x2_survival:', g['x2_survival'])
    print(' g2:', g['g2_registration_v2'])
    print(' exit:', {k: d['exit_census'][f][k] for k in ('n_exits_total', 'n_exits_other', 'other_share', 'blocked')})
    print(' regime:', r['regime_segments_x2'])
    print(' extreme:', r['extreme_days_x2'])
print('== nulls p95:', d['nulls']['p95_abs_mean_ic'], 'br_x2_mean:', d['nulls']['beat_rate_x2_mean'])
print(' null_pool coverage:', d['nulls']['null_pool_sharpe_x1']['coverage'])
print('== d6 max:', d['d6']['max_abs_corr_by_face'], 'inter:', d['d6']['inter_face_pairs'])
print('== fam cross:', {fam: {k: d['family_matrices'][fam]['parent_crosscheck'][k] for k in ('n_faces_checked', 'n_drift')} for fam in ('old','tail')})
print('== fam pbo old:', d['family_matrices']['old']['pbo_cscv']['pbo'], d['family_matrices']['old']['pbo_cscv']['verdict'],
      'tail:', d['family_matrices']['tail']['pbo_cscv']['pbo'], d['family_matrices']['tail']['pbo_cscv']['verdict'])
print('== preds vs actual:', json.dumps(d['predictions_vs_actual'], ensure_ascii=False, indent=1)[:1500])
