import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

d = json.load(open('results/perpetual_faces/n1_w22_results.json', encoding='utf-8'))
c = d['null_pool_cumulative']
kl = d['skill_line_v2_k_lift']

mu_m = c['merged']['mu']; sig_m = c['merged']['sigma']
a95 = d['families']['A_random_engine_exit']['full_sharpe_p95']
print('K merged:', c['merged']['n_values'])
print('merged mu:', mu_m, 'sigma:', sig_m)
print('A p95:', a95, 'p99:', d['families']['A_random_engine_exit']['full_sharpe_p99'])
print('w22_only mu:', c['w22_only']['mu'])
print('se_mu:', {k: v for k, v in c.items() if 'se_mu' in k})
print('mu_delta:', {k: v for k, v in c.items() if 'delta' in k})
print('K-lift:', {k: v for k, v in kl.items()})
print('ledger prev->total:', d['science_gates']['ledger']['prev_total'], '->',
      d['science_gates']['ledger']['total'])
print('evidence_cutoff:', d['evidence_cutoff'])
print('audit:', d.get('audit'))
print('shards_consumed:', len(d.get('shards_consumed', [])))
print('ledger file guard (family summary persistence, r509):',
      'perpetual_faces/n1_w22_results.json' == d['science_gates']['ledger']['file'])

# S5 four predictions vs W20 anchors (prereg frozen)
checks = []
checks.append(('1 mu-drift |%.5f|<0.02' % abs(mu_m - (-0.09210)),
               abs(mu_m - (-0.09210)) < 0.02))
rel = (sig_m - 0.24443) / 0.24443 * 100
checks.append(('2 sigma-rel %+.3f%% <±10' % rel, abs(rel) < 10))
dp95 = a95 - 0.3224
checks.append(('3 A-p95 delta %+.4f <0.05' % dp95, abs(dp95) < 0.05))
dkl = kl['line_delta_k_lift']
checks.append(('4 K-lift |%+.4f| <=0.02' % dkl, abs(dkl) <= 0.02))
for name, ok in checks:
    print(('PASS ' if ok else 'FAIL ') + name)
assert all(ok for _, ok in checks), 'S5 prediction FAILED'
print('S5: 4/4 PASS')
