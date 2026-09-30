import json, sys
h = json.load(open('results/_r465bma_w13_harvest.json', encoding='utf-8'))
want = sys.argv[1:]
for r in h['rows']:
    if r['what'] in want:
        print('=' * 25, r['what'], r['kind'], 'n=', r.get('n_expected'))
        print(repr(r['new_text']))
        print()
