import json, math, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# W73-only mu derive (merged73 - pre73 weighted)
d73 = json.load(open('results/perpetual_faces/n1_w73_results.json', encoding='utf-8'))
npc73 = d73['null_pool_cumulative']
pre = npc73['pre_w73_cumulative']
mer = None
for k, v in npc73.items():
    if 'merg' in str(k).lower():
        mer = v
print('W73 merged key search:', list(npc73.keys()))
if mer:
    w73_mu = (mer['n_values'] * mer['mu'] - pre['n_values'] * pre['mu']) / 2200
    w73_sig2 = (mer['sigma'] ** 2 * mer['n_values'] - pre['sigma'] ** 2 * pre['n_values']) / 2200
    print('W73-only mu=%s sigma~%s' % (round(w73_mu, 6), round(math.sqrt(max(w73_sig2, 0)), 6)))
    se73 = mer['sigma'] / math.sqrt(mer['n_values'])
    print('W73 se_mu=%s @K=%s' % (round(se73, 6), mer['n_values']))
sl73 = d73.get('skill_line_v2_k_lift', {})
print('W73 K-lift:', sl73.get('line_delta_k_lift'), sl73.get('line_pre_w73'), '->', sl73.get('line_merged_158520'))

# W74-only mu
w74_mu = (2000 * -0.084152 + 200 * -0.121909) / 2200
print('W74-only mu=%s' % round(w74_mu, 6))
merged_mu = -0.09210586859133878
print('gate1 |drift| = %s (W74-only vs merged)' % round(abs(w74_mu - merged_mu), 6))
print('gate1 vs W72 anchor merged -0.092251: %s' % round(abs(merged_mu - (-0.092251)), 6))
# gate2 sigma relative
w74_sig = 0.2467
anchor_sig = 0.249564
print('gate2 sigma rel change = %s%%' % round((w74_sig - anchor_sig) / anchor_sig * 100, 2))
# gate3 A p95
print('gate3 A p95 delta vs 0.3372 = %s' % round(abs(0.3117 - 0.3372), 4))
# se_mu merged W74
se74 = 0.2447726710550595 / math.sqrt(160720)
print('W74 se_mu=%s @K=160720' % round(se74, 6))
# mu_delta w74 vs w73 ext
if mer:
    print('mu_delta_w74_vs_w73ext = %s' % round(w74_mu - w73_mu, 6))

# W74 freeze commit hash
r = subprocess.run(['git', 'log', '--oneline', '--grep=W74', 'origin/main'], capture_output=True, text=True, encoding='utf-8', errors='replace')
print('---W74 commits on origin---')
print(r.stdout[:800])
