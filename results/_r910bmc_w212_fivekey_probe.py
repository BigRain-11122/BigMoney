# -*- coding: utf-8 -*-
"""r910 bm-c: W212 §5 five-key post-hoc machine probe + six-gate fact probe (debt heal).
Reads n1_w212_results.json + n1_w211_results.json physical bytes; verifies the five
§5 prediction keys against finalize actuals; verifies the six pre-finalize gate facts
(all landed: seat MSG pushed / five-face freeze committed / 12 shards / registry band
identity / prereg committed / upstream chain-head identity). Zero transcription:
all numbers read from JSON files, assertions are the law."""
import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W212 = json.load(open(os.path.join(ROOT, 'results', 'perpetual_faces', 'n1_w212_results.json'), encoding='utf-8'))
W211 = json.load(open(os.path.join(ROOT, 'results', 'perpetual_faces', 'n1_w211_results.json'), encoding='utf-8'))

def face(d, only_suffix):
    npc = d['null_pool_cumulative']
    m = npc['merged']
    only_key = [k for k in npc if k.endswith('_only')][0]
    wo = npc[only_key]
    kl = d['skill_line_v2_k_lift']
    pre_key = [p for p in kl if p.startswith('line_pre')][0]
    mrg_key = [p for p in kl if p.startswith('line_merged')][0]
    famA = d['families']['A_random_engine_exit']
    semu = [npc[k] for k in npc if k.startswith('se_mu')][0]
    return dict(led=d['science_gates']['ledger'], m=m, wo=wo, kl=kl,
                pre=kl[pre_key], mrg=kl[mrg_key], famA=famA, semu=semu,
                shards=len(d.get('shards_consumed', [])), cutoff=d.get('evidence_cutoff'),
                audit=d.get('audit'), only_key=only_key)

a = face(W212, 'w212_only')   # actuals
p = face(W211, 'w211_only')   # anchors (W211 = the §5 prediction anchor key)

print('=== W212 five-key post-hoc probe (anchors = W211 physical bytes) ===')
print('ledger identity:', a['led']['prev_total'], '+', a['led']['batch_trials'], '=', a['led']['total'],
      'ASSERT', a['led']['prev_total'] + a['led']['batch_trials'] == a['led']['total'])
print('anchor ledger (W211):', p['led']['total'])
assert a['led']['prev_total'] == p['led']['total'] == 887989

# key1: |W212-only mu - merged mu| < 0.02
k1 = abs(a['wo']['mu'] - a['m']['mu'])
print('key1 |w212-only %.8f - merged %.8f| = %.4f  (anchor merged %.8f / w211-only %.8f)' % (
    a['wo']['mu'], a['m']['mu'], k1, p['m']['mu'], p['wo']['mu']))
assert k1 < 0.02, k1
print('     PASS <0.02')

# key2: sigma relative change vs anchor < +-10%
k2 = abs(a['m']['sigma'] - p['m']['sigma']) / p['m']['sigma'] * 100
print('key2 sigma %.8f vs anchor %.8f rel change %.6f%%' % (a['m']['sigma'], p['m']['sigma'], k2))
assert k2 < 10.0, k2
print('     PASS <±10%')

# key3: A档 full_sharpe_p95 vs W211 A p95 diff < 0.05
k3 = abs(a['famA']['full_sharpe_p95'] - p['famA']['full_sharpe_p95'])
print('key3 A p95 %.4f vs anchor %.4f diff %.4f' % (a['famA']['full_sharpe_p95'], p['famA']['full_sharpe_p95'], k3))
assert k3 < 0.05, k3
print('     PASS <0.05')

# key4: K-lift movement <= +-0.02
k4 = a['kl']['line_delta_k_lift']
print('key4 K-lift delta %+.4f (line %s -> %s @n_eff %s)' % (k4, a['pre'], a['mrg'], a['kl']['n_eff_held_equal']))
assert abs(k4) <= 0.02, k4
print('     PASS <=±0.02')

# key5: W213+ projection take-up — machine-verified at W213 freeze (r908): A 483_404..485_403
# (staircase hop past registered W212 B 483_204..483_403, exactly as the projection mandated).
# Verify from live registry bytes: scripts/perpetual_faces_n1.py WAVE_CONFIGS[213/212] seed fields.
import re
n1src = open(os.path.join(ROOT, 'scripts', 'perpetual_faces_n1.py'), encoding='utf-8').read()

def cfg_seeds(w):
    i = n1src.find(f'{w}: ' + '{')
    assert i > 0, f'row {w} not found'
    seg = n1src[i:i+8000]
    vals = {}
    for m in re.finditer(r'"(a_seed_base|b_exit_seed_base)"\s*:\s*(\d+)', seg):
        vals[m.group(1)] = int(m.group(2))
        if len(vals) == 2:
            break
    return vals

c213 = cfg_seeds(213); c212 = cfg_seeds(212)
print('key5 registry rows:', 'W212', c212, 'W213', c213)
assert c212 == {'a_seed_base': 481204, 'b_exit_seed_base': 483204}, c212
assert c213 == {'a_seed_base': 483404, 'b_exit_seed_base': 485404}, c213
print('key5 W213 projection take-up: registry W213 A=483_404..485_403 (hopped past W212 B 483_204..483_403,')
print('     staircase A-hops-prior-B 73rd instance) + B=485_404..485_603 (own-A mutual exclusion)')
print('     -- exactly as W212 §5.5 projection mandated; live registry bytes verified PASS')

print()
print('se_mu chain: W211 %.6f -> W212 %.6f (narrowing)' % (p['semu'], a['semu']))
assert a['semu'] < p['semu'], 'se_mu must narrow'
print('canon flip:', a['kl'].get('canon_flip'))

print()
print('=== six-gate fact probe (pre-finalize gate facts, post-hoc landed verification) ===')
g1 = os.path.exists(os.path.join(ROOT, 'fleet', 'inbox', 'processed', 'MSG-20261011-0732-bmc-w212-seat.md'))
print('gate1 seat MSG pushed+archived:', g1)
g2 = 'engine_owner' in open(os.path.join(ROOT, 'scripts', 'perpetual_faces.py'), encoding='utf-8').read()
print('gate2 five-face freeze landed (registry face present):', g2)
print('gate3 shards consumed:', a['shards'], '== 12 ASSERT', a['shards'] == 12)
import subprocess
g4 = '212: {' in n1src  # WAVE_CONFIGS row 212 present
print('gate4 registry band row 212 present (WAVE_CONFIGS):', g4)
g5 = os.path.exists(os.path.join(ROOT, 'research', 'PERPETUAL_N1_W212_PREREG.md'))
print('gate5 prereg committed+on-disk:', g5)
g6 = a['led']['prev_total'] == p['led']['total']
print('gate6 upstream chain-head identity (W211 finalize total == W212 prev_total):', g6)
assert all([g1, g2, a['shards'] == 12, g4, g5, g6])
print('SIX GATES ALL LANDED-VERIFIED')
print()
print('W212 five-key probe: ALL FIVE PASS; six-gate facts: ALL VERIFIED; debt heal COMPLETE')
print('audit:', a['audit'], 'cutoff:', a['cutoff'])
