# -*- coding: utf-8 -*-
# r336 bm-c: W26 finalize chain cross-check (r322 dangling-claim law) --
# verify W25-on-origin K/mu vs W26 product pre_w26_cumulative, and S5 gate block.
import io, sys, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
w25_raw = subprocess.check_output(['git', '-C', R, 'show', 'origin/main:results/perpetual_faces/n1_w25_results.json'])
w25 = json.loads(w25_raw.decode('utf-8'))
w26 = json.load(open(R + r'\results\perpetual_faces\n1_w26_results.json', encoding='utf-8'))

w25_ledger = w25['science_gates']['ledger']['total']
w25_mu = w25['null_pool_cumulative']['merged']['mu']
w25_sigma = w25['null_pool_cumulative']['merged']['sigma']
pre = w26['null_pool_cumulative']['pre_w26_cumulative']

print('W25-on-origin ledger total =', w25_ledger, '(expect 419548)')
print('W25-on-origin merged mu    =', w25_mu)
print('W26 pre_w26 mu             =', pre['mu'])
print('W25 sigma                  =', w25_sigma)
print('W26 pre_w26 sigma          =', pre['sigma'])
ok_head = w25_ledger == 419548 and abs(w25_mu - pre['mu']) < 1e-12 and abs(w25_sigma - pre['sigma']) < 1e-12
print('CHAIN PREV-MATCH:', 'PASS' if ok_head else 'FAIL')

sg = w26['science_gates']
s5 = sg.get('s5_final') or sg.get('s5') or {k: v for k, v in sg.items() if 's5' in str(k).lower()}
print('S5 block:', json.dumps(s5, ensure_ascii=False)[:600])
kl = w26.get('skill_line_v2_k_lift', {})
print('K-lift block:', json.dumps(kl, ensure_ascii=False)[:300])
shards = w26.get('shards_consumed')
print('shards_consumed:', shards if not isinstance(shards, list) else (len(shards), shards[:3]))
npool = w26.get('null_pool_cumulative', {})
print('se_mu_at_k55120 =', npool.get('se_mu_at_k55120'))
print('k_value_probe keys:', [k for k in npool if 'k' in k.lower()][:8])
