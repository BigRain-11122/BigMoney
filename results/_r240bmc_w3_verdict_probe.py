import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
p = json.load(open('results/innovation_quota/HIGHERMOM-TIMING-P1.json', encoding='utf-8'))
print('=== cells (x1 judged face):')
for n, st in p['cells'].items():
    print(f"  {n}: sharpe={st['sharpe_full']} ann={st['ann_ret']} dd={st['max_dd']}")
print('passive:', p['passive']['passive_510300_bh']['full']['sharpe_full'])
print()
for n, g in p['gates'].items():
    sl = g['g1_prime_v2']['skill_line']
    print(f"{n}: line={sl['line']:.4f} (passive_term={sl.get('passive_term')}, null_term={sl.get('null_term')}, N_eff={sl['n_eff']}) line_ok={g['g1_prime_v2']['line_ok']} ci_pos={g['g1_prime_v2']['ci_lower_bound_positive']} trade_ok={g['g1_prime_v2'].get('trade_gate',{}).get('entries_ok')} G1={g['g1_prime_v2']['pass_v2']} dsr={g['dsr'].get('dsr')} G2={g['g2']['eligible_v2']} d6_reject={g['d6_reject']}")
print('family_pbo:', p['family_pbo'])
print()
print('virtual starts beat_rates:')
for n, w in p['virtual_starts']['cells'].items():
    print(f"  {n}: 6m={w['6m']['beat_rate']} 12m={w['12m']['beat_rate']} 24m={w['24m']['beat_rate']}")
print('splits:', {n: (p['splits'][n]['same_sign_rate'], p['splits'][n]['segment_stable']) for n in p['splits']})
print('d6 max_abs per cell:', {n: p['d6']['cells'][n]['max_abs_corr_member'] for n in p['d6']['cells']})
print('d6 cross:', p['d6']['same_batch_cross'])
print('episode_kpi:', {n: (p['episode_kpi'][n]['win_rate_vs_passive_same_days'], p['episode_kpi'][n]['mean_episode_edge']) for n in p['episode_kpi']})
print('ledger:', p['trials_ledger'])
print('extreme:', p['extreme_day_face']['worst_day'], '|', p['extreme_day_face']['best_day'])
print('stop days:', p['extreme_day_face']['stop_exit_days'])
