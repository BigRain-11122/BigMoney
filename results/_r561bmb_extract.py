import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for w in [53, 54, 55, 56]:
    t = open(f'research/PERPETUAL_N1_W{w}_PREREG.md', encoding='utf-8').read()
    m5 = re.search(r'## .?5', t); m6 = re.search(r'## .?6', t); m7 = re.search(r'## .?7', t); m8 = re.search(r'## .?8', t)
    s5 = t[m5.start():m6.start()]
    # anchor wave references in S5
    refs = sorted(set(re.findall(r'W(\d+)\s*(?:实测|finalize 实测|锚)', s5)))
    print(f'=== W{w} S5 anchor wave refs: {refs}')
    # key anchor numbers stated in S5
    for line in s5.splitlines():
        if any(k in line for k in ['−0.09', '0.24', '0.31', 'K-lift', '锚']):
            print('   ', line.strip()[:200])
    print(f'--- W{w} S7 placeholder region:')
    print(repr(t[m7.start():m8.start()])[:400])
    d = json.load(open(f'results/perpetual_faces/n1_w{w}_results.json', encoding='utf-8'))
    np_ = d['null_pool_cumulative']; A = d['families']['A_random_engine_exit']
    wonly = {k: np_[k] for k in np_ if k.startswith(f'w{w}_only')}
    mk = np_['merged']['n_values']
    print('   w_only:', wonly)
    print('   merged n/mu/sigma:', mk, np_['merged']['mu'], np_['merged']['sigma'], 'se:', np_.get(f'se_mu_at_k{mk}'))
    print('   A_p95:', A['full_sharpe_p95'], ' skl:', json.dumps(d.get('skill_line_v2_k_lift', {}), ensure_ascii=False))
    print('   ledger:', d['science_gates']['ledger']['prev_total'], '->', d['science_gates']['ledger']['total'])
    print()
