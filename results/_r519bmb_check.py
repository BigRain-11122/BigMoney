import subprocess, json, re

def show(p):
    return subprocess.run(['git', 'show', 'origin/main:' + p],
                          capture_output=True).stdout.decode('utf-8', errors='replace')

src = show('scripts/perpetual_faces.py')
print('86_001 in origin perpetual_faces:', '86_001' in src)
m = re.search(r'22: \{"a"', src)
print('N1_BANDS[22] row present on origin:', bool(m))

d = json.loads(show('results/perpetual_faces/n1_w20_results.json'))
merged = d['null_pool_cumulative']['merged']
k = merged['n_values']
print('W20 K:', k)
print('W20 merged mu:', merged['mu'])
print('W20 merged sigma:', merged['sigma'])
print('W20 A p95:', d['families']['A_random_engine_exit']['full_sharpe_p95'])
print('W20 A p99:', d['families']['A_random_engine_exit']['full_sharpe_p99'])
print('W20 ledger total:', d['science_gates']['ledger']['total'])
kl = d['skill_line_v2_k_lift']
print('W20 K-lift keys:', {kk: vv for kk, vv in kl.items()})
print('W20 se_mu key:', d['null_pool_cumulative'].get('se_mu_at_k%d' % k))
print('W20 w20_only mu:', d['null_pool_cumulative'].get('w20_only', {}).get('mu'))
print('W20 mu_delta:', [vv for kk2, vv in d['null_pool_cumulative'].items() if 'delta' in kk2])
