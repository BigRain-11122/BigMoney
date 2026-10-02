import json

cur = json.load(open('results/perpetual_faces/n1_w106_results.json', encoding='utf-8'))
npc = cur['null_pool_cumulative']
w_mu = npc['w106_only']['mu']
w_sigma = npc['w106_only']['sigma']
a_p95 = cur['families']['A_random_engine_exit']['full_sharpe_p95']
klift = cur['skill_line_v2_k_lift']['line_delta_k_lift']
led = cur['science_gates']['ledger']

# W106 prereg S5 declared keys (W100 finalize measured anchors)
KEY_MU_MERGED = -0.092852425660794
KEY_SIGMA_MERGED = 0.24483423138995133
KEY_A_P95 = 0.3015

g1 = w_mu - KEY_MU_MERGED
g2 = (w_sigma - KEY_SIGMA_MERGED) / KEY_SIGMA_MERGED * 100
g3 = a_p95 - KEY_A_P95
gates = [
    (f'gate1 |dmu|={abs(g1):.6f} < 0.02', abs(g1) < 0.02),
    (f'gate2 sigma_rel={g2:+.4f}% |<10%|', abs(g2) < 10),
    (f'gate3 A_p95_diff={g3:+.4f} < 0.05', g3 < 0.05),
    (f'gate4 K-lift={klift:+.4f} >= -0.02', klift >= -0.02),
]
print('=== W106 S5 four gates (prereg-exact, W100 anchors) ===')
for t, ok in gates:
    print(('PASS ' if ok else 'FAIL ') + t)
allpass = all(ok for _, ok in gates)
print('ALL PASS:', allpass)
print(f'ledger prev={led["prev_total"]} batch={led["batch_trials"]} total={led["total"]} voids={led["voids_applied"]}')
print(f'K merged={npc["merged"]["n_values"]} mu={npc["merged"]["mu"]:.6f} sigma={npc["merged"]["sigma"]:.6f}')
print(f'se_mu={npc.get("se_mu_at_k231120")}')
print(f'audit.machine={cur["audit"]["machine"]} generated={cur["generated"]}')
