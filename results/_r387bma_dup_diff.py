import json
a = json.load(open('results/trial_labor_w2/w2_candidates.json', encoding='utf-8'))
b = json.load(open('results/trial_labor_w2/w2_candidates.json.live-bma-dup', encoding='utf-8'))
def summ(d, tag):
    print(tag, 'top keys:', sorted(d.keys())[:8])
    for k, v in d.items():
        if isinstance(v, list):
            print('  ', k, 'len=', len(v))
        elif isinstance(v, dict):
            print('  ', k, 'dict keys=', len(v))
        else:
            print('  ', k, '=', str(v)[:80])
summ(a, 'CANONICAL')
summ(b, 'DUP')
ca = a.get('candidates', a)
cb = b.get('candidates', b)
if isinstance(ca, list) and isinstance(cb, list):
    ia = {c.get('cell_id') or c.get('id') or json.dumps(c, sort_keys=True)[:60] for c in ca}
    ib = {c.get('cell_id') or c.get('id') or json.dumps(c, sort_keys=True)[:60] for c in cb}
    print('canon ids:', len(ia), 'dup ids:', len(ib), 'common:', len(ia & ib))
    print('canon-only:', len(ia - ib), 'dup-only:', len(ib - ia))
    print('canon-only sample:', sorted(ia - ib)[:5])
    print('dup-only sample:', sorted(ib - ia)[:5])
