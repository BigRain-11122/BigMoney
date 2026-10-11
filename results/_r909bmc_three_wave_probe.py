# -*- coding: utf-8 -*-
"""r909 bm-c: machine-read W209/W211/W213 finalize results (debt-heal + backfill shared probe)."""
import json

for w in ['209', '211', '213']:
    d = json.load(open(rf'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\perpetual_faces\n1_w{w}_results.json'))
    sg = d['science_gates']['ledger']
    npc = d['null_pool_cumulative']
    m = npc['merged']
    only_key = [k for k in npc if k.endswith('_only')][0]
    wo = npc[only_key]
    kl = d['skill_line_v2_k_lift']
    pre_key = [p for p in kl if p.startswith('line_pre')][0]
    mrg_key = [p for p in kl if p.startswith('line_merged')][0]
    delta_key = [p for p in npc if 'mu_delta' in p]
    semu_key = [p for p in npc if p.startswith('se_mu')]
    famA = d['families']['A_random_engine_exit']
    print(f'--- W{w} ---')
    print('ledger:', sg['prev_total'], '+', sg['batch_trials'], '=', sg['total'])
    ident = sg['prev_total'] + sg['batch_trials'] == sg['total']
    print('ledger identity assert:', ident)
    print('merged mu:', m['mu'], 'sigma:', m['sigma'])
    print('w-only mu:', wo['mu'], 'sigma:', wo['sigma'])
    for k in delta_key:
        print('mu_delta field:', k, '=', npc[k])
    for k in semu_key:
        print('se_mu:', k, '=', npc[k])
    print('k_lift:', kl[pre_key], '->', kl[mrg_key], 'delta', kl.get('line_delta_k_lift'), 'n_eff', kl.get('n_eff_held_equal'))
    print('canon_flip:', kl.get('canon_flip'))
    print('A p95:', famA.get('full_sharpe_p95'), 'n:', famA.get('n'))
    print('shards:', len(d.get('shards_consumed', [])), 'cutoff:', d.get('evidence_cutoff'))
    print('voids:', sg.get('voids_applied'))
    print('audit:', d.get('audit'))
