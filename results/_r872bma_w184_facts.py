# -*- coding: utf-8 -*-
import subprocess, json, hashlib

def gs(*a):
    r = subprocess.run(list(a), capture_output=True)
    assert r.returncode == 0, (a, r.stderr[:200])
    return r.stdout

# 1. W183 prereg freeze-time blob sha (prereg-freeze commit + registry-freeze commit equality)
blob_sha = gs('git','rev-parse','678da52e2:research/PERPETUAL_N1_W183_PREREG.md').decode().strip()
blob_sha2 = gs('git','rev-parse','481da4d78:research/PERPETUAL_N1_W183_PREREG.md').decode().strip()
blob = gs('git','show','678da52e2:research/PERPETUAL_N1_W183_PREREG.md')
print('W183 prereg blob sha:', blob_sha)
print('registry-freeze blob :', blob_sha2, 'EQUAL' if blob_sha==blob_sha2 else 'DIFFER')
print('blob bytes:', len(blob), 'CRLF' if b'\r\n' in blob else 'LF')

# 2. W184 seat MSG push sha (first commit adding the seat MSG path)
r = subprocess.run(['git','log','--all','--oneline','--follow','--diff-filter=A','--',
                    'fleet/inbox/MSG-2026-10-08-0826-bma-w184-seat.md'], capture_output=True, text=True)
print('seat MSG add commit:', r.stdout.strip()[:100])

# 3. W183 FREEZE push sha (registry freeze)
r = subprocess.run(['git','log','origin/main','--oneline','--grep','W183 FREEZE'], capture_output=True, text=True)
print('W183 FREEZE commits:', r.stdout.strip()[:200])

# 4. W183 results actuals
res = json.load(open('results/perpetual_faces/n1_w183_results.json', encoding='utf-8'))
npc = res['null_pool_cumulative']
kl = res['skill_line_v2_k_lift']
fam = res['families']
print('merged K:', npc['merged']['n_values'])
print('pre_w183 K:', npc['pre_w183_cumulative']['n_values'])
print('w183_only:', npc['w183_only']['n_values'], 'mu', npc['w183_only']['mu'])
print('merged mu:', npc['merged']['mu'])
print('merged sigma:', npc['merged']['sigma'])
print('se_mu_at_k400520:', npc['se_mu_at_k400520'])
print('mu_delta:', npc['mu_delta_w183_vs_w182ext'])
print('kl keys:', {k: kl[k] for k in kl})
print('A p95:', fam['A_random_engine_exit']['full_sharpe_p95'])
print('A family keys sample:', [k for k in fam.keys()][:5])
print('ledger keys:', res.get('ledger', 'NONE'))
print('top keys:', list(res.keys()))
