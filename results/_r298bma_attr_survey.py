import json
d = json.load(open('results/gate_attrition.json', encoding='utf-8'))
for e in d['entries']:
    n_g1 = len(e.get('gates', {}).get('g1_pass', {}))
    print(e['batch'], '| ts', e.get('ts'), '| delta', e.get('cells_ledger_delta'), '| total', e.get('ledger_total_after'), '| n_g1_keys', n_g1, '| kind', e.get('kind'), '| top keys', list(e.keys()))
