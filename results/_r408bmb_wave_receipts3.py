import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for w in ['w2', 'w3', 'w4', 'w5']:
    p = r'results\trial_labor_%s\%s_judge.json' % (w, w)
    j = json.load(open(p, encoding='utf-8'))
    print('=====', w.upper(), '=====')
    for k in ['gate_face_judgment', 'vol_face_judgment', 'yang_face_judgment', 'gate_vol_interaction_judgment', 'gate_vol_yang_interaction_judgment']:
        v = j.get(k)
        if v is None: continue
        if isinstance(v, dict):
            print(' ', k, '->', json.dumps({kk: vv for kk, vv in v.items() if not isinstance(vv, (list, dict))}, ensure_ascii=False)[:300])
        else:
            print(' ', k, '=', str(v)[:300])
    # G1'/G2 per-cell pass counts
    cells = j.get('cells', [])
    ng1 = sum(1 for c in cells if c.get('g1_pass') or c.get('g1_prime_v2_pass'))
    ng2 = sum(1 for c in cells if c.get('g2_eligible') or c.get('eligible'))
    print('  cells n=%d  g1_pass=%d  g2_eligible=%d' % (len(cells), ng1, ng2))
    if cells:
        ckeys = list(cells[0].keys())
        # find best sharpe / dsr
        def best(key):
            vals = [(c.get(key), c.get('candidate_id', c.get('cell_id', '?'))) for c in cells if isinstance(c.get(key), (int, float))]
            if vals: return max(vals)
            return None
        for key in ['sharpe_full', 'sharpe', 'dsr', 'g1_metric', 'skill_gap']:
            b = best(key)
            if b: print('  best', key, '=', b)
        # any g1 passers detail
        for c in cells:
            if c.get('g1_pass') or c.get('g1_prime_v2_pass'):
                print('  G1-PASSER:', json.dumps({kk: c[kk] for kk in ckeys if not isinstance(c[kk], (list, dict))}, ensure_ascii=False)[:400])
    print('  top-level g1/g2 faces:', [k for k in j.keys() if 'g1' in k.lower() or 'g2' in k.lower()])
    for k in j.keys():
        if ('g1' in k.lower() or 'g2' in k.lower() or 'skill' in k.lower() or 'e_fp' in k.lower()) and not isinstance(j[k], (list, dict)):
            print('   ', k, '=', j[k])
        elif ('g1' in k.lower() or 'g2' in k.lower() or 'skill' in k.lower() or 'e_fp' in k.lower()) and isinstance(j[k], dict):
            print('   ', k, '=', json.dumps(j[k], ensure_ascii=False)[:300])
print('done')
