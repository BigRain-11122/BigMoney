# -*- coding: utf-8 -*-
# r336 bm-c: S5 anchor verification -- W23 finalize product on origin (A p95 / mu / sigma)
import io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
w23 = json.loads(subprocess.check_output(
    ['git', '-C', R, 'show', 'origin/main:results/perpetual_faces/n1_w23_results.json']).decode('utf-8'))
m = w23['null_pool_cumulative']['merged']
p95 = w23['families']['A_random_engine_exit']['full_sharpe_p95']
print('W23 merged mu =', m['mu'], '(backfill anchor -0.09309)')
print('W23 sigma     =', m['sigma'], '(backfill anchor 0.24449)')
print('W23 A p95     =', p95, '(backfill anchor 0.3054)')
ok = abs(m['mu'] - (-0.09309)) < 5e-6 and abs(m['sigma'] - 0.24449) < 5e-6 and abs(p95 - 0.3054) < 5e-5
print('ANCHOR-MATCH:', 'PASS' if ok else 'FAIL')
