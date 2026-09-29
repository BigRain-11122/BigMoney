import json
for f in ['VOLREGIME-TIMING-P1', 'ICU-MA-TIMING-P1', 'HIGHERMOM-TIMING-P1']:
    d = json.load(open('results/innovation_quota/%s.json' % f, encoding='utf-8'))
    print('==', f, '| gates:', str(d.get('gates'))[:260])
    print('  judgment_note:', str(d.get('judgment_note'))[:300])
    for name, c in d['cells'].items():
        print('  %s: sharpe=%s ann=%s dd=%s n_days=%s' % (name, c.get('sharpe_full'), c.get('ann_ret'), c.get('max_dd'), c.get('n_days')))
