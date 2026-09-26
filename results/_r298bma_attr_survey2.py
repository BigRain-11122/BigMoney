import json
d = json.load(open('results/gate_attrition.json', encoding='utf-8'))
rows = d['entries']
for e in rows[-8:]:
    g = e.get('gates') or {}
    n_g1 = len(g.get('g1_pass') or {})
    print(e['batch'], '| ts', e.get('ts'), '| delta', e.get('cells_ledger_delta'), '| total', e.get('ledger_total_after'), '| n_g1_keys', n_g1, '| kind', e.get('kind'), '| top keys', list(e.keys()))
print()
# show compact structure of the FUSION-P1-NAV row (s1 harvest of this very ticket)
for e in rows:
    if e['batch'] == 'FUSION_P1_NAV':
        print('FUSION_P1_NAV row:')
        print(json.dumps(e, ensure_ascii=False, indent=1)[:3000])
