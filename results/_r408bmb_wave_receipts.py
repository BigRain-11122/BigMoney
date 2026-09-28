import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

for w in ['w2', 'w3', 'w4', 'w5']:
    p = r'results\trial_labor_%s\%s_judge.json' % (w, w)
    j = json.load(open(p, encoding='utf-8'))
    print('=====', w.upper(), '=====')
    print(' n_judged_cells:', j.get('n_judged_cells'))
    print(' n_eligible_g2:', j.get('n_eligible_g2'))
    tl = j.get('trials_ledger')
    print(' trials_ledger:', json.dumps(tl, ensure_ascii=False)[:220] if tl else None)
    fp = j.get('family_pbo')
    if fp:
        if isinstance(fp, dict):
            print(' family_pbo keys:', list(fp.keys())[:8])
            for k in ['n_families', 'worst_family', 'max_pbo', 'n_modules', 'worst']:
                if k in fp: print('  ', k, '=', fp[k])
    ds = j.get('descriptive_summary')
    if isinstance(ds, dict):
        for k in ['e_fp', 'E_FP', 'expected_false_positives', 'skill_line', 'g1_pass', 'n_g1_pass', 'best_sharpe', 'max_dsr', 'best_dsr', 'n_trials', 'ledger_after', 'ledger_head']:
            if k in ds: print(' ds.'+k, '=', ds[k])
    # screen receipts
    try:
        s = json.load(open(r'results\trial_labor_%s\%s_screen.json' % (w, w), encoding='utf-8'))
        for k in ['n_cells', 'n_survivors', 'survival_rate', 'null_p95', 'p95', 'n_candidates']:
            if k in s: print(' screen.'+k, '=', s[k])
        if isinstance(s.get('summary'), dict):
            for k in ['n_cells', 'n_survivors', 'null_p95']:
                if k in s['summary']: print(' screen.summary.'+k, '=', s['summary'][k])
    except FileNotFoundError:
        print(' screen file missing')
    # candidates
    try:
        c = json.load(open(r'results\trial_labor_%s\%s_candidates.json' % (w, w), encoding='utf-8'))
        if isinstance(c, list): print(' candidates_n:', len(c))
        elif isinstance(c, dict): print(' candidates_n:', len(c.get('candidates', c.get('cells', []))))
    except FileNotFoundError:
        print(' candidates file missing')
print('done')
